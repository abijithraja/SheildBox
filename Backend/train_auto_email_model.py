"""
Auto Email classification model training script for ShieldBox extension.
This script processes email datasets to train a model for auto email scan (separate from manual scan).
"""

import pandas as pd
import numpy as np
import re
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# Email categories to classify (can be customized for auto scan)
EMAIL_CATEGORIES = [
    "phishing",
    "spam",
    "legitimate",
    "malware",
    "scam",
    "spear_phishing",
    "fraudulent",
    "safe"
]

print("Starting auto email model training...")
print(f"Target categories: {', '.join(EMAIL_CATEGORIES)}")

# Define datasets and their default categories
DATASETS = {
    "phishing_email.csv": "phishing",
    "CEAS_08.csv": "spam",
    "Enron.csv": "legitimate",
    "Ling.csv": "legitimate",
    "Nazario.csv": "phishing",
    "Nigerian_Fraud.csv": "fraudulent",
    "SpamAssasin.csv": "spam",
    "synthetic_donation_scams.csv": "fraudulent"
}

def extract_email_features(email_data):
    text = ""
    subject = email_data.get('subject', '')
    body = email_data.get('body', '')
    # Convert to string and handle NaN/None
    if pd.isna(subject):
        subject = ""
    if pd.isna(body):
        body = ""
    subject = str(subject)
    body = str(body)
    if subject:
        text += subject + " "
    if body:
        text += body
    if not text:
        return ""
    text = text.lower()
    url_regex = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    text = re.sub(url_regex, " URL ", text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Add a donation scam keyword flag as a feature
    donation_keywords = [
        "donate", "donation", "charity", "fund", "fundraiser", "help", "support", "contribute", "relief", "urgent", "bank transfer", "account details", "wire", "bitcoin", "crypto", "ngo", "foundation", "orphans", "disaster", "emergency", "aid", "gift", "generous", "contribution", "please send", "payment", "transfer", "beneficiary"
    ]
    donation_flag = any(kw in text for kw in donation_keywords)
    # Append the flag as a token to the text for the vectorizer
    if donation_flag:
        text += " DONATION_SCAM_KEYWORD"
    return text

def load_datasets(dataset_folder):
    print(f"Loading datasets from: {dataset_folder}")
    all_data = []
    for filename, default_category in DATASETS.items():
        file_path = os.path.join(dataset_folder, filename)
        if not os.path.exists(file_path):
            print(f"Warning: Dataset file {filename} not found, skipping.")
            continue
        print(f"Processing {filename}...")
        try:
            try:
                df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
            except:
                df = pd.read_csv(file_path, encoding='latin1', on_bad_lines='skip')
            if 'body' not in df.columns:
                if 'content' in df.columns:
                    df['body'] = df['content']
                elif 'text' in df.columns:
                    df['body'] = df['text']
                elif 'message' in df.columns:
                    df['body'] = df['message']
                elif 'email' in df.columns:
                    df['body'] = df['email']
                elif len(df.columns) > 0:
                    df['body'] = df[df.columns[0]]
                else:
                    df['body'] = ""
            if 'subject' not in df.columns:
                if 'subject_line' in df.columns:
                    df['subject'] = df['subject_line']
                else:
                    df['subject'] = ""
            if 'category' not in df.columns:
                df['category'] = default_category
            df['body'] = df['body'].fillna("")
            df['subject'] = df['subject'].fillna("")
            df['email_text'] = df.apply(
                lambda row: extract_email_features({
                    'subject': row['subject'],
                    'body': row['body']
                }),
                axis=1
            )
            if len(df) > 2000:
                print(f"  Dataset is large ({len(df)} records), sampling 2000 records")
                df = df.sample(2000, random_state=42)
            all_data.append(df[['email_text', 'category']])
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
    if not all_data:
        raise ValueError("No datasets could be loaded. Check file paths and formats.")
    combined_data = pd.concat(all_data, ignore_index=True)
    print(f"Dataset loading complete. Total samples: {len(combined_data)}")
    print("\nCategory distribution:")
    for category, count in combined_data['category'].value_counts().items():
        print(f"  {category}: {count} emails")
    return combined_data

def train_email_model(data):
    print("\nPreparing data for training...")
    X = data['email_text']
    y = data['category']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    print("\nTraining model using RandomForest...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=3000, ngram_range=(1, 2))),
        ('classifier', OneVsRestClassifier(RandomForestClassifier(
            n_estimators=100,
            max_depth=None,
            random_state=42,
            n_jobs=-1
        )))
    ])
    pipeline.fit(X_train, y_train)
    model_type = "RandomForest"
    print("\nEvaluating model...")
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    model_package = {
        'model': pipeline,
        'accuracy': accuracy,
        'model_type': model_type,
        'categories': list(set(y)),
        'training_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'samples': len(X)
    }
    return model_package

if __name__ == "__main__":
    try:
        import os
        # Prefer the balanced merged dataset if it exists
        balanced_path = os.path.join(os.path.dirname(__file__), "merged_emails_balanced.csv")
        merged_path = os.path.join(os.path.dirname(__file__), "merged_emails.csv")
        if os.path.exists(balanced_path):
            print("Using balanced dataset: merged_emails_balanced.csv")
            df = pd.read_csv(balanced_path)
            # Map to expected columns for training
            df['email_text'] = df.apply(lambda row: extract_email_features({'subject': row.get('subject', ''), 'body': row.get('body', '')}), axis=1)
            df['category'] = df['label'] if 'label' in df.columns else 'fraudulent'
            email_data = df[['email_text', 'category']]
        elif os.path.exists(merged_path):
            print("Using merged dataset: merged_emails.csv")
            df = pd.read_csv(merged_path)
            df['email_text'] = df.apply(lambda row: extract_email_features({'subject': row.get('subject', ''), 'body': row.get('body', '')}), axis=1)
            df['category'] = df['label'] if 'label' in df.columns else 'fraudulent'
            email_data = df[['email_text', 'category']]
        else:
            # Fallback to folder-based loading
            dataset_folder = "email_datasets"
            email_data = load_datasets(dataset_folder)
        model_package = train_email_model(email_data)
        output_path = "auto_email_model.pkl"
        joblib.dump(model_package, output_path)
        print(f"\nAuto email model training complete!")
        print(f"Model saved to {output_path}")
        print(f"Accuracy: {model_package['accuracy']:.4f}")
        print(f"Model type: {model_package['model_type']}")
        print(f"Categories: {', '.join(model_package['categories'])}")
    except Exception as e:
        print(f"Error in training process: {str(e)}")
