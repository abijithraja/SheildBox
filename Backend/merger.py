
import pandas as pd
import os

# Path to dataset folder
dataset_folder = "email_datasets"

# Mapping: file name ➜ class label
label_map = {
    "phishing_email.csv": "phishing",
    "Nazario.csv": "phishing",
    "Nigerian_Fraud.csv": "scam",
    "CEAS_08.csv": "safe",
    "Enron.csv": "safe",
    "Ling.csv": "safe",
    "SpamAssasin.csv": "safe"
}

# List to collect all dataframes
dfs = []

for filename, label in label_map.items():
    file_path = os.path.join(dataset_folder, filename)
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # Normalize column names
            df.columns = [c.lower().strip() for c in df.columns]

            # Extract subject and body based on available columns
            if "subject" in df.columns and "body" in df.columns:
                df = df[["subject", "body"]].copy()
            elif "text" in df.columns:
                df["subject"] = ""
                df["body"] = df["text"]
                df = df[["subject", "body"]].copy()
            elif "text_combined" in df.columns:
                df["subject"] = ""
                df["body"] = df["text_combined"]
                df = df[["subject", "body"]].copy()
            else:
                print(f"⚠️ Skipped (no usable columns): {filename}")
                continue

            # Add source and label columns
            df["source"] = filename.replace(".csv", "").lower()
            df["label"] = label

            # Append to list
            dfs.append(df)
            print(f"✅ Loaded: {filename} ({len(df)} rows)")
        except Exception as e:
            print(f"❌ Failed to load {filename}: {e}")
    else:
        print(f"❌ File not found: {filename}")

# Merge and export
if dfs:
    merged = pd.concat(dfs, ignore_index=True)
    merged.to_csv("merged_emails.csv", index=False)
    print(f"\n✅ Merged {len(dfs)} files into 'merged_emails.csv' with {len(merged)} rows.")
else:
    print("\n❌ No data merged. Check your file paths.")
