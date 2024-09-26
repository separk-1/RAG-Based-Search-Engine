import os
from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI

import spacy
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO

import re
import spacy
import networkx as nx
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib
import pdfplumber
import plotly.graph_objects as go 
import io
matplotlib.use('Agg')

from functions.functions_rag import (
    encode_pdf,
    retrieve_context_per_question,
    answer_question_from_context,
    create_question_answer_from_context_chain,
    show_context
)

from functions.functions_vis import (
    extract_keywords_tfidf,
    extract_relationships_paragraph,
    create_knowledge_graph
)

app = Flask(__name__)

# 파일 업로드를 위한 설정
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load environment variables from a .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key manually as a backup (optional)
os.environ["OPENAI_API_KEY"] = openai_api_key
nlp = spacy.load("en_core_web_sm")

# 파일 확장자 허용 여부 확인 함수
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# PDF에서 텍스트 추출 함수
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# 홈페이지 라우팅 - uploads 폴더의 파일 목록을 보여줌
@app.route('/')
def index():
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]
    return render_template('index.html', files=files)

# 파일 업로드 처리
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    files = request.files.getlist('files')

    # 업로드된 파일 저장
    for file in files:
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

    # 업로드 완료 후 최신 파일 목록 반환
    return jsonify({'message': 'Files uploaded successfully', 'files': os.listdir(app.config['UPLOAD_FOLDER'])}), 200

# 파일 삭제 처리
@app.route('/remove', methods=['POST'])
def remove_file():
    data = request.get_json()
    filename = data.get('filename')

    # 파일 경로
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # 파일 삭제
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'message': 'File removed successfully', 'files': os.listdir(app.config['UPLOAD_FOLDER'])}), 200
    else:
        return jsonify({'error': 'File not found'}), 400

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({'error': 'Missing question'}), 400

    # 업로드된 모든 파일을 가져옴
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    pdf_files = [f for f in uploaded_files if allowed_file(f)]

    if not pdf_files:
        return jsonify({'error': 'No files uploaded'}), 400

    # 모든 PDF 파일을 하나의 벡터 저장소에 인코딩
    combined_chunks_vector_store = None
    for pdf_file in pdf_files:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file)
        chunks_vector_store = encode_pdf(filepath, chunk_size=1000, chunk_overlap=200)
        
        if combined_chunks_vector_store is None:
            combined_chunks_vector_store = chunks_vector_store
        else:
            # 기존 벡터 저장소에 추가
            combined_chunks_vector_store.merge_from(chunks_vector_store)

    # 벡터 저장소에서 질문에 대한 답변을 생성
    chunks_query_retriever = combined_chunks_vector_store.as_retriever(search_kwargs={"k": 2})
    
    # context를 받아오고 출력하는 부분
    context = retrieve_context_per_question(question, chunks_query_retriever)
    print("Retrieved Context: ", context)  # 실제로 검색된 문맥을 확인

    # LLM을 사용하여 답변 생성
    llm = ChatOpenAI(temperature=0, model_name="gpt-4", max_tokens=2000)
    question_answer_from_context_chain = create_question_answer_from_context_chain(llm)
    result = answer_question_from_context(question, " ".join(context), question_answer_from_context_chain)

    # context에서 출처 문장을 추출하여 references 리스트를 만듦
    references = [sentence.strip() for sentence in context]  # context에서 문장을 추출
    
    print("references:", references)

    return jsonify({'answer': result['answer'], 'context': result['context'], 'references': references}), 200

# 시각화 버튼 요청 처리
@app.route('/visualize', methods=['POST'])
def visualize():
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    pdf_files = [f for f in uploaded_files if allowed_file(f)]

    if not pdf_files:
        return jsonify({'error': 'No PDF files uploaded'}), 400

    combined_text = ""
    for pdf_file in pdf_files:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file)
        extracted_text = extract_text_from_pdf(filepath)
        combined_text += extracted_text + "\n"

    keywords = extract_keywords_tfidf(combined_text)
    relationships = extract_relationships_paragraph(combined_text, keywords)

    G = create_knowledge_graph(relationships)
    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 10))
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=15, font_weight="bold", arrows=True)
    plt.title("Knowledge Graph")

    # 이미지를 메모리 버퍼에 저장
    img = io.BytesIO()
    plt.savefig(img, format='PNG')
    img.seek(0)
    plt.close()

    return send_file(img, mimetype='image/png')


if __name__ == '__main__':
    # 업로드 폴더가 없으면 생성
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5001)