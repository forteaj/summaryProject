import requests
import json
import os

from summarisation.globals import LLM_ENDPOINT, CORPUS, ROOT, MODEL

def generate_summary(filename):
    json_path = ROOT / 'information_extraction' / 'results' / f'{filename}.json'
    with open(json_path, 'r') as j:
        data = json.load(j)

    prompt = f"""
    Eres un redactor profesional.

Genera un RESUMEN EJECUTIVO del documento.

Objetivo:
- Explicar de forma global y sintética el propósito del documento
- Describir qué regula o establece
- Mantener un tono institucional

No incluyas:
- Listas detalladas de requisitos
- Umbrales económicos concretos
- Valores monetarios
- Plazos específicos
- Repeticiones de normativa

El resumen debe ser:
- Breve
- General
- Descriptivo
- No técnico-normativo

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

    data = response.json()
    print("STATUS:", response.status_code)
    print("JSON:", data)

    if "response" not in data:
        raise ValueError(f"Unexpected API response: {data}")

    return data["response"]


def generate_requirements(filename):
    json_path = ROOT / 'information_extraction' / 'results' / f'{filename}.json'

    with open(json_path, 'r', encoding='utf-8') as j:
        data = json.load(j)

    prompt = f"""
    Eres un analista experto en documentación administrativa y normativa de becas.

Tu tarea es identificar y redactar EXCLUSIVAMENTE los REQUISITOS GENERALES 
que debe cumplir un solicitante.

Presenta los requisitos como lista formal clara.
Cada requisito debe ser independiente.
No combines múltiples condiciones en una sola frase.

Definición:
Los requisitos generales incluyen únicamente condiciones, criterios o 
obligaciones que el solicitante debe cumplir (por ejemplo: elegibilidad, 
perfil requerido, limitaciones, incompatibilidades).

No incluyen:
- Plazos
- Fechas
- Procedimientos
- Documentación a presentar
- Información económica
- Descripciones generales

Instrucciones estrictas:
- No inventes información
- Usa únicamente datos explícitamente presentes en el contenido
- Ignora valores null, vacíos o ambiguos
- No infieras requisitos implícitos
- Redacta en español formal y claro
- Presenta el resultado como una sección institucional
- Organiza con títulos/subtítulos si es apropiado
- NO menciones el formato de entrada
- NO añadas explicaciones externas
- NO añadas conclusiones

REPETICIÓN DEL ENCARGO:

Identifica y redacta EXCLUSIVAMENTE los requisitos generales.
No inventes información.
Usa solo datos explícitos.

    Contenido:
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

    result = response.json()

    print("STATUS:", response.status_code)
    print("JSON:", result)

    if "response" not in result:
        raise ValueError(f"Unexpected API response: {result}")

    return result["response"]




def main():
    for filename in CORPUS:
        print(f"\nProcessing: {filename}")

        # --- GENERATE CONTENT ---
        requirements = generate_requirements(filename)
        print("\n--- REQUIREMENTS ---")
        print(requirements)

        summary = generate_summary(filename)
        print("\n--- SUMMARY ---")
        print(summary)

        # --- OUTPUT DIR ---
        output_dir = ROOT / 'summarisation' / 'results' / MODEL.replace(":", "_")
        os.makedirs(output_dir, exist_ok=True)

        # --- COMBINED DOCUMENT ---
        combined_document = f"""# REQUISITOS GENERALES

{requirements}

---

# RESUMEN DEL DOCUMENTO

{summary}
"""

        with open(output_dir / f"{filename}.md", 'w', encoding='utf-8') as f:
            f.write(combined_document)

#def main():
  #  for filename in CORPUS:
     #   summary = generate_summary(filename)
    #    print(summary)

    #    output_dir = ROOT / 'summarisation' / 'results' / MODEL.replace(":", "_")
    #    os.makedirs(output_dir, exist_ok=True)
#
    #    with open(output_dir / f"{filename}.md", 'w', encoding='utf-8') as f:
    #        f.write(summary)

main()