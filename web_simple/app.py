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

@app.route('/')
def home():
    return render_template('index.html')  # index.html 파일이 templates 폴더에 있어야 함

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
    
    print("references", references)

    return jsonify({'answer': result['answer'], 'context': result['context'], 'references': references}), 200


if __name__ == '__main__':
    # 업로드 폴더가 없으면 생성
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5001)