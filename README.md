# X3GPT_V6

V7DEV2.py : Permet de parler tous les fichier HTML d'un répertoire pour en sortir un fichier global de tout le texte récupéré, dans le code HTML inutile.
Hyper optimisé pour laide en ligne Sage X3
Tente de repérer le code et de l'encapsuler dans f"\n### START EXAMPLES\n{code_text}\n### END EXAMPLES\n"

GenerateGenericTrainingJSON_V2_2.py : Récupére le fichier précédent et génére un fichier de couples de questions / réponses en utilisant l'API Open AI

jsonl-to-autotrain-converter.py : Récupére le fichier de couples de questions / réponses pour le convertir au format Autotrain / huggingface

jsonl-to-mistral-converter.py : Récupére le fichier de couples de questions / réponses pour le convertir au format Mistral

Note : Il manque la génération du JSON générique depuis des codes divers, à corriger avant release.
