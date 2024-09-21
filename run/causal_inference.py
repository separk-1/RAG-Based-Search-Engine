import re
import spacy
import networkx as nx
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer

# Load Spacy model for dependency parsing
nlp = spacy.load("en_core_web_sm")

# Step 1: Text preprocessing (tokenization and stop word removal)
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    words = [word for word in text.lower().split() if word.isalnum() and word not in stop_words]
    return ' '.join(words)

# Step 2: Extract keywords based on importance (using TF-IDF or other methods)
def extract_keywords_tfidf(text, num_keywords=15):
    # TF-IDF를 사용하여 중요한 키워드 추출
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])
    indices = X[0].toarray().argsort()[0][-num_keywords:]
    feature_names = vectorizer.get_feature_names_out()
    
    # 숫자가 포함된 키워드를 제거하는 필터링 추가
    keywords = [feature_names[i] for i in indices if not re.search(r'\d', feature_names[i])]
    
    return keywords[:num_keywords]

# Step 3: Extract relationships based on context, focusing on verb-based relations
def extract_relationships_context(text, keywords):
    doc = nlp(text)
    relationships = defaultdict(list)
    
    for sent in doc.sents:
        # Dependency parsing to identify subject-object pairs through verbs
        for token in sent:
            if token.pos_ == 'VERB':  # Focus on verbs to find relationships
                subj = None
                obj = None
                for child in token.children:
                    if child.dep_ == 'nsubj' and child.text in keywords:
                        subj = child.text
                    if child.dep_ in ('dobj', 'pobj') and child.text in keywords:
                        obj = child.text
                if subj and obj:
                    relationships[subj].append(obj)
    
    return relationships

# Step 4: Create a knowledge graph based on contextual relationships
def create_knowledge_graph(relationships):
    G = nx.DiGraph()
    for cause, effects in relationships.items():
        for effect in effects:
            G.add_edge(cause, effect)
    return G

# Step 5: Visualize the knowledge graph
def plot_graph(G):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='lightgreen', font_size=10, font_weight='bold', arrows=True)
    plt.title("Contextual Knowledge Graph")
    plt.show()

# Step 6: Read the document from a file
def read_document(file_path):
    with open(file_path, 'r') as file:
        document = file.read().replace('\n', ' ')  # Replace newline characters with space
    return document

# Main execution
file_path = '../results/temperature_sentences.txt'

# 기존 코드를 사용하여 문서 읽기 및 관계 추출 수행
document = read_document(file_path)

# TF-IDF 기반 키워드 추출 (숫자를 제외한)
keywords = extract_keywords_tfidf(document)
print("Extracted Keywords:", keywords)

# 문단 기반으로 관계 추출
relationships = extract_relationships_context(document, keywords)
print("Extracted Relationships:", relationships)

# 지식 그래프 생성 및 시각화
G = create_knowledge_graph(relationships)
plot_graph(G)