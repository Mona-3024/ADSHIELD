import pandas as pd
import re
import json
import requests
from scrapy.selector import Selector
import nltk
from urllib.parse import urlparse

nltk.download('stopwords')

# Load the Excel file
file_path = "image_ads_data_easyocr.xlsx"
df = pd.read_excel(file_path)

# Function to clean text
def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = text.strip()
    return text

# Scam keywords
scam_keywords = [
    "congratulations", "winner", "claim your prize", "limited time", "urgent",
    "act now", "gift card", "free", "click here", "cash prize", "special offer",
    "black friday", "sale", "discount", "register now", "70%% off", "extra savings","prize"
]

# Function to detect scam text
def is_scam(text,url):
    text = clean_text(text)
    if any(keyword in text for keyword in scam_keywords):
        return "Scam"
    if 'youtube.com' in url or 'youtu.be' in url:
        return "Scam"
    # Check for Google redirection
    if 'google.com' in url:
        return "Scam"
    suspicious_domains = ["bit.ly", "tinyurl.com", "short.ly"]
    if any(domain in url for domain in suspicious_domains):
        return "Scam"

    return "Not Scam"


# Function to fetch and parse webpage content
def get_webpage_content(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        selector = Selector(text=response.text)
        return selector.xpath('//body//text()').getall()
    except Exception:
        return []

# Extract domain from URL
def get_domain_name(url):
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.split('.')[-2]  # Get main domain name
        return domain.lower()
    except Exception:
        return ""

# Function to classify based on extracted text and redirected content
# Function to classify based on extracted text and redirected content
def classify_scam(text, url):
    if not url:
        return "No URL"
    
    domain_name = get_domain_name(url)
    cleaned_text = clean_text(text)
    
    # Check if the brand name is present in the extracted text
    if domain_name and domain_name in cleaned_text:
        return "Not Scam"
    
    # Fallback to scam keyword detection
    return is_scam(text, url)  # Pass both text and url here

# Apply scam analysis for extracted text and redirection checks
df['Scam Analysis'] = df.apply(
    lambda row: classify_scam(row['extracted_text'], row['redirect_url']), axis=1
)

# Save report as JSON
data_list = df.to_dict(orient="records")
with open('scam_report.json', 'w') as json_file:
    json.dump(data_list, json_file, indent=4)
print("Data saved as scam_report.json")
# Count scam and not scam occurrences
scam_count = df['Scam Analysis'].value_counts().to_dict()

# Save scam count data to JSON
with open('scam_counts.json', 'w') as json_file:
    json.dump(scam_count, json_file, indent=4)

print("Data saved as scam_counts.json")