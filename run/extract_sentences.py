import spacy
import os
import pdfplumber
import yaml  # YAML 파일을 불러오기 위한 패키지

# YAML 파일에서 설정 값 로드
with open('../config.yml', 'r') as file:
    config = yaml.safe_load(file)

# SpaCy 모델 로드
nlp = spacy.load("en_core_web_sm")

'''
Step 1: Load and Read the PDF Files
'''

# YAML 파일에서 경로 불러오기
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

# PDF 텍스트 결합 (하나의 문자열로 병합)
combined_text = " ".join(pdf_data.values())

# YAML 파일에서 온도 관련 키워드 불러오기
temperature_keywords = config['keywords']['temperature_related']

# 온도와 관련된 키워드가 포함된 문장 추출 함수
def extract_temperature_related_sentences(text):
    doc = nlp(text)
    temperature_sentences = []
    
    # 총 문장 개수를 위한 리스트
    all_sentences = list(doc.sents)

    # 각 문장을 분석하여 온도 관련 키워드가 포함된 문장을 추출
    for sent in all_sentences:
        if any(keyword in sent.text.lower() for keyword in temperature_keywords):
            temperature_sentences.append(sent.text)

    return temperature_sentences, len(all_sentences)  # 온도 관련 문장과 총 문장 개수를 반환

# 온도 관련 문장 추출
temperature_sentences, total_sentences = extract_temperature_related_sentences(combined_text)

# YAML 파일에서 결과 파일 경로 불러오기
output_file = config['paths']['output_file']

# 추출된 문장 텍스트 파일로 저장
with open(output_file, 'w') as f:
    for sentence in temperature_sentences:
        f.write(sentence + '\n')

# 비율 계산
temperature_sentence_count = len(temperature_sentences)
temperature_ratio = (temperature_sentence_count / total_sentences) * 100

# 출력
print(f"Total sentences: {total_sentences}")
print(f"Extracted {temperature_sentence_count} sentences related to temperature.")
print(f"Temperature-related sentences make up {temperature_ratio:.2f}% of all sentences.")
print(f"Temperature-related sentences saved to {output_file}")