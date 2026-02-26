import markdown
import json
import os
import requests
from bert_score import score as bert_score
from rouge import Rouge

from summarisation.globals import MODELS, CORPUS, API_KEY
from summarisation.util import load_file

def get_metrics(ground_truth, result):
    rouge = Rouge().get_scores(result, ground_truth)

    bert_p, bert_r, bert_f1 = bert_score([result], [ground_truth], lang='es', model_type='bert-base-multilingual-cased')

    hallucinations = requests.post(
        "https://api.vectara.io/v2/evaluate_factual_consistency", 
        json={
            "model_parameters": {
                "model_name": "hhem_v2.3"
            },
            "generated_text": result,
            "source_texts": [ground_truth]
        }, 
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': API_KEY
        }
    )

    return {
        "ROUGE": {
            "ROUGE-1": {
                "Precision": rouge[0]["rouge-1"]["p"],
                "Recall": rouge[0]["rouge-1"]["r"],
                "F1": rouge[0]["rouge-1"]["f"]
            },
            "ROUGE-2": {
                "Precision": rouge[0]["rouge-2"]["p"],
                "Recall": rouge[0]["rouge-2"]["r"],
                "F1": rouge[0]["rouge-2"]["f"]
            },
            "ROUGE-L": {
                "Precision": rouge[0]["rouge-l"]["p"],
                "Recall": rouge[0]["rouge-l"]["r"],
                "F1": rouge[0]["rouge-l"]["f"]
            }
        },
        "BERTScore": {
            "Precision": bert_p.mean().item(),
            "Recall": bert_r.mean().item(),
            "F1": bert_f1.mean().item()
        },
        "Consistency": hallucinations.json().get("score")
    }

def main():
    for model in MODELS:
        for filename in CORPUS:
            print("Evaluating", model, ";", filename)
            ground_truth = load_file(f"summarisation/ground_truth/{filename}.md")
            result = load_file(f"summarisation/results/{model.replace(':', '_')}/{filename}.md")

            metrics = get_metrics(ground_truth, result)

            output_dir = f"summarisation/metrics/{model.replace(':', '_')}"
            os.makedirs(output_dir, exist_ok=True)

            with open(output_dir + f'/{filename}.json', 'w', encoding='utf-8') as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()