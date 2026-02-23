import fitz
import json
import os
import re

from information_extraction.globals import CLEAN_PATTERNS, STRUCTURE_PATTERNS, ROOT

def remove_page_numbers(text):
    lines = text.strip().split("\n")

    if lines and lines[0].strip().isdigit():
        lines = lines[1:]

    if lines and lines[-1].strip().isdigit():
        lines = lines[:-1]

    return "\n".join(lines)

def pdf_to_txt(pdf_path):
    pdf_path = ROOT / pdf_path
    pages = []
    with fitz.open(str(pdf_path)) as pdf:
        for page in pdf:
            text = remove_page_numbers(page.get_text())
            pages.append(text)
    return " ".join(pages)


def clean_text(text):
    for pattern in CLEAN_PATTERNS:
        text = pattern.sub('', text)
    
    text = re.sub(r'\n\s*\n+', '\n', text) # Collapse new lines
    return text

def parse_hierarchy(text):
    json = {}

    chapters = list(STRUCTURE_PATTERNS['chapter'].finditer(text))
    for i, cmatch in enumerate(chapters):
        cnumber = cmatch.group(1)
        ctitle = cmatch.group(2).strip()
        
        start = cmatch.end()
        end = chapters[i+1].start() if i+1 < len(chapters) else len(text)
        ccontent = text[start:end].strip()

        articles = {}
        for amatch in STRUCTURE_PATTERNS['article'].finditer(ccontent):
            anumber = amatch.group(1)
            acontent = amatch.group(2).strip()

            title_body = acontent.split('\n', 1)
            atitle = title_body[0].strip()
            abody = title_body[1].strip() if len(title_body) > 1 else ''

            articles[anumber] = {
                "title": atitle,
                "content": abody
            }
        
        json[cnumber] = {
            "title": ctitle,
            "articles": articles
        }
    
    return json

def preprocess_pdf(filename, save=True):
    text = pdf_to_txt(f'corpus/{filename}.pdf')
    clean = clean_text(text)
    final = parse_hierarchy(clean)

    output_dir = ROOT / "corpus_json"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{filename}.json"

    if save:
        os.makedirs('json', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final, f, ensure_ascii=False, indent=2)
    
    return final

if __name__ == "__main__":
    preprocess_pdf("ayudas_24-25")

