import spacy
import os
import pdfplumber

# SpaCy 모델 로드
nlp = spacy.load("en_core_web_sm")

'''
Step 1: Load and Read the PDF Files
'''

# Path to the data folder
data_folder = '../data'

# Function to extract text from a single PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Load all PDFs from the ../data folder
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

# PDF 텍스트 결합 (하나의 문자열로 병합)
combined_text = " ".join(pdf_data.values())

# 온도와 관련된 키워드 목록 정의
temperature_keywords = ["temperature", "heat", "cooling", "thermal", "overheat", "overheating", "coolant", "hot"]

# 온도와 관련된 키워드가 포함된 문장 추출 함수
def extract_temperature_related_sentences(text):
    doc = nlp(text)
    temperature_sentences = []

    # 각 문장을 분석하여 온도 관련 키워드가 포함된 문장을 추출
    for sent in doc.sents:
        if any(keyword in sent.text.lower() for keyword in temperature_keywords):
            temperature_sentences.append(sent.text)

    return temperature_sentences

# 온도 관련 문장 추출
temperature_sentences = extract_temperature_related_sentences(combined_text)

# 추출된 문장 텍스트 파일로 저장
output_file = '../results/temperature_sentences.txt'

with open(output_file, 'w') as f:
    for sentence in temperature_sentences:
        f.write(sentence + '\n')

print(f"Extracted {len(temperature_sentences)} sentences related to temperature.")
print(f"Temperature-related sentences saved to {output_file}")