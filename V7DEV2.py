import os
from bs4 import BeautifulSoup

# Dossier contenant les fichiers HTML
folder_path = "C:/WORK/V7DEV"  # Remplace par le chemin correct
output_file_path = "C:/WORK/V7DEV.txt"

# Fonction pour convertir un tableau HTML en texte simplifié
def convert_table_to_text(table_tag):
    rows = []
    for tr in table_tag.find_all('tr'):
        cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
        if cells:
            rows.append('\t'.join(cells))
    return '\n'.join(rows)

# Fonction pour extraire le contenu principal
def extract_main_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Trouver le <div role="main" id="mc-main-content">
    main_content = soup.find('div', {'role': 'main', 'id': 'mc-main-content'})
    
    if main_content:
        # Traiter la section "See also" avant de remplacer les <a>
        see_also_header = main_content.find('h1', id='Seealso')
        if see_also_header:
            see_also_content = see_also_header.find_next_sibling('p')
            if see_also_content:
                link_texts = [a.get_text() for a in see_also_content.find_all('a')]
                see_also_text = ', '.join(link_texts) + '.'
                see_also_content.string = see_also_text
        
        # Remplacer les liens <a> par leur texte
        for a_tag in main_content.find_all('a'):
            a_tag.replace_with(a_tag.get_text())
        
        # Remplacer les balises <code> par leur texte pour éviter les sauts de ligne
        for code_tag in main_content.find_all('code'):
            code_tag.replace_with(code_tag.get_text())
        
        # Encadrer les balises <pre> (qui contiennent des exemples de code)
        for pre_tag in main_content.find_all('pre'):
            code_text = pre_tag.get_text()
            pre_tag.replace_with(f"\n### START EXAMPLES\n{code_text}\n### END EXAMPLES\n")
        
        # Convertir les tableaux en texte simplifié
        for table_tag in main_content.find_all('table'):
            table_text = convert_table_to_text(table_tag)
            table_tag.replace_with(table_text)
        
        # Fonction pour extraire le texte avec des sauts de ligne avant les balises h et ul, après les ul
        def extract_text_with_line_breaks(element):
            texts = []
            for child in element.children:
                if isinstance(child, str):
                    text = child.strip()
                    if text:
                        texts.append(text)
                else:
                    if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        # Ajouter un saut de ligne avant les titres
                        child_text = child.get_text(strip=True)
                        if child_text:
                            texts.append(f"\n{child_text}\n")
                    elif child.name == 'ul':
                        # Ajouter des sauts de ligne avant et après les balises <ul>
                        child_text = child.get_text(strip=True)
                        if child_text:
                            texts.append(f"\n{child_text}\n")
                    elif child.name == 'br':
                        texts.append('\n')
                    else:
                        # Traiter récursivement les autres éléments
                        child_text = extract_text_with_line_breaks(child)
                        if child_text:
                            texts.append(child_text)
            final_text = ''
            for i, text in enumerate(texts):
                if text == '\n':
                    final_text = final_text.rstrip() + '\n'
                else:
                    if final_text and not final_text.endswith('\n'):
                        final_text += ' '
                    final_text += text
            return final_text.strip()
        
        # Extraire le texte du contenu principal
        final_text = extract_text_with_line_breaks(main_content)
        return final_text
    
    return None

# Boucle à travers tous les fichiers HTML du dossier
all_relevant_texts = []

for filename in os.listdir(folder_path):
    if filename.endswith(".html"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
            main_content_text = extract_main_content(html_content)
            if main_content_text:
                all_relevant_texts.append(f"===== {filename} =====\n{main_content_text}")

# Combiner les textes dans un seul fichier
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write("\n\n".join(all_relevant_texts))

print(f"Extraction terminée, résultats enregistrés dans {output_file_path}")
