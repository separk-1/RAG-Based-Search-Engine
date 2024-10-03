import os
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
import pdfplumber
import spacy
from tqdm import tqdm
from functions.functions_rag import (
    encode_pdf,
    retrieve_context_per_question,
    answer_question_from_context,
    create_question_answer_from_context_chain
)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './database'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load environment variables
load_dotenv()

# Load OpenAI API key from environment
openai_api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = openai_api_key

nlp = spacy.load("en_core_web_sm")

# File validation
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Extract text from a PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Find all PDFs in the folder
def find_all_pdfs(root_folder):
    pdf_files = []
    for dirpath, _, filenames in os.walk(root_folder):
        for file in filenames:
            if allowed_file(file):
                full_path = os.path.join(dirpath, file)
                pdf_files.append(full_path)
    return pdf_files

@app.route('/')
def home():
    return render_template('index.html')

from tqdm import tqdm

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({'error': 'Missing question'}), 400

    # Get all PDF files in the directory
    pdf_files = find_all_pdfs(app.config['UPLOAD_FOLDER'])

    if not pdf_files:
        return jsonify({'error': 'No files uploaded'}), 400

    combined_chunks_vector_store = None
    references = []

    # Progress bar to show file processing
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        chunks_vector_store = encode_pdf(pdf_file, chunk_size=1000, chunk_overlap=200)

        if combined_chunks_vector_store is None:
            combined_chunks_vector_store = chunks_vector_store
        else:
            combined_chunks_vector_store.merge_from(chunks_vector_store)

    # Retrieve the relevant context
    chunks_query_retriever = combined_chunks_vector_store.as_retriever(search_kwargs={"k": 2})
    context = retrieve_context_per_question(question, chunks_query_retriever)
    print("Retrieved Context: ", context)

    # Append source of related files to references
    for chunk in context:
        if isinstance(chunk, dict) and 'metadata' in chunk:
            if 'source' in chunk['metadata']:
                references.append(chunk['metadata']['source'])

    # Generate an answer using LLM
    llm = ChatOpenAI(temperature=0, model_name="gpt-4", max_tokens=2000)
    question_answer_from_context_chain = create_question_answer_from_context_chain(llm)
    result = answer_question_from_context(question, " ".join(context), question_answer_from_context_chain)

    return jsonify({'answer': result['answer'], 'context': result['context'], 'references': references}), 200

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, host='0.0.0.0', port=5001)
