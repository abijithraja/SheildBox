
import pandas as pd
import random

# Function to add a specific real scam email to the dataset
def add_real_scam_email(subject, body, sender=None):
    new_row = {"subject": subject, "body": body, "label": "fraudulent"}
    global df
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    print(f"Added real scam email: {subject[:40]}...")

# Always add this real scam email for training


# Load your merged dataset
merged_path = "merged_emails.csv"
df = pd.read_csv(merged_path)

# Always add these real scam emails for training
add_real_scam_email(
    subject="Fwd: 'Their Shelter Is Gone. Their Lives Are In Your Hands '",
    body="URGENT: Sponsor a Child, Save a Life. Dear Ki… not send real donations or personal information.",
    sender="Sri Vardhan"
)

# Add the promotional spam that Google correctly flagged but our model missed
add_real_scam_email(
    subject="Fwd: 'Act Fast! Only 3 Units Left in Stock '",
    body="EXCLUSIVE DEAL: ₹4999 Smartphone Just for You! Limited time offer. Act fast! Only 3 units left in stock. This is for testing purposes only. Do not enter real credentials.",
    sender="Sri Vardhan"
)

# How many new fraudulent samples to add (aim for class balance)
label_counts = df['label'].value_counts()
max_count = label_counts.max()
fraud_count = label_counts.get('fraudulent', 0)
add_count = max_count - fraud_count

# Synthetic fraudulent donation scam templates
subjects = [
    "Charity Request", "Help Needed", "Donation Appeal", "Urgent Fundraiser", "Charity Scam", "Disaster Relief Needed", "Support Our Cause", "Emergency Aid Request",
    "EXCLUSIVE DEAL", "Act Fast! Limited Time", "Only Few Left", "Special Offer Just for You", "Urgent Sale", "Flash Sale", "Don't Miss Out", "Last Chance"
]
bodies = [
    "Dear friend, we are raising urgent funds for disaster relief. Please donate via bank transfer to the following account details...",
    "Support our orphanage by sending your generous contribution to our foundation. Payment details attached.",
    "We need your help! Please send your donation to our NGO via wire or bitcoin.",
    "Emergency aid required. Kindly transfer your gift to the beneficiary account below.",
    "Donate now to help disaster victims. Send payment to our account. Thank you for your support.",
    "Your support is needed for our charity. Please make a donation using the attached bank details.",
    "Help us provide relief to those in need. Donate via crypto or wire transfer.",
    "Urgent: Orphanage needs your help. Please send your donation today.",
    "EXCLUSIVE DEAL: ₹4999 Smartphone Just for You! Limited time offer. Act fast! Only 3 units left in stock.",
    "Flash Sale! 90% OFF on all products. Hurry up! Limited stock available. Click now to claim your discount.",
    "Special offer exclusively for you! Don't miss this amazing deal. Order now before it's too late!",
    "URGENT: Your package is waiting. Pay small fee to receive your prize. Act fast - offer expires soon!",
    "Congratulations! You've won ₹50,000. Click here to claim your prize money. Limited time offer.",
    "Amazing discount! 80% off luxury items. Only for today! Don't let this opportunity slip away."
]

new_rows = []
for _ in range(add_count):
    subj = random.choice(subjects)
    body = random.choice(bodies)
    new_rows.append({"subject": subj, "body": body, "label": "fraudulent"})

# Add new rows to DataFrame
if new_rows:
    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    print(f"Added {len(new_rows)} synthetic fraudulent emails for class balance.")
else:
    print("No new fraudulent emails needed for balance.")

# Save the new merged dataset
out_path = "merged_emails_balanced.csv"
df.to_csv(out_path, index=False)
print(f"Saved balanced dataset to {out_path}")
