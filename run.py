import os
import pdfplumber

'''
Step 1: Load and Read the PDF Files
'''

# Path to the data folder
data_folder = './data'

# Function to extract text from a single PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Load all PDFs from the ./data folder
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


'''
Step 2: Extract Keywords Related to LOCA
'''
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

# Download stopwords for preprocessing
nltk.download('punkt_tab')
from nltk.corpus import stopwords

# Preprocess text data (remove stopwords, punctuation, etc.)
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    tokens = nltk.word_tokenize(text)
    tokens = [word.lower() for word in tokens if word.isalpha() and word not in stop_words]
    return " ".join(tokens)

# Apply preprocessing to the PDF data
preprocessed_texts = {filename: preprocess_text(text) for filename, text in pdf_data.items()}

# Use TF-IDF to extract keywords
def extract_keywords(text_data):
    vectorizer = TfidfVectorizer(max_df=0.85, max_features=1000)
    X = vectorizer.fit_transform(text_data)
    keywords = vectorizer.get_feature_names_out()
    return keywords

# Extract keywords from all documents
all_texts = list(preprocessed_texts.values())
keywords = extract_keywords(all_texts)
print(f"Extracted keywords: {keywords[:20]}")  # Show top 20 keywords

'''
Step 3: Build the Causal Relationship Knowledge Graph
'''
import networkx as nx
import matplotlib.pyplot as plt
import os

# Ensure the ./result folder exists
if not os.path.exists('./result'):
    os.makedirs('./result')

# Initialize the graph
G = nx.DiGraph()

# Example of how to add nodes and edges based on causal relationships
causal_pairs = [("coolant", "temperature rise"), ("pressure", "shutdown"), ("leakage", "reactor failure")]

for cause, effect in causal_pairs:
    G.add_edge(cause, effect)

# Customize the drawing to make it look nicer
plt.figure(figsize=(10, 7))

# Set positions for all nodes using spring layout for better spacing
pos = nx.spring_layout(G, seed=42)  # Adding a seed for reproducibility

# Draw nodes and edges with different styles and sizes
nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=4000, edgecolors='black', linewidths=1.5)
nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20, edge_color='gray')
nx.draw_networkx_labels(G, pos, font_size=12, font_color='darkblue', font_weight='bold')

# Title and axis details
plt.title('Causal Relationship Knowledge Graph', fontsize=16)
plt.axis('off')

# Save the graph to the result folder
plt.savefig('./result/causal_relationship_graph.png', format='PNG', dpi=300)

# Clear the plot to avoid overlapping of multiple graphs in future plots
plt.close()

print("Knowledge graph saved to ./result/causal_relationship_graph.png")