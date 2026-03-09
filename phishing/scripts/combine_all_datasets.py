import os
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer

# === Setup ===
nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
tokenizer = RegexpTokenizer(r'\b[a-z]{2,}\b')

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    tokens = tokenizer.tokenize(text)
    cleaned = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(cleaned)

def load_and_process(filepath, text_fields, label_value=None):
    df = pd.read_csv(filepath)
    
    # Auto-label if needed
    if label_value is not None:
        df['label'] = label_value

    # Combine text fields (e.g., subject + body)
    df['combined_text'] = df[text_fields].fillna('').agg(' '.join, axis=1)
    df['clean_email'] = df['combined_text'].apply(clean_text)
    
    return df[['clean_email', 'label']]

# === Base Paths ===
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.normpath(os.path.join(base_dir, "..", "data"))
output_path = os.path.join(data_dir, "final_combined_dataset.csv")

# === Datasets ===
datasets = []

# Kaggle (already preprocessed)
kaggle = pd.read_csv(os.path.join(data_dir, "preprocessed_phishing_dataset.csv"))
datasets.append(kaggle[['clean_email', 'label']])

# Nazario
datasets.append(load_and_process(os.path.join(data_dir, "nazario_dataset.csv"), ['subject', 'body']))

# Enron (legitimate only)
datasets.append(load_and_process(os.path.join(data_dir, "enron_dataset.csv"), ['body'], label_value=0))

# CEAS 2008
datasets.append(load_and_process(os.path.join(data_dir, "ceas_08.csv"), ['subject', 'body']))

# Ling-Spam
datasets.append(load_and_process(os.path.join(data_dir, "ling_spam.csv"), ['subject', 'body']))

# Nigerian Fraud
datasets.append(load_and_process(os.path.join(data_dir, "nigerian_fraud.csv"), ['body'], label_value=1))

# SpamAssassin
datasets.append(load_and_process(os.path.join(data_dir, "spamassassin.csv"), ['subject', 'body']))

# === Combine all
all_df = pd.concat(datasets, ignore_index=True)
all_df = all_df.dropna().drop_duplicates()

print(f"✅ Total records: {len(all_df)}")
print(f"   🟥 Phishing: {sum(all_df.label == 1)}")
print(f"   🟩 Legitimate: {sum(all_df.label == 0)}")

# === Save final CSV
all_df.to_csv(output_path, index=False)
print(f"\n📦 Final dataset saved to: {output_path}")
