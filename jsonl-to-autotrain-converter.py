import json

def convert_jsonl_to_autotrain(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        # Lire tout le contenu du fichier
        content = infile.read().strip()
        
        # Supprimer les crochets au début et à la fin si présents
        if content.startswith('[') and content.endswith(']'):
            content = content[1:-1]
        
        # Diviser le contenu en entrées individuelles
        entries = content.split('},')
        
        for entry in entries:
            # Ajouter l'accolade fermante si elle a été retirée par le split
            if not entry.strip().endswith('}'):
                entry += '}'
            
            try:
                # Charger l'entrée JSON
                json_entry = json.loads(entry.strip())
                
                # Construire le texte de l'entrée
                text = f"### Human: {json_entry['instruction']}\n### Assistant: "
                
                # Remplacer les délimiteurs de code dans la sortie
                output = json_entry['output'].replace("### START EXAMPLES", "```").replace("### END EXAMPLES", "```")
                
                text += output
                
                # Créer le nouveau format JSON
                new_entry = {"text": text}
                
                # Écrire la nouvelle entrée dans le fichier de sortie
                json.dump(new_entry, outfile, ensure_ascii=False)
                outfile.write('\n')
            
            except json.JSONDecodeError as e:
                print(f"Erreur lors du décodage de l'entrée : {e}")
                print(f"Entrée problématique : {entry}")

# Utilisation du script
input_file = 'input.jsonl'  # Remplacez par le nom de votre fichier d'entrée
output_file = 'output_autotrain.jsonl'  # Remplacez par le nom souhaité pour votre fichier de sortie

convert_jsonl_to_autotrain(input_file, output_file)
print(f"Conversion terminée. Le fichier de sortie est : {output_file}")