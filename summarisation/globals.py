from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#MODEL = "mistral:7b-instruct"  # llama?

MODEL = "llama3:latest"

CORPUS = [
    'ayudas_21-22', 
    'ayudas_22-23', 
    'ayudas_23-24', 
    'ayudas_24-25', 
    'ayudas_25-26'
]

LLM_ENDPOINT = "http://localhost:11434/api/generate"