
# train_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
from feature_extractor import extract_features

# Load dataset
df = pd.read_csv("dataset_phishing.csv")  # Or your small custom csv
df["label"] = df["status"].apply(lambda x: 1 if x == "phishing" else 0)

# Use only URL for features
X = [extract_features(url) for url in df["url"]]
y = df["label"]

# Train model
model = RandomForestClassifier()
model.fit(X, y)

# Save model
joblib.dump(model, "phishing_model.pkl")
print("✅ Raw URL model trained and saved.")
