import spacy
import os
import pdfplumber
import yaml  

with open('../config.yml', 'r') as file:
    config = yaml.safe_load(file)

nlp = spacy.load("en_core_web_sm")

data_folder = config['paths']['data_folder']

# Function to extract text from a single PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Load all PDFs from the data folder
def load_pdfs(data_folder):
    pdf_texts = {}
    for filename in os.listdir(data_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(data_folder, filename)
            pdf_texts[filename] = extract_text_from_pdf(pdf_path)
    return pdf_texts

# Extract text from all PDFs
pdf_data = load_pdfs(data_folder)
print(f"Loaded {len(pdf_data)} PDF files.")

combined_text = " ".join(pdf_data.values())

temperature_keywords = config['keywords']['temperature_related']
x
def extract_temperature_related_sentences(text):
    doc = nlp(text)
    temperature_sentences = []
    
    all_sentences = list(doc.sents)

    for sent in all_sentences:
        if any(keyword in sent.text.lower() for keyword in temperature_keywords):
            temperature_sentences.append(sent.text)

    return temperature_sentences, len(all_sentences) 

temperature_sentences, total_sentences = extract_temperature_related_sentences(combined_text)

output_file = config['paths']['output_file']

with open(output_file, 'w') as f:
    for sentence in temperature_sentences:
        f.write(sentence + '\n')

temperature_sentence_count = len(temperature_sentences)
temperature_ratio = (temperature_sentence_count / total_sentences) * 100

print(f"Total sentences: {total_sentences}")
print(f"Extracted {temperature_sentence_count} sentences related to temperature.")
print(f"Temperature-related sentences make up {temperature_ratio:.2f}% of all sentences.")
print(f"Temperature-related sentences saved to {output_file}")