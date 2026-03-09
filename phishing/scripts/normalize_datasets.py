import pandas as pd
import os

# Load dataset
file_path = os.path.join("..", "data", "phishing_email.csv")  # make sure the name matches
df = pd.read_csv(file_path)

# Show the original columns
print("🧾 Columns in dataset:", df.columns.tolist())

# Directly rename columns to match our system
df.rename(columns={'text_combined': 'email'}, inplace=True)

# Ensure only 'email' and 'label' columns remain
df = df[['email', 'label']]

# Show class distribution
print("📊 Class distribution:\n", df['label'].value_counts())

# Save cleaned version
output_path = os.path.join("..", "data", "cleaned_phishing_dataset.csv")
df.to_csv(output_path, index=False)

print(f"✅ Cleaned dataset saved at: {output_path}")
