import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
import joblib

# Optional: XGBoost
try:
    from xgboost import XGBClassifier
    has_xgb = True
except ImportError:
    has_xgb = False

# === Load Data ===
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.normpath(os.path.join(base_dir, "..", "data", "final_combined_dataset.csv"))
df = pd.read_csv(data_path)

df = df.dropna(subset=['clean_email', 'label'])
X_raw = df['clean_email'].astype(str)
y = df['label']

# === Vectorize Text ===
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(X_raw)

# === Split ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === Models ===
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(n_estimators=100),
    "Naive Bayes": MultinomialNB(),
    "SVM (Linear)": LinearSVC()
}
if has_xgb:
    models["XGBoost"] = XGBClassifier(use_label_encoder=False, eval_metric="logloss")

results = []

# === Train & Evaluate ===
print("🚀 Training models...")
for name, model in models.items():
    print(f"🔧 Training {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    results.append({
        "Model": name,
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1": f1
    })
    
    # Save model
    model_file = os.path.join(base_dir, "..", "models", f"{name.replace(' ', '_').lower()}.pkl")
    joblib.dump(model, model_file)

# Save vectorizer
vectorizer_file = os.path.join(base_dir, "..", "models", "tfidf_vectorizer.pkl")
joblib.dump(vectorizer, vectorizer_file)

# === Summary Report ===
result_df = pd.DataFrame(results).sort_values(by="F1", ascending=False)
print("\n📊 Model Performance Summary:\n")
print(result_df.to_string(index=False))

best_model = result_df.iloc[0]["Model"]
print(f"\n✅ Best Performing Model: {best_model}")
