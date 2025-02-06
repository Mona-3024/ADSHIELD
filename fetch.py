import easyocr
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import pandas as pd
import numpy as np
import cv2
import json

# Load image URLs from ads.json
with open('ads.json', 'r') as file:
    image_urls = json.load(file)

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])

def extract_text_from_image(image_url):
    try:
        # Fetch the image from the URL
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Open the image using PIL
        img = Image.open(BytesIO(response.content))
        
        # Convert the image to a numpy array for EasyOCR
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Extract text using EasyOCR
        result = reader.readtext(img_cv)
        
        # Join the extracted text
        extracted_text = " ".join([text[1] for text in result])
        return extracted_text if extracted_text else "No text found"
    
    except UnidentifiedImageError:
        return "Unsupported image format"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from {image_url}: {e}")
        return "Error fetching image"
    except Exception as e:
        print(f"Error processing image from {image_url}: {e}")
        return "Error processing image"

# List to hold the image information
image_data = []

# Extract text from all images
for image_info in image_urls:
    image_url = image_info['image_url']
    redirect_url = image_info['redirect_url']
    print(f"Processing: {image_url}")
    
    # Extract text from the image
    extracted_text = extract_text_from_image(image_url)
    
    # Add extracted text and redirect URL to the data
    image_data.append({
        'image_url': image_url,
        'extracted_text': extracted_text,
        'redirect_url': redirect_url
    })

# Create a DataFrame to store the image data
df = pd.DataFrame(image_data)

# Save the DataFrame to an Excel file
excel_filename = "image_ads_data_easyocr.xlsx"
df.to_excel(excel_filename, index=False)

print(f"Image data with redirect links has been saved to {excel_filename}")