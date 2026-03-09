import streamlit as st
import os
import joblib
import re
import pandas as pd
from io import StringIO
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer

import nltk
nltk.download('stopwords')
nltk.download('wordnet')

# === Preprocessing ===
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
tokenizer = RegexpTokenizer(r'\b[a-z]{2,}\b')

def preprocess_email(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    tokens = tokenizer.tokenize(text)
    cleaned = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(cleaned)

# === Paths ===
base_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.normpath(os.path.join(base_dir, "..", "models"))
vectorizer_path = os.path.join(models_dir, "tfidf_vectorizer.pkl")

# === Load models dynamically ===
model_files = [f for f in os.listdir(models_dir) if f.endswith(".pkl") and "vectorizer" not in f]
model_dict = {}
for file in model_files:
    name = os.path.splitext(file)[0].replace("_", " ").title()
    model_dict[name] = joblib.load(os.path.join(models_dir, file))

vectorizer = joblib.load(vectorizer_path)

# === App UI ===
st.set_page_config(page_title="Multi-Model Phishing Detector", layout="centered")
st.title("📩 Multi-Model Phishing Email Analyzer")

uploaded_file = st.file_uploader("📤 Upload email file (.txt, .eml)", type=['txt', 'eml'])

if uploaded_file:
    file_details = {"filename": uploaded_file.name, "type": uploaded_file.type}
    st.write("🗂 File uploaded:", file_details["filename"])

    # Read uploaded content
    if uploaded_file.type == "text/plain":
        raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
    else:
        raw_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")

    st.subheader("📜 Raw Email Preview:")
    st.text_area("Content", raw_text, height=200)

    # Process
    cleaned = preprocess_email(raw_text)
    input_vector = vectorizer.transform([cleaned])

    st.subheader("🤖 Model Predictions:")
    result_data = []
    votes = {"phishing": 0, "legit": 0}

    for name, model in model_dict.items():
        try:
            prob = model.predict_proba(input_vector)[0][1]
        except:
            prob = None

        pred = model.predict(input_vector)[0]
        pred_label = "Phishing" if pred == 1 else "Legitimate"
        votes["phishing" if pred == 1 else "legit"] += 1

        result_data.append({
            "Model": name,
            "Prediction": "🟥 Phishing" if pred == 1 else "🟩 Legitimate",
            "Phishing Percentage (%)": f"{prob*100:.1f}%" if prob is not None else "N/A"
        })

    result_df = pd.DataFrame(result_data)
    st.dataframe(result_df)

    # Final Recommendation
    st.subheader("🧠 Final Recommendation")
    st.caption(f"This result is machine-generated. Developer isn’t responsible for any outcome under Malaysian law.")
    if votes["phishing"] > votes["legit"]:
        st.error(f"⚠️ Final Conclusion: **Phishing Email** ({votes['phishing']} of {len(model_dict)} models agree)")
    else:
        st.success(f"✅ Final Conclusion: **Legitimate Email** ({votes['legit']} of {len(model_dict)} models agree)")

st.markdown("---")
st.caption("Developed for Capstone Project by Chun Fan Sim · All rights reserved.")