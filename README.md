
# 🔍 RAG-based Search Engine Project

This project is a search engine that utilizes Retrieval-Augmented Generation (RAG) to search through a dataset of nuclear safety regulations.

## 📋 Table of Contents

0. **requirements.txt**  
1. **Dataset Collection** - Scrapes safety regulation datasets from the NRC website.  
2. **Running the Search Engine** - How to execute the web app and search questions.  
3. **Functions** - Overview of the main functionalities and utilities.  
4. **Static and Templates** - Web design files.

---

## 0. requirements.txt

The project dependencies and required packages are listed in the `requirements.txt` file. This includes necessary Python libraries such as Flask, LangChain, and others for web scraping, RAG, and running the search engine.

---

## 1. Dataset Collection

This module scrapes safety regulation datasets from the NRC website and saves them into the `./database/manual` folder.

### Scripts:

- **get_dataset.py**:  
  Scrapes the dataset and stores it in `./database/manual`. If any downloads fail, they are logged in `failed_downloads.txt`. The file paths and titles are stored as a dictionary in `file_title.csv`.

- **check_dataset.py**:  
  Verifies if there are any corrupted files within the `./database` folder.

---

## 2. Running the Search Engine

To launch the search engine, run the `app.py` script. This will start a web server where you can input queries. After hitting enter, the system will retrieve answers along with relevant references.

### Key file:

- **app.py**:  
  Starts the search engine and provides answers to questions based on the dataset, along with references.

---

## 3. Functions

This section contains two utility modules:

- **functions/functions_rag.py**:  
  Contains core functions related to RAG-based search processes.

- **functions/functions_utils.py**:  
  Includes additional utility functions to support the search engine.

---

## 4. Static and Templates

The web design (CSS and HTML templates) is stored in the `static` and `templates` folders.

---

## 📦 How to Set Up

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/rag-search-engine.git
   cd rag-search-engine
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Search Engine**:
   ```bash
   python app.py
   ```
