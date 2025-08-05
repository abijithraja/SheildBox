import joblib
import os

def load_auto_email_model():
    """
    Loads the auto email scan model. Uses the improved model if available.
    """
    print("Loading auto email model for auto scan...")
    
    # Try to use the improved model first, fallback to auto_email_model.pkl
    if os.path.exists("email_model_complete.pkl"):
        print("Using improved complete email model for auto scan...")
        model_package = joblib.load("email_model_complete.pkl")
        print(f"Auto email model loaded. Accuracy: {model_package['accuracy']:.4f}")
        return model_package
    elif os.path.exists("auto_email_model.pkl"):
        print("Using auto_email_model.pkl...")
        model_package = joblib.load("auto_email_model.pkl")
        print(f"Auto email model loaded. Accuracy: {model_package['accuracy']:.4f}")
        return model_package['model']
    else:
        # Fallback to individual components
        print("Loading individual model components for auto scan...")
        model = joblib.load("email_model.pkl")
        vectorizer = joblib.load("email_vectorizer.pkl")
        label_encoder = joblib.load("email_label_encoder.pkl")
        return {
            'model': model,
            'vectorizer': vectorizer,
            'label_encoder': label_encoder
        }
