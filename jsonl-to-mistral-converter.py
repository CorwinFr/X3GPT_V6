import json
import re

def clean_json_string(s):
    # Remplace les sauts de ligne par des espaces dans les chaînes de caractères
    return re.sub(r'(?<!\\)\\n', ' ', s)

def extract_json_objects(text):
    objects = []
    bracket_count = 0
    start_index = -1
    
    for i, char in enumerate(text):
        if char == '{':
            if bracket_count == 0:
                start_index = i
            bracket_count += 1
        elif char == '}':
            bracket_count -= 1
            if bracket_count == 0 and start_index != -1:
                objects.append(text[start_index:i+1])
                start_index = -1
    
    return objects

def convert_jsonl_to_mistral(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        content = infile.read()
        
        # Extraire les objets JSON
        json_objects = extract_json_objects(content)
        
        for json_str in json_objects:
            try:
                # Nettoyer l'entrée
                cleaned_entry = clean_json_string(json_str)
                
                # Charger l'entrée JSON
                json_entry = json.loads(cleaned_entry)
                
                # Vérifier si les clés nécessaires sont présentes
                if 'instruction' not in json_entry or 'output' not in json_entry:
                    continue
                
                # Remplacer les délimiteurs de code dans la sortie
                output = json_entry['output'].replace("### START EXAMPLES", "```").replace("### END EXAMPLES", "```")
                
                # Créer la liste des messages
                messages = [
                    {"role": "user", "content": json_entry['instruction']},
                    {"role": "assistant", "content": output}
                ]
                
                # Créer le nouveau format JSON pour Mistral
                new_entry = {"messages": messages}
                
                # Écrire la nouvelle entrée dans le fichier de sortie
                json.dump(new_entry, outfile, ensure_ascii=False)
                outfile.write('\n')
                
            except json.JSONDecodeError as e:
                print(f"Erreur lors du décodage de l'entrée : {e}")
                print(f"Entrée problématique : {json_str[:100]}...")  # Affiche les 100 premiers caractères de l'entrée problématique

# Utilisation du script
input_file = 'input.jsonl'  # Remplacez par le nom de votre fichier d'entrée
output_file = 'output_mistral.jsonl'  # Remplacez par le nom souhaité pour votre fichier de sortie

convert_jsonl_to_mistral(input_file, output_file)
print(f"Conversion terminée. Le fichier de sortie est : {output_file}")