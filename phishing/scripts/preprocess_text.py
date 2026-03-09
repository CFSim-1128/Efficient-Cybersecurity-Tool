import pandas as pd
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer

# === Step 1: NLTK Setup ===
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('punkt_tab')

# === Step 2: Use absolute paths ===
base_dir = os.path.dirname(os.path.abspath(__file__))

input_path = os.path.normpath(os.path.join(base_dir, "..", "data", "cleaned_phishing_dataset.csv"))
output_path = os.path.normpath(os.path.join(base_dir, "..", "data", "preprocessed_phishing_dataset.csv"))

# === Step 3: Check if file exists ===
if not os.path.exists(input_path):
    raise FileNotFoundError(f"❌ File not found: {input_path}")
print(f"📄 Input file found at: {input_path}")

# === Step 4: Load the dataset ===
df = pd.read_csv(input_path)

# === Step 5: Preprocessing function ===
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    # Ensure it's a string
    text = str(text)
    # Lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    # Remove punctuation and numbers
    text = re.sub(r"[^a-z\s]", "", text)
    # Tokenize
    tokenizer = RegexpTokenizer(r'\b[a-z]{2,}\b')  # match words with at least 2 letters
    tokens = tokenizer.tokenize(text)
    # Remove stopwords and lemmatize
    cleaned = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and len(word) > 2]
    return " ".join(cleaned)

# === Step 6: Apply to dataset ===
print("⚙️ Cleaning email content...")
df['clean_email'] = df['email'].apply(clean_text)

# === Step 7: Save preprocessed data ===
df[['clean_email', 'label']].to_csv(output_path, index=False)
print(f"✅ Preprocessed dataset saved at: {output_path}")
