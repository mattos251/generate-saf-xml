import os
import shutil
import xml.etree.ElementTree as ET

# Diretórios
entrada = "xml"
saida = "saf"

os.makedirs(saida, exist_ok=True)


def extrair_valores(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Namespace do XOAI
    ns = {"xoai": "http://www.lyncode.com/xoai"}

    metadados = []

    # ----------- Título -----------
    for title in root.findall(".//xoai:element[@name='title']//xoai:field[@name='value']", ns):
        metadados.append(('title', 'none', 'pt_BR', title.text.strip()))

    # ----------- Autor -----------
    for creator in root.findall(".//xoai:element[@name='creator']//xoai:field[@name='value']", ns):
        metadados.append(('creator', 'none', None, creator.text.strip()))

    # ----------- Datas -----------
    for issued in root.findall(".//xoai:element[@name='date']/xoai:element[@name='issued']//xoai:field[@name='value']", ns):
        metadados.append(('date', 'issued', None, issued.text.strip()))
    for accessioned in root.findall(".//xoai:element[@name='date']/xoai:element[@name='accessioned']//xoai:field[@name='value']", ns):
        metadados.append(('date', 'accessioned', None, accessioned.text.strip()))
    for available in root.findall(".//xoai:element[@name='date']/xoai:element[@name='available']//xoai:field[@name='value']", ns):
        metadados.append(('date', 'available', None, available.text.strip()))

    # ----------- Resumos (PT/EN) -----------
    for abstract in root.findall(".//xoai:element[@name='description']/xoai:element[@name='abstract']//xoai:field[@name='value']", ns):
        metadados.append(('description', 'abstract', 'en', abstract.text.strip()))
    for resumo in root.findall(".//xoai:element[@name='description']/xoai:element[@name='resumo']//xoai:field[@name='value']", ns):
        metadados.append(('description', 'abstract', 'pt_BR', resumo.text.strip()))

    # ----------- Idioma -----------
    for lang in root.findall(".//xoai:element[@name='language']//xoai:field[@name='value']", ns):
        metadados.append(('language', 'iso', None, lang.text.strip()))

    # ----------- Publisher + Local + Departamento -----------
    for pub in root.findall(".//xoai:element[@name='publisher']/xoai:element[@name='pt_BR']/xoai:field[@name='value']", ns):
        metadados.append(('publisher', 'none', 'pt_BR', pub.text.strip()))
    for local in root.findall(".//xoai:element[@name='publisher']/xoai:element[@name='local']//xoai:field[@name='value']", ns):
        metadados.append(('publisher', 'place', 'pt_BR', local.text.strip()))
    for dept in root.findall(".//xoai:element[@name='publisher']/xoai:element[@name='department']//xoai:field[@name='value']", ns):
        metadados.append(('contributor', 'department', 'pt_BR', dept.text.strip()))

    # ----------- Assuntos (subjects) -----------
    for subject in root.findall(".//xoai:element[@name='subject']//xoai:field[@name='value']", ns):
        val = subject.text.strip()
        if val not in [m[3] for m in metadados]:  # evita duplicatas
            metadados.append(('subject', 'none', 'pt_BR', val))

    # ----------- Tipo -----------
    for tipo in root.findall(".//xoai:element[@name='type']//xoai:field[@name='value']", ns):
        metadados.append(('type', 'none', None, tipo.text.strip()))

    # ----------- Identificadores -----------
    for uri in root.findall(".//xoai:element[@name='identifier']/xoai:element[@name='uri']//xoai:field[@name='value']", ns):
        metadados.append(('identifier', 'uri', None, uri.text.strip()))
    for citation in root.findall(".//xoai:element[@name='identifier']/xoai:element[@name='citation']//xoai:field[@name='value']", ns):
        metadados.append(('identifier', 'citation', 'pt_BR', citation.text.strip()))

    # ----------- Contribuidores (orientador e banca) -----------
    for advisor in root.findall(".//xoai:element[@name='contributor']/xoai:element[@name='advisor1']//xoai:field[@name='value']", ns):
        metadados.append(('contributor', 'advisor', None, advisor.text.strip()))

    for referee in root.findall(".//xoai:element[@name='contributor']/xoai:element", ns):
        nome_attr = referee.attrib.get("name", "")
        if nome_attr.startswith("referee"):
            for field in referee.findall(".//xoai:field[@name='value']", ns):
                metadados.append(('contributor', 'referee', None, field.text.strip()))

    return metadados


# ---------------- Loop principal ----------------
for nome in os.listdir(entrada):
    if not nome.endswith(".xml"):
        continue

    item_id = nome[:-4]  # remove .xml
    pasta_item = os.path.join(saida, item_id)
    os.makedirs(pasta_item, exist_ok=True)

    caminho_xml = os.path.join(entrada, nome)

    # Extrair dados e gerar dublin_core.xml
    metadados = extrair_valores(caminho_xml)

    with open(os.path.join(pasta_item, "dublin_core.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<dublin_core>\n')
        for elem, qual, lang, valor in metadados:
            lang_attr = f' language="{lang}"' if lang else ""
            qual_attr = f' qualifier="{qual}"' if qual else ' qualifier="none"'
            f.write(f'  <dcvalue element="{elem}"{qual_attr}{lang_attr}>{valor}</dcvalue>\n')
        f.write('</dublin_core>\n')

    # Criar contents (se houver PDF com o mesmo nome)
    contents_path = os.path.join(pasta_item, "contents")
    with open(contents_path, "w", encoding="utf-8") as contents:
        pdf_path = os.path.join(entrada, f"{item_id}.pdf")
        if os.path.exists(pdf_path):
            shutil.copy(pdf_path, os.path.join(pasta_item, f"{item_id}.pdf"))
            contents.write(f"{item_id}.pdf\tbundle:ORIGINAL\n")
        else:
            contents.write("")

    print(f"[✔] SAF gerado: {pasta_item}")
