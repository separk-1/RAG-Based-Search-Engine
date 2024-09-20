import spacy
import os
import pdfplumber
import yaml
from datetime import datetime  # Module to add timestamps

# Load configuration values from YAML file
with open('../config/config_extract_sentences.yml', 'r') as file:
    config = yaml.safe_load(file)

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Load the data folder path from the YAML configuration file
data_folder = config['paths']['data_folder']

# Function to extract text from a single PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        # Extract text from each page and append to the 'text' variable
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Load all PDFs from the specified data folder
def load_pdfs(data_folder):
    pdf_texts = {}
    # Loop through each file in the data folder
    for filename in os.listdir(data_folder):
        if filename.endswith('.pdf'):  # Only process PDF files
            pdf_path = os.path.join(data_folder, filename)
            pdf_texts[filename] = extract_text_from_pdf(pdf_path)
    return pdf_texts

# Extract text from all PDFs in the data folder
pdf_data = load_pdfs(data_folder)
print(f"Loaded {len(pdf_data)} PDF files.")

# Combine the text from all PDFs into a single string
combined_text = " ".join(pdf_data.values())

# Load temperature-related keywords from the YAML configuration file
temperature_keywords = config['keywords']['temperature_related']

# Function to extract sentences related to temperature keywords
def extract_temperature_related_sentences(text):
    doc = nlp(text)  # Process the text using SpaCy
    temperature_sentences = []
    
    # Create a list of all sentences in the text
    all_sentences = list(doc.sents)

    # Loop through each sentence and check if it contains any temperature-related keywords
    for sent in all_sentences:
        if any(keyword in sent.text.lower() for keyword in temperature_keywords):
            temperature_sentences.append(sent.text)

    return temperature_sentences, len(all_sentences)  # Return temperature-related sentences and the total number of sentences

# Extract sentences related to temperature
temperature_sentences, total_sentences = extract_temperature_related_sentences(combined_text)

# Create a timestamp based on the current time (MMDD_HHMMSS format)
timestamp = datetime.now().strftime("%m%d%H%M%S")

# Load the output file path from the YAML configuration file
output_file = config['paths']['output_file']

# Load the timestamp option from the YAML configuration file
add_timestamp = config['options'].get('add_timestamp', False)

# Add a timestamp to the filename if the 'add_timestamp' option is true
if add_timestamp:
    output_file_with_timestamp = f"{timestamp}_{os.path.basename(output_file)}"
else:
    output_file_with_timestamp = os.path.basename(output_file)

# Combine the directory path with the filename
output_file_with_timestamp = os.path.join(os.path.dirname(output_file), output_file_with_timestamp)

# Save the extracted temperature-related sentences to a text file
with open(output_file_with_timestamp, 'w') as f:
    for sentence in temperature_sentences:
        f.write(sentence + '\n')

# Calculate the percentage of temperature-related sentences
temperature_sentence_count = len(temperature_sentences)
temperature_ratio = (temperature_sentence_count / total_sentences) * 100

# Print the results
print(f"Total sentences: {total_sentences}")
print(f"Extracted {temperature_sentence_count} sentences related to temperature.")
print(f"Temperature-related sentences make up {temperature_ratio:.2f}% of all sentences.")
print(f"Temperature-related sentences saved to {output_file_with_timestamp}")