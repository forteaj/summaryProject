import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

load_dotenv(find_dotenv())
API_KEY = os.getenv("VECTARA_API_KEY")

MODELS = [
    "llama3:8b", 
    "qwen2.5:7b", 
    "granite3.2:8b", 
    "deepseek-r1:8b",
    "mistral:7b-instruct"
]

CORPUS = [
    'ayudas_21-22', 
    'ayudas_22-23', 
    'ayudas_23-24', 
    'ayudas_24-25', 
    'ayudas_25-26'
]

LLM_ENDPOINT = "http://localhost:11434/api/generate"