import requests
import json
import os

from summarisation.globals import LLM_ENDPOINT, CORPUS, ROOT, MODEL

def generate_summary(filename):
    json_path = ROOT / 'information_extraction' / 'results' / f'{filename}.json'
    with open(json_path, 'r') as j:
        data = json.load(j)

    prompt = f"""
    Eres un redactor profesional. A partir del siguiente JSON, genera un texto claro y formal en español sobre la solicitud de una beca de estudio.
    El texto debe estar correctamente estructurado con títulos y subtítulos cuando sea conveniente.

    Reglas:
    - No inventes información.
    - Usa solo los datos presentes en el JSON.
    - Utiliza toda la información presente en el JSON.
    - Redacta en párrafos naturales.
    - NO menciones que el input es JSON.
    - NO hagas referencia a los valores null presentes en el JSON
    - Prioriza la redacción sobre el uso de tablas y listas

    JSON:
    {json.dumps(data, ensure_ascii=False, indent=2)}
    """

    response = requests.post(
        LLM_ENDPOINT,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "0m",
            "options": {
                "temperature": 0.2
            }
        }
    )

    return response.json()["response"]

def main():
    for filename in CORPUS:
        summary = generate_summary(filename)
        print(summary)

        output_dir = ROOT / 'summarisation' / 'results' / MODEL.replace(":", "_")
        os.makedirs(output_dir, exist_ok=True)

        with open(output_dir / f'{filename}.md', 'w', encoding='utf-8') as f:
            f.write(summary)

main()