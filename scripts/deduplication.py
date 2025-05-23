import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz.distance import Levenshtein
from sentence_transformers import SentenceTransformer, util
import torch

# Similarity weights and threshold
EDIT_WEIGHT = 0.2
TFIDF_WEIGHT = 0.3
BERT_WEIGHT = 0.5
THRESHOLD = 0.9

# Load question data from the first column of A.csv
df = pd.read_csv(".csv", header=None)
questions = df[0].tolist()
n = len(questions)

# Compute BERT embeddings using SentenceTransformer
bert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
bert_embeddings = bert_model.encode(questions, convert_to_tensor=True)

# Compute TF-IDF vectors and cosine similarity matrix
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(questions)
tfidf_sim = cosine_similarity(tfidf_matrix)

# Set to store indices of duplicate questions
duplicate_indices = set()

# Compare each question with all subsequent ones
for i in range(n):
    if i in duplicate_indices:
        continue
    for j in range(i + 1, n):
        if j in duplicate_indices:
            continue

        # 1. String edit similarity (normalized Levenshtein distance)
        edit_sim = 1 - Levenshtein.distance(questions[i], questions[j]) / max(len(questions[i]), len(questions[j]))

        # 2. TF-IDF cosine similarity
        tfidf_score = tfidf_sim[i][j]

        # 3. BERT embedding cosine similarity
        bert_score = util.pytorch_cos_sim(bert_embeddings[i], bert_embeddings[j]).item()

        # Combined weighted similarity
        combined_score = (EDIT_WEIGHT * edit_sim +
                          TFIDF_WEIGHT * tfidf_score +
                          BERT_WEIGHT * bert_score)

        # Mark as duplicate if similarity exceeds threshold
        if combined_score > THRESHOLD:
            duplicate_indices.add(j)

# Drop duplicate rows and reset DataFrame index
clean_df = df.drop(index=duplicate_indices).reset_index(drop=True)

# Save deduplicated results to a new CSV file
clean_df.to_csv("A_deduplicated.csv", index=False, header=False)
print(f"Deduplication completed. Original: {n}, After: {len(clean_df)}, Removed: {n - len(clean_df)}.")
