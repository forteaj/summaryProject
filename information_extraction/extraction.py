import json
import os
import re
from typing import Callable, Dict, Any, List, Tuple
from typing import Dict, Any, Optional

from information_extraction.globals import CORPUS, DATE_PATTERN
from information_extraction.preprocessing import preprocess_pdf
from information_extraction.util import iso

"""
Function to extract different information from text.
Parameters:
    tasks - Any number of tuples (key, text, function):
        key - The key that will be applied for the value / result of the function in the generated JSON dictionary.
        text - The text to extract information from. Usually a specific article of the PDF to process, as the structure is mostly similar across samples.
        function - The extraction function to apply to the text. Should return a string or a dictionary.
"""
def extraction_pipeline(*tasks: Tuple[str, str, Callable[[str], Any]]) -> Dict[str, Any]:
    info = {}

    for key, text, function in tasks:
        text = re.sub('\n', '', text)
        info[key] = function(text)

    return info

"""
Template-based approach for extracting salary thresholds (umbrales) from a specific text. 
"""
def extract_umbrales(text):
    result = {
        "umbral 1": {},
        "umbral 2": {},
        "umbral 3": {}
    }

    umbrales = re.findall(r'\b\d{1,3}(?:\.\d{3})+\b', text)
    umbrales = [int(u.replace('.', '')) for u in umbrales]

    if len(umbrales) != 27:
        return "unknown"

    style = "bullet" if "•" in text else "table"

    if style == "bullet":
        for u in range(3):
            start = u * 9
            for i in range(8):
                result["umbral " + str(u+1)][str(i+1)] = umbrales[start + i]
            result["umbral " + str(u+1)]["incremento miembros adicionales al 8"] = umbrales[start + 8]

    elif style == "table":
        for i in range(8):
            result["umbral 1"][str(i+1)] = umbrales[i*3]
            result["umbral 2"][str(i+1)] = umbrales[i*3 + 1]
            result["umbral 3"][str(i+1)] = umbrales[i*3 + 2]
        result["umbral 1"]["incremento miembros adicionales al 8"] = umbrales[24]
        result["umbral 2"]["incremento miembros adicionales al 8"] = umbrales[25]
        result["umbral 3"]["incremento miembros adicionales al 8"] = umbrales[26]

    return result

def extract_compatibility(text):
    pass

def extract_deducciones(text):
    pass

"""
Template-based approach for extracting submission dates from a specific article. 
"""
def extract_plazos(text):
    def get_key(sentence):
        prefix = sentence.lower()[:match.start()]

        if "hasta" in prefix:
            return "hasta"
        if "desde" in prefix:
            return "desde"
        
        return "hasta" # We default to "hasta"

    result = {
        "universitario": {"desde": None, "hasta": None},
        "no universitario": {"desde": None, "hasta": None},
        "excepciones": {"desde": None, "hasta": None}
    }

    sections = re.split(r'\d+\. ', text)[1:]

    # --- Regular dates ---

    sentences = re.split(r'\.', sections[0])
    for sentence in sentences:
        contexts = []
        if re.search(r'\bno universitarios\b', sentence.lower()):
            contexts.append("no universitario")
        if re.search(r'(?<!no )\buniversitarios\b', sentence.lower()):
            contexts.append("universitario")
        
        if contexts:
            for match in DATE_PATTERN.finditer(sentence):
                iso_date = iso(match)
                key = get_key(sentence)
                    
                for context in contexts:
                    result[context][key] = iso_date
    
    # --- Exception dates ---

    for match in DATE_PATTERN.finditer(sections[1]):
        iso_date = iso(match)
        key = get_key(sentence)

        result["excepciones"][key] = iso_date

    return result

def main():
    for filename in CORPUS:
        pdf = preprocess_pdf(filename)

        info = extraction_pipeline(
            ("umbrales renta", pdf["IV"]["articles"]["19"]["content"], extract_umbrales),
            ("plazos solicitud", pdf["VII"]["articles"]["48"]["content"], extract_plazos),
        )

        os.makedirs('information_extraction/results', exist_ok=True)
        with open(f'information_extraction/results/{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
main()
