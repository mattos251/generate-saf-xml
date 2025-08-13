import xml.etree.ElementTree as ET

input_forms_file = "reference-files/input-forms_pt_BR.xml"
output_file = "normalize-dspace9/lista-campos-convertido.xml"


# Função para limpar texto sem remover tags HTML codificadas
def clean_text(text):
    return (text or "").strip()


# Ler o XML de entrada
tree = ET.parse(input_forms_file)
root = tree.getroot()

# Usar lista para manter a ordem e evitar perda de campos distintos
campos = []

for field in root.findall(".//field"):
    dc_type = {
        "schema": clean_text(field.findtext("dc-schema")),
        "element": clean_text(field.findtext("dc-element")),
        "qualifier": clean_text(field.findtext("dc-qualifier")),
        "label": clean_text(field.findtext("label")),
        "repeatable": clean_text(field.findtext("repeatable")),
        "type_bind": clean_text(field.findtext("type-bind")),
        "input_type": clean_text(field.findtext("input-type")),
        "hint": clean_text(field.findtext("hint")),
        "required": clean_text(field.findtext("required"))
    }
    campos.append(dc_type)

# Criar XML de saída
dspace_types = ET.Element("dspace-dc-types")

for campo in campos:
    if not campo["schema"] or not campo["element"]:
        continue

    dc_type_el = ET.SubElement(dspace_types, "dc-type")

    ET.SubElement(dc_type_el, "schema").text = campo["schema"]
    ET.SubElement(dc_type_el, "element").text = campo["element"]
    ET.SubElement(dc_type_el, "qualifier").text = campo["qualifier"]
    ET.SubElement(dc_type_el, "scope_note").text = campo["label"] or "Campo importado do formulário"

    # Novos campos preservados
    if campo["repeatable"]:
        ET.SubElement(dc_type_el, "repeatable").text = campo["repeatable"]
    if campo["type_bind"]:
        ET.SubElement(dc_type_el, "type_bind").text = campo["type_bind"]
    if campo["input_type"]:
        ET.SubElement(dc_type_el, "input_type").text = campo["input_type"]
    if campo["hint"]:
        ET.SubElement(dc_type_el, "hint").text = campo["hint"]
    if campo["required"]:
        ET.SubElement(dc_type_el, "required").text = campo["required"]

# Salvar XML final
tree_out = ET.ElementTree(dspace_types)
tree_out.write(output_file, encoding="UTF-8", xml_declaration=True)

print(f"Arquivo convertido salvo como: {output_file}")
