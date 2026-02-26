import requests
import json
import os

from summarisation.globals import LLM_ENDPOINT, CORPUS, MODELS

def generate_summary(filename, model):
    json_path = f"information_extraction/results/{filename}.json"
    with open(json_path, 'r') as j:
        data = json.load(j)

    prompt = f"""
    A partir de la información JSON proporcionada, redacta un documento formal completo de solicitud de beca de estudios, como si fuera un texto definitivo listo para su presentación oficial.

    JSON:
    {json.dumps(data, ensure_ascii=False, indent=2)}

    El texto debe:

    - Estar redactado íntegramente en español formal.
    - Tener una estructura clara con títulos y subtítulos coherentes.
    - Estar organizado en párrafos bien construidos.
    - Integrar toda la información disponible en el JSON de forma natural.
    - Omitir cualquier dato cuyo valor sea null.
    - NO inventar información bajo ningún concepto.
    - No utilizar listas o tablas salvo que sea estrictamente necesario.
    - No hacer referencias al formato de origen de los datos.
    - No utilizar expresiones como:
        "El texto describe...",
        "El JSON contiene...",
        "La información proporcionada...",
        "Este documento explica..."
    - NO explicar ni resumir: redacta directamente el documento final.

    El resultado debe leerse como un documento administrativo real, no como un resumen ni como un análisis.

    Comienza directamente con el título del documento.
    """

    response = requests.post(
        LLM_ENDPOINT,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "30s",
            "options": {
                "temperature": 0.2
            }
        }
    )

    return response.json()["response"]

def main():
    for model in MODELS:
        print("Using", model)
        for filename in CORPUS:
            print("    Generating", filename)
            summary = generate_summary(filename, model)

            output_dir = f"summarisation/results/{model.replace(':', '_')}"
            os.makedirs(output_dir, exist_ok=True)

            with open(output_dir + f'/{filename}.md', 'w', encoding='utf-8') as f:
                f.write(summary)

if __name__ == "__main__":
    main()