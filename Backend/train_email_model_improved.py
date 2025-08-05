# train_email_model_improved.py - Enhanced email classification model
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import os

def load_dataset():
    """Load the dataset, preferring balanced version if available"""
    balanced_path = "merged_emails_balanced.csv"
    merged_path = "merged_emails.csv"
    
    if os.path.exists(balanced_path):
        print(f"Loading balanced dataset: {balanced_path}")
        df = pd.read_csv(balanced_path)
    elif os.path.exists(merged_path):
        print(f"Loading merged dataset: {merged_path}")
        df = pd.read_csv(merged_path)
    else:
        raise FileNotFoundError("Neither merged_emails_balanced.csv nor merged_emails.csv found")
    
    print(f"Loaded {len(df)} emails.")
    return df

def preprocess_data(df):
    """Clean and preprocess the email data"""
    print("Preprocessing and cleaning text...")
    
    # Handle missing values
    df["subject"] = df["subject"].fillna("").astype(str)
    df["body"] = df["body"].fillna("").astype(str) 
    df["label"] = df["label"].fillna("unknown").astype(str)
    
    # Combine subject and body
    df["text"] = (df["subject"] + " " + df["body"]).str.lower().str.strip()
    
    # Remove empty texts
    df = df[df["text"].str.len() > 0]
    
    print(f"After preprocessing: {len(df)} emails.")
    print("Label distribution:")
    print(df["label"].value_counts())
    
    return df

def train_model(df):
    """Train the email classification model"""
    print("Vectorizing text...")
    
    # TF-IDF Vectorization with enhanced parameters
    vectorizer = TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2),
        stop_words='english',
        min_df=2,  # Ignore terms that appear in fewer than 2 documents
        max_df=0.95  # Ignore terms that appear in more than 95% of documents
    )
    
    X = vectorizer.fit_transform(df["text"])
    print(f"Vectorized to {X.shape[1]} features.")
    
    # Encode labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["label"])
    
    print("Label mapping:", dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_))))
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Train classifier with balanced class weights
    print("Training model (LogisticRegression with balanced class weights)...")
    model = LogisticRegression(
        max_iter=1000, 
        multi_class='multinomial', 
        solver='lbfgs',
        class_weight='balanced',  # Handle class imbalance
        random_state=42
    )
    
    model.fit(X_train, y_train)
    print("Model training complete.")
    
    # Evaluation
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    return model, vectorizer, label_encoder, accuracy

def save_model_components(model, vectorizer, label_encoder, accuracy):
    """Save all model components"""
    print("\nSaving model components...")
    
    # Save individual components
    joblib.dump(model, "email_model.pkl")
    joblib.dump(vectorizer, "email_vectorizer.pkl")
    joblib.dump(label_encoder, "email_label_encoder.pkl")
    
    # Save a complete package for the auto model as well
    model_package = {
        'model': model,
        'vectorizer': vectorizer,
        'label_encoder': label_encoder,
        'accuracy': accuracy,
        'model_type': 'LogisticRegression',
        'categories': list(label_encoder.classes_),
        'training_date': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    joblib.dump(model_package, "email_model_complete.pkl")
    
    print("✅ Saved:")
    print("  - email_model.pkl")
    print("  - email_vectorizer.pkl") 
    print("  - email_label_encoder.pkl")
    print("  - email_model_complete.pkl")

if __name__ == "__main__":
    try:
        # Load dataset
        df = load_dataset()
        
        # Preprocess data
        df = preprocess_data(df)
        
        # Train model
        model, vectorizer, label_encoder, accuracy = train_model(df)
        
        # Save components
        save_model_components(model, vectorizer, label_encoder, accuracy)
        
        print(f"\n✅ Email model training complete! Final accuracy: {accuracy:.4f}")
        
    except Exception as e:
        print(f"❌ Error in training process: {str(e)}")
