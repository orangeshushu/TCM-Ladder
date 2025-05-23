import csv
import jieba
import nltk
import torch
import numpy as np
from rouge_chinese import Rouge
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate import meteor_score
from transformers import BertModel, BertTokenizer

# Ensure NLTK resources are available
try:
    nltk.data.find('wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('omw-1.4')
except LookupError:
    nltk.download('omw-1.4')


def calculate_metrics(hypothesis, reference, bert_model, bert_tokenizer):
    results = {}

    # Tokenization
    hypothesis_tokens = list(jieba.cut(hypothesis))
    reference_tokens = list(jieba.cut(reference))

    # BLEU-4
    smoothie = SmoothingFunction().method1
    bleu_score = sentence_bleu([reference_tokens], hypothesis_tokens,
                               weights=(0.25, 0.25, 0.25, 0.25),
                               smoothing_function=smoothie)
    results['BLEU-4'] = bleu_score

    # ROUGE-L
    rouge = Rouge()
    hyp_rouge = ' '.join(hypothesis_tokens)
    ref_rouge = ' '.join(reference_tokens)
    rouge_scores = rouge.get_scores(hyp_rouge, ref_rouge)
    results['ROUGE-L'] = rouge_scores[0]['rouge-l']['f']

    # METEOR
    meteor = meteor_score.meteor_score([reference_tokens], hypothesis_tokens)
    results['METEOR'] = meteor

    # BERTScore
    results['BERTScore'] = calculate_bert_score(hypothesis, reference, bert_model, bert_tokenizer)

    return results


def calculate_bert_score(hypothesis, reference, model, tokenizer):
    model.eval()
    with torch.no_grad():
        ref_inputs = tokenizer(reference, return_tensors='pt', truncation=True, padding=True)
        ref_outputs = model(**ref_inputs)
        ref_embeddings = ref_outputs.last_hidden_state.mean(dim=1)

        hyp_inputs = tokenizer(hypothesis, return_tensors='pt', truncation=True, padding=True)
        hyp_outputs = model(**hyp_inputs)
        hyp_embeddings = hyp_outputs.last_hidden_state.mean(dim=1)

    cos_sim = torch.nn.functional.cosine_similarity(ref_embeddings, hyp_embeddings).item()
    return cos_sim


def evaluate_csv(reference_path, candidate_path):
    tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
    model = BertModel.from_pretrained('bert-base-chinese')

    metrics_total = {
        'BLEU-4': 0.0,
        'ROUGE-L': 0.0,
        'METEOR': 0.0,
        'BERTScore': 0.0
    }
    count = 0

    with open(reference_path, encoding='utf-8-sig') as ref_file, open(candidate_path, encoding='utf-8-sig') as hyp_file:
        ref_reader = csv.reader(ref_file)
        hyp_reader = csv.reader(hyp_file)

        for ref_row, hyp_row in zip(ref_reader, hyp_reader):
            if not ref_row or not hyp_row:
                continue
            reference = ref_row[0].strip()
            hypothesis = hyp_row[0].strip()
            if not reference or not hypothesis:
                continue

            metrics = calculate_metrics(hypothesis, reference, model, tokenizer)
            for k in metrics:
                metrics_total[k] += metrics[k]
            count += 1

    print("Average Evaluation Metrics:")
    for k in metrics_total:
        avg = metrics_total[k] / count if count > 0 else 0.0
        print(f"{k}: {avg:.4f}")


if __name__ == "__main__":
    evaluate_csv('A.csv', 'B.csv')
