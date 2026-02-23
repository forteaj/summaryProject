import markdown
import json
from bert_score import score as bert_score
from nltk.translate.bleu_score import sentence_bleu
from rouge import Rouge
from transformers import AutoModelForSequenceClassification

from summarisation.globals import ROOT, MODEL, CORPUS
from summarisation.util import load_file

def get_metrics(ground_truth, result):
    bleu = sentence_bleu([ground_truth.split()], result.split())

    rouge = Rouge().get_scores(result, ground_truth)

    bert_p, bert_r, bert_f1 = bert_score([result], [ground_truth], lang='es', model_type='bert-base-uncased')
    
    model = AutoModelForSequenceClassification.from_pretrained('vectara/hallucination_evaluation_model', trust_remote_code=True)
    hallucinations = model.predict([(ground_truth, result)])

    return {
        "BLEU": bleu,
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
        "Hallucinations score": hallucinations[0].item()
    }

def main():
    for filename in CORPUS:
        ground_truth = load_file(ROOT / 'summarisation' / 'ground_truth' / f'{filename}.md')
        result = load_file(ROOT / 'summarisation' / 'results' / MODEL.replace(":", "_") / f'{filename}.md')

        metrics = get_metrics(ground_truth, result)
        print(json.dumps(metrics, indent=2))

main()