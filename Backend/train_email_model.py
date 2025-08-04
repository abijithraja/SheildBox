# train_email_model.py - For emails with subject/body
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

print("Loading merged dataset...")
df = pd.read_csv("merged_emails.csv")

# Combine subject and body
df["text"] = (df["subject"].fillna("") + " " + df["body"].fillna("")).str.strip()

# Drop empty messages
df = df[df["text"].str.strip().astype(bool)]

# Encode labels: phishing=2, scam=1, safe=0
label_encoder = LabelEncoder()
df["label_encoded"] = label_encoder.fit_transform(df["label"])

print("Label mapping:", dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_))))
# Example: {'phishing': 2, 'safe': 1, 'scam': 0}

# Split
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label_encoded"], test_size=0.2, random_state=42, stratify=df["label_encoded"]
)

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),
    stop_words='english'
)

print("Extracting TF-IDF features...")
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train classifier
model = LogisticRegression(max_iter=1000, class_weight="balanced")
print("Training model...")
model.fit(X_train_tfidf, y_train)

# Evaluation
y_pred = model.predict(X_test_tfidf)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# Save model, vectorizer, and label encoder
print("\nSaving model components...")
joblib.dump(model, "email_model.pkl")
joblib.dump(vectorizer, "email_vectorizer.pkl")
joblib.dump(label_encoder, "email_label_encoder.pkl")

print("✅ Model training complete.")
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

print("Loading dataset (subject, body, label)...")
df = pd.read_csv("merged_emails.csv", usecols=["subject", "body", "label"])
print(f"Loaded {len(df)} emails.")

print("Preprocessing and cleaning text...")
df.dropna(subset=["subject", "body", "label"], inplace=True)
df["text"] = (df["subject"].astype(str) + " " + df["body"].astype(str)).str.lower()

print("Vectorizing text...")
vectorizer = TfidfVectorizer(stop_words='english', max_features=20000)
X = vectorizer.fit_transform(df["text"])

# Encode labels
le = LabelEncoder()
y = le.fit_transform(df["label"].astype(str))

print("Vectorized text.")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Training model (LogisticRegression)...")
model = LogisticRegression(max_iter=1000, multi_class='multinomial', solver='lbfgs')
model.fit(X_train, y_train)
print("Model training complete.")

# Evaluation
y_pred = model.predict(X_test)
print("\nModel trained:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# Save model, vectorizer, and label encoder
joblib.dump(model, "email_model.pkl")
joblib.dump(vectorizer, "email_vectorizer.pkl")
joblib.dump(le, "email_label_encoder.pkl")
print("Saved model, vectorizer, and label encoder.")
