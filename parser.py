import os
import json
import xml.etree.ElementTree as ET
import re

INPUT_FOLDER = "./xml_files"     # Folder with your .xml papers
OUTPUT_FOLDER = "./json_output"  # Folder where JSONs will be saved
MIN_WORD_COUNT = 50  # Minimum word count to keep a paper

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

NAMESPACES = {
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dcterms': 'http://purl.org/dc/terms/',
    'prism': 'http://prismstandard.org/namespaces/basic/2.0/',
    'ce': 'http://www.elsevier.com/xml/common/dtd',
    'sb': 'http://www.elsevier.com/xml/common/struct-bib/dtd',
    'sa': 'http://www.elsevier.com/xml/common/struct-aff/dtd',
}


def get_text_from_element(element):
    """Extract all text from an element and its children, ignoring tags."""
    if element is None:
        return ""
    text_parts = []
    if element.text:
        text_parts.append(element.text.strip())
    for child in element:
        if child.text:
            text_parts.append(child.text.strip())
        if child.tail:
            text_parts.append(child.tail.strip())
    return " ".join(text_parts)


def count_words(text):
    """Count words in text."""
    if not text or text == "No body text" or text == "No abstract":
        return 0
    return len(re.findall(r'\b\w+\b', text))


def parse_xml_to_json(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        title_elem = root.find(".//{http://purl.org/dc/elements/1.1/}title")
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Unknown Title"

        abstract_elem = root.find(".//{http://purl.org/dc/elements/1.1/}description")
        abstract = abstract_elem.text.strip() if abstract_elem is not None and abstract_elem.text else "No abstract"

        body_paras = root.findall(".//{http://www.elsevier.com/xml/common/dtd}para")
        body_texts = []
        for para in body_paras:
            para_text = get_text_from_element(para)
            if para_text:
                body_texts.append(para_text)
        body = " ".join(body_texts) if body_texts else "No body text"

        total_words = count_words(body) + count_words(abstract)
        if total_words < MIN_WORD_COUNT:
            print(f"⏭️  Skipping {os.path.basename(xml_path)}: only {total_words} words (minimum: {MIN_WORD_COUNT})")
            return None

        date_elem = root.find(".//{http://prismstandard.org/namespaces/basic/2.0/}coverDate")
        publication_date = date_elem.text.strip() if date_elem is not None and date_elem.text else "Unknown"

        institution = "Unknown Institution"
        aff_elem = root.find(".//{http://www.elsevier.com/xml/common/struct-aff/dtd}affiliation")
        if aff_elem is not None:
            org_elem = aff_elem.find(".//{http://www.elsevier.com/xml/common/struct-aff/dtd}organization")
            if org_elem is not None and org_elem.text:
                institution = org_elem.text.strip()
        else:
            aff_alt = root.find(".//{http://www.elsevier.com/xml/common/dtd}affiliation")
            if aff_alt is not None:
                inst_text = get_text_from_element(aff_alt)
                if inst_text:
                    institution = inst_text

        authors = []
        creator_elems = root.findall(".//{http://purl.org/dc/elements/1.1/}creator")
        for creator in creator_elems:
            if creator.text:
                authors.append(creator.text.strip())

        references = []
        ref_elems = root.findall(".//{http://www.elsevier.com/xml/common/dtd}source-text")
        for ref_elem in ref_elems:
            if ref_elem.text:
                ref_text = ref_elem.text.strip()
                if ref_text:
                    references.append(ref_text)

        citations = []
        cross_refs = root.findall(".//{http://www.elsevier.com/xml/common/dtd}cross-ref")
        for cross_ref in cross_refs:
            if cross_ref.text:
                citations.append(cross_ref.text.strip())

        keywords = []
        keyword_elems = root.findall(".//{http://purl.org/dc/terms/}subject")
        for kw_elem in keyword_elems:
            if kw_elem.text:
                keywords.append(kw_elem.text.strip())

        datasets = []
        doi_elems = root.findall(".//{http://www.elsevier.com/xml/common/dtd}doi")
        for doi_elem in doi_elems:
            if doi_elem.text:
                datasets.append(doi_elem.text.strip())

        json_data = {
            "title": title,
            "abstract": abstract,
            "body": body,
            "citations": citations,
            "references": references,
            "datasets": datasets,
            "authors": authors,
            "publication date": publication_date,
            "keywords": keywords,
            "institution": institution
        }

        return json_data
    except Exception as e:
        print(f"error parsing {xml_path}: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    if not os.path.exists(INPUT_FOLDER):
        print(f"input folder '{INPUT_FOLDER}' not found (create it and add your XML files)")
        return

    xml_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".xml")]
    
    if not xml_files:
        print(f"no XML files found in '{INPUT_FOLDER}'")
        return

    # if os.path.exists(OUTPUT_FOLDER):
    #     for old_file in os.listdir(OUTPUT_FOLDER):
    #         if old_file.endswith(".json"):
    #             os.remove(os.path.join(OUTPUT_FOLDER, old_file))
    #     print(f"cleared old output files\n")

    print(f"found {len(xml_files)} XML file(s) to process...\n")
    print(f"minimum word count: {MIN_WORD_COUNT} words\n")

    processed_count = 0
    skipped_count = 0

    for filename in xml_files:
        xml_path = os.path.join(INPUT_FOLDER, filename)
        json_data = parse_xml_to_json(xml_path)
        
        if json_data:
            json_path = os.path.join(OUTPUT_FOLDER, filename.replace(".xml", ".json"))
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)
            print(f"saved to: {json_path}")
            processed_count += 1
        else:
            skipped_count += 1

    print(f"\n processing complete")
    print(f"processed: {processed_count} files")
    print(f"skipped: {skipped_count} (below {MIN_WORD_COUNT} words)")
    print(f"output folder: '{OUTPUT_FOLDER}'")


if __name__ == "__main__":
    main()


