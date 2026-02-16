import fitz
import json
import os
import re

from information_extraction.globals import CLEAN_PATTERNS, STRUCTURE_PATTERNS

def pdf_to_txt(pdf_path):
    pages = []
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            pages.append(page.get_text())
    
    return ' '.join(pages)

def clean_text(text):
    for pattern in CLEAN_PATTERNS:
        text = pattern.sub('', text)
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

filename = 'ayudas_25-26'

text = pdf_to_txt(f'corpus/{filename}.pdf')
clean = clean_text(text)

os.makedirs('json', exist_ok=True)
with open(f'json/{filename}.json', 'w', encoding='utf-8') as f:
    json.dump(parse_hierarchy(clean), f, ensure_ascii=False, indent=2)



