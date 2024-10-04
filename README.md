# I'll create the README.md file for you with the provided structure and save it.

readme_content = """
# 🔍 RAG-Based Search Engine

This project is a **RAG (Retrieval-Augmented Generation)**-powered search engine designed to provide precise answers and references from regulatory documents related to nuclear safety. The system crawls safety datasets, processes them, and builds a search interface where users can input questions and receive relevant responses with cited references.

---

## 📦 Project Structure

### 0. **Requirements**
Ensure that the required packages and dependencies are installed by referencing the `requirements.txt` file.

### 1. **Dataset Collection** 🗂️

We collect nuclear safety regulation datasets from the NRC website.

- **`get_dataset.py`**:  
   This script crawls the NRC website for regulatory documents and stores them in the `./database/manual` directory. Any failed downloads are logged in `failed_downloads.txt`. Additionally, it saves the file path and corresponding file title in `file_title.csv`.
  
- **`check_dataset.py`**:  
   This script checks the `./database` folder for any corrupted or missing files and ensures that the dataset is intact.

### 2. **Run Search Engine** 🔍

- **`app.py`**:  
   This script runs the web application. When launched, it starts a local web server where users can input queries. By pressing the Enter key, the system provides an answer along with references to relevant documents.

### 3. **Functions** ⚙️

- **`functions/functions_rag.py`**:  
   This file stores all functions related to **RAG (Retrieval-Augmented Generation)** processing, including document chunking, encoding, and retrieval.

- **`functions/functions_utils.py`**:  
   This file stores utility functions such as file loading, dataset handling, and metadata processing.

### 4. **Frontend Design** 🎨

- **`static/`** and **`templates/`**:  
   These folders contain the HTML, CSS, and other static assets for the web application design. The user interface is clean, minimalistic, and responsive.

---

## 🛠️ Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-repository/RAG-Search-Engine.git
cd RAG-Search-Engine
