import json
import os
import re
import requests
from typing import Callable, Dict, Any, List, Tuple
from typing import Dict, Any, Optional

from information_extraction.globals import CORPUS, DATE_PATTERN, LLM_ENDPOINT, MODEL
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
        
        return "hasta" # Default to "hasta"

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

def get_json_from_prompt(prompt, model=MODEL):
    response = requests.post(
        LLM_ENDPOINT,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "0m",
            "options": {
                "temperature": 0
            }
        }
    )

    output = response.json()["response"]

    try:
        return json.loads(output)
    except:
        print("Invalid JSON:", output)
        return None

"""
LLM-based approach for extracting deductions from a specific text. 
"""
def extract_deducciones(text):
    prompt = f"""
    You are an information extraction system.

    Extract the deductions from the Spanish text below and return ONLY valid JSON.
    Do not explain anything.
    Do not include markdown.
    Follow exactly this JSON schema for each of the deductions:

    {{
        "cantidad": 0,
        "tipo": "",
        "descripcion": ""
    }}

    If multiple deductions exist, return multiple objects.
    If none exist, return an empty list [].
    "tipo" can ONLY be "porcentaje" or "euros".
    "descripcion" should not include any amount, and only refer to the amount extracted in "cantidad".

    Text:
    {text}

    Output:
    """

    return get_json_from_prompt(prompt)

# Capítulo VII Articulo 55 
def extract_compatibilidad(text):
    pass # TODO

# Capítulo VI Articulo 40 
def extract_obligaciones(text):
    pass # TODO

# Capítulo III Articulo 15 
def extract_requisitos(text):
    pass # TODO

# Capítulo II Articulos 4 - 11 (concat texts?)
    # Artículo 4 - Clases (introducción)
    # Artículo 5 - Beca matrícula
    # Artículo 6 - Cuantía fija
    # Artículo 7 - Cuantía residencia
    # Artículo 8 - Cuantía excelencia
    # Artículo 9 - Beca básica
    # Artículo 10 - Cuantía variable
    # Artículo 11 - Cantidades de las cuantías
def extract_cuantías(text):
    pass # TODO

# Capítulo V Articulo 22 - 24 
def extract_requisitos_grado_universidad(text):
    pass # TODO

# Capítulo V Articulo 28 - 30 
def extract_requisitos_master(text):
    pass # TODO

# Capítulo V Articulo 33
def extract_requisitos_grado_superior(text):
    pass # TODO

# Capítulo V Articulo 34
def extract_requisitos_bachiller(text):
    pass # TODO

# Capítulo V Articulo 36
def extract_requisitos_ciclo_medio(text):
    pass # TODO

def main():
    for filename in CORPUS:
        pdf = preprocess_pdf(filename)

        info = extraction_pipeline(
            ("umbrales renta", pdf["IV"]["articles"]["19"]["content"], extract_umbrales),
            ("deducciones renta", pdf["IV"]["articles"]["18"]["content"], extract_deducciones),
            ("plazos solicitud", pdf["VII"]["articles"]["48"]["content"], extract_plazos),
        )

        os.makedirs('information_extraction/results', exist_ok=True)
        with open(f'information_extraction/results/{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
            
main()
