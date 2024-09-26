import os
import sys

from dotenv import load_dotenv
import json

from deepeval import evaluate
from deepeval.metrics import GEval, FaithfulnessMetric, ContextualRelevancyMetric
from deepeval.test_case import LLMTestCaseParams
from langchain_openai import ChatOpenAI

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from openai import RateLimitError
from rank_bm25 import BM25Okapi
import fitz
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../functions')))

from functions_rag import (
    replace_t_with_space,
    text_wrap,
    encode_pdf,
    encode_from_string,
    retrieve_context_per_question,
    create_question_answer_from_context_chain,
    answer_question_from_context,
    show_context,
    read_pdf_to_string,
    bm25_retrieval,
    exponential_backoff,
    retry_with_exponential_backoff,
    create_deep_eval_test_cases
)

# Load environment variables from a .env file
print("Loading environment variables...")

load_dotenv()  # .env 파일에서 환경 변수를 로드

openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key environment variable
os.environ["OPENAI_API_KEY"] = openai_api_key

print("OpenAI API Key set.")

# Define evaluation metrics
correctness_metric = GEval(
    name="Correctness",
    model="gpt-4o",
    evaluation_params=[
        LLMTestCaseParams.EXPECTED_OUTPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT
    ],
    evaluation_steps=[
        "Determine whether the actual output is factually correct based on the expected output."
    ],
)

faithfulness_metric = FaithfulnessMetric(
    threshold=0.7,
    model="gpt-4",
    include_reason=False
)

relevance_metric = ContextualRelevancyMetric(
    threshold=1,
    model="gpt-4",
    include_reason=True
)

def evaluate_rag(chunks_query_retriever, num_questions: int = 5) -> None:
    """
    Evaluate the RAG system using predefined metrics.

    Args:
        chunks_query_retriever: Function to retrieve context chunks for a given query.
        num_questions (int): Number of questions to evaluate (default: 5).
    """
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o", max_tokens=2000)
    question_answer_from_context_chain = create_question_answer_from_context_chain(llm)

    # Load questions and answers from JSON file
    q_a_file_name = "../data/custom_q_a.json"
    with open(q_a_file_name, "r", encoding="utf-8") as json_file:
        q_a = json.load(json_file)

    questions = [qa["question"] for qa in q_a][:num_questions]
    ground_truth_answers = [qa["answer"] for qa in q_a][:num_questions]
    generated_answers = []
    retrieved_documents = []

    # Generate answers and retrieve documents for each question
    for question in questions:
        context = retrieve_context_per_question(question, chunks_query_retriever)
        retrieved_documents.append(context)
        context_string = " ".join(context)
        result = answer_question_from_context(question, context_string, question_answer_from_context_chain)
        generated_answers.append(result["answer"])

    # Create test cases and evaluate
    test_cases = create_deep_eval_test_cases(questions, ground_truth_answers, generated_answers, retrieved_documents)
    evaluate(
        test_cases=test_cases,
        metrics=[correctness_metric, faithfulness_metric, relevance_metric]
    )
    
print("Evaluation metrics defined.")


if __name__ == "__main__":
    # Ensure main block for running setup
    print("Running main setup...")

path = "../data/ML070610277.pdf"

# Encoding PDF to vector store
print(f"Encoding PDF at path: {path} ...")
chunks_vector_store = encode_pdf(path, chunk_size=1000, chunk_overlap=200)
print("PDF encoding completed.")

# Set up the retriever
print("Setting up retriever with vector store...")
chunks_query_retriever = chunks_vector_store.as_retriever(search_kwargs={"k": 2})
print("Retriever set up completed.")

# Example query
test_query = "What is the title of this document?"
print(f"Running query: {test_query}")
context = retrieve_context_per_question(test_query, chunks_query_retriever)

# Show retrieved context
print("Retrieved context:")
show_context(context)

# Evaluate the RAG system with the retriever
print("Evaluating RAG system with retriever...")
evaluate_rag(chunks_query_retriever)
print("RAG evaluation completed.")