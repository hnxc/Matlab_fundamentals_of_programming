import os
import zipfile
import shutil
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator

def translate_text(text, source_lang='en', target_lang='vi'):
    try:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def translate_mlx_file(filepath, output_dir):
    filename = os.path.basename(filepath)
    temp_dir = "temp_mlx_extracted"

    # Step 1: Unzip the .mlx file
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Step 2: Find the XML document path
    doc_xml_path = os.path.join(temp_dir, 'matlab', 'document.xml')
    if not os.path.exists(doc_xml_path):
        print(f"document.xml not found in {filepath}")
        return None

    # Step 3: Load XML and fix namespace
    tree = ET.parse(doc_xml_path)
    root = tree.getroot()
    ns = {'w': "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    # Step 4: Translate text nodes in <w:t> tags
    for elem in root.findall(".//w:t", ns):
        if elem.text and elem.text.strip():
            original = elem.text.strip()
            # print(f"Translating: {original}")
            translated = translate_text(original)
            # print(f"Translated: {translated}")
            elem.text = translated
            # print(f"Translated '{original}' to '{translated}'")

    # Step 5: Save the modified document.xml
    tree.write(doc_xml_path, encoding='utf-8', xml_declaration=True)

    # Step 6: Re-zip into .mlx format
    translated_mlx_path = os.path.join(output_dir, filename.replace('.mlx', '_vi.mlx'))
    with zipfile.ZipFile(translated_mlx_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for foldername, _, filenames in os.walk(temp_dir):
            for file in filenames:
                full_path = os.path.join(foldername, file)
                arcname = os.path.relpath(full_path, temp_dir)
                zip_out.write(full_path, arcname)

    # Step 7: Cleanup
    shutil.rmtree(temp_dir)
    return translated_mlx_path

def batch_translate_mlx(directory, output_directory):
    os.makedirs(output_directory, exist_ok=True)
    translated_files = []
    for file in os.listdir(directory):
        if file.endswith('.mlx'):
            full_path = os.path.join(directory, file)
            translated = translate_mlx_file(full_path, output_directory)
            if translated:
                translated_files.append(translated)
    return translated_files

# Example usage:
translated = batch_translate_mlx("mlx_folder", "translated_mlx_folder")
print(translated)
