import pandas as pd
df = pd.read_csv("merged_emails.csv")
print(df['label'].value_counts())
