V7DEV2.py : Permet de parcourir tous les fichiers HTML d'un répertoire pour en extraire un fichier global contenant tout le texte récupéré, sans le code HTML inutile. Hyper optimisé pour l'aide en ligne Sage X3. Tente de repérer le code et de l'encapsuler dans f"\n### START EXAMPLES\n{code_text}\n### END EXAMPLES\n".

GenerateGenericTrainingJSON_V2_2.py : Récupère le fichier précédent et génère un fichier de couples questions/réponses en utilisant l'API OpenAI.

jsonl-to-autotrain-converter.py : Récupère le fichier de couples questions/réponses et le convertit au format AutoTrain/HuggingFace.

jsonl-to-mistral-converter.py : Récupère le fichier de couples questions/réponses et le convertit au format Mistral.

Note : Il manque la génération du JSON générique à partir de codes divers, à corriger avant la sortie de la version finale.
