import pandas as pd

df = pd.read_csv("merged_emails.csv")
print("Unique classifications (labels):")
print(df['label'].unique())
print("\nLabel counts:")
print(df['label'].value_counts())
