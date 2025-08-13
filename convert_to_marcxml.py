import xml.etree.ElementTree as ET


def convert_to_marcxml(input_file, output_file):
    # Parse the input XML file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Create the root element for the output MARCXML
    record = ET.Element('record', {
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': 'http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd',
        'xmlns': 'http://www.loc.gov/MARC21/slim'
    })

    # Create and append the leader element
    leader = ET.SubElement(record, 'leader')
    leader.text = '00567cam a2200205uu 4500'

    # Define a mapping from input XML tags to MARC21 tags
    mapping = {
        'id': ('controlfield', '001'),
        'fonte_catalogacao': ('controlfield', '003'),
        'campo_controle': ('controlfield', '008'),
        'isbn': ('datafield', '020', 'a'),
        'identificacao_registro': ('datafield', '035', 'a'),
        'codigo': ('datafield', '082', 'a'),
        'titulo': ('datafield', '245', 'a'),
        'descricao_fisica': ('datafield', '300', 'a'),
        'assunto': ('datafield', '650', 'a'),
        'tipo': ('datafield', '999', 'a')
    }

    # Create lists to separate controlfields and datafields
    controlfields = []
    datafields = []

    for elem in root:
        tag_info = mapping.get(elem.tag)
        if tag_info:
            if tag_info[0] == 'controlfield':
                field = ET.Element('controlfield', {'tag': tag_info[1]})
                field.text = elem.text
                controlfields.append(field)
            elif tag_info[0] == 'datafield':
                field = ET.Element('datafield', {'tag': tag_info[1], 'ind1': ' ', 'ind2': ' '})
                subfield = ET.SubElement(field, 'subfield', {'code': tag_info[2]})
                subfield.text = elem.text
                datafields.append(field)

    # Add controlfields to the record
    for field in controlfields:
        record.append(field)

    # Add publication date from campo_controle to datafields
    campo_controle = root.find('campo_controle')
    if campo_controle is not None:
        pub_date = campo_controle.text[7:11]
        field_260 = ET.Element('datafield', {'tag': '260', 'ind1': ' ', 'ind2': ' '})
        subfield_c = ET.SubElement(field_260, 'subfield', {'code': 'c'})
        subfield_c.text = pub_date
        datafields.append(field_260)

    # Add datafields to the record
    for field in datafields:
        record.append(field)

    # Write the output MARCXML file
    tree = ET.ElementTree(record)
    tree.write(output_file, encoding='UTF-8', xml_declaration=True)


# Example usage
input_file = 'input.xml'
output_file = 'output.xml'
convert_to_marcxml(input_file, output_file)
