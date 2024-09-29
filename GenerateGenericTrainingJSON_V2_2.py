import openai
import json
import re
import os
import asyncio
from openai import AsyncOpenAI
import tiktoken
from tqdm import tqdm
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Global variables
MODEL = "gpt-4o-mini"
MAX_TOKENS = 7000
BATCH_SIZE = 5
RESUME_FROM = "how-to_best-practice-when-using-snapshots.html"

# Load OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
client = AsyncOpenAI(api_key=api_key)

console = Console()

def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4")  # Use GPT-4 encoding for gpt-4o-mini
    return len(encoding.encode(text))

# Read the content of the uploaded file with 'utf-8' encoding
input_file_path = "V7DEV.txt"
with open(input_file_path, "r", encoding="utf-8") as file:
    content = file.read()

# Split content into blocks by the header pattern
blocks_with_names = re.split(r'(===== .*? =====\n)', content)

# Combine the block names with their respective content
combined_blocks = []
resume_flag = False
for i in range(1, len(blocks_with_names), 2):
    block_name = blocks_with_names[i].strip('= \n')
    if i + 1 < len(blocks_with_names):
        block_content = blocks_with_names[i + 1].strip()
        if block_name == RESUME_FROM:
            resume_flag = True
        if resume_flag:
            combined_blocks.append((block_name, block_content))

def split_block_into_chunks(block):
    lines = block.splitlines()
    chunks = []
    current_chunk = []

    for line in lines:
        current_chunk.append(line)
        current_text = "\n".join(current_chunk)
        if count_tokens(current_text) > MAX_TOKENS:
            chunks.append("\n".join(current_chunk[:-1]))  # Add the chunk without the last line
            current_chunk = [line]  # Start a new chunk with the last line

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks

async def generate_question_for_block(block, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates questions about Sage X3 4GL based on the provided content. All questions should start with 'In Sage X3 4GL ...'"},
                    {"role": "user", "content": f"Generate a question that starts with 'In Sage X3 4GL ...' for which the following content would be the answer:\n\n{block.strip()}"}
                ],
                temperature=0.7
            )

            question = response.choices[0].message.content.strip()
            if not question.startswith("In Sage X3 4GL"):
                question = "In Sage X3 4GL " + question
            return question

        except openai.RateLimitError as e:
            retries += 1
            wait_time = 2 ** retries  # Exponential backoff
            console.log(f"[red]Rate limit exceeded. Retrying in {wait_time} seconds...[/red]")
            await asyncio.sleep(wait_time)

    return "In Sage X3 4GL, explain the following content:"

def clean_qa_pair(text):
    text = re.sub(r"^Q:\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^A:\s*", "", text, flags=re.IGNORECASE).strip()
    return text

async def generate_qa_pairs(block, max_retries=5):
    chunks = split_block_into_chunks(block)
    qa_pairs_list = []

    for chunk in chunks:
        question = await generate_question_for_block(chunk)
        qa_pairs_list.append({
            "instruction": question,
            "output": chunk.strip()
        })

        retries = 0
        while retries < max_retries:
            try:
                response = await client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that generates questions and answers about Sage X3 4GL based solely on the provided content. All questions should start with 'In Sage X3 4GL ...'"},
                        {"role": "user", "content": f"Generate additional questions and answers based on the following content. All questions should start with 'In Sage X3 4GL ...'. Format each question and answer clearly using 'Q:' for the question and 'A:' for the answer, like this:\n\nQ: In Sage X3 4GL, [Your Question]\nA: [Your Answer]\n\nContent:\n\n{chunk.strip()}"}
                    ],
                    temperature=0.7
                )

                qa_pairs_raw = response.choices[0].message.content.split("\n\n")
                for qa_pair in qa_pairs_raw:
                    if "Q:" in qa_pair and "A:" in qa_pair:
                        parts = re.split(r"A:", qa_pair, maxsplit=1)
                        if len(parts) == 2:
                            question = clean_qa_pair(parts[0].replace("Q:", "").strip())
                            answer = clean_qa_pair(parts[1].strip())
                            if question and answer:
                                qa_pairs_list.append({
                                    "instruction": question,
                                    "output": answer
                                })

                break

            except openai.RateLimitError as e:
                retries += 1
                wait_time = 2 ** retries  # Exponential backoff
                console.log(f"[red]Rate limit exceeded. Retrying in {wait_time} seconds...[/red]")
                await asyncio.sleep(wait_time)

    return qa_pairs_list

async def process_block(block_name, block_content, output_file, progress, task_id):
    if block_name.startswith("4gl") or "Endif" in block_content:
        qa_pairs = await generate_qa_pairs(block_content)
        for qa_pair in qa_pairs:
            qa_pair['block_name'] = block_name
            json.dump(qa_pair, output_file, ensure_ascii=False, indent=2)
            output_file.write(",\n")
        progress.update(task_id, advance=1)

async def process_blocks_in_batches():
    output_file_path = "qa_pairs_with_labels_resumed.json"

    # Check if the file exists and read its content
    existing_data = []
    if os.path.exists(output_file_path):
        with open(output_file_path, "r", encoding="utf-8") as existing_file:
            existing_data = json.load(existing_file)

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write("[\n")
        if existing_data:
            json.dump(existing_data, output_file, ensure_ascii=False, indent=2)
            if len(existing_data) > 0:
                output_file.write(",\n")

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task_id = progress.add_task("[bold green]Processing blocks...[/bold green]", total=len(combined_blocks))

            for block_name, block_content in combined_blocks:
                await process_block(block_name, block_content, output_file, progress, task_id)
                await asyncio.sleep(2)

        # Remove the last comma and close the JSON array
        output_file.seek(output_file.tell() - 2, os.SEEK_SET)
        output_file.write("\n]\n")

    console.log(f"[bold green]Questions and answers with labels have been saved to {output_file_path}[/bold green]")

if __name__ == "__main__":
    asyncio.run(process_blocks_in_batches())