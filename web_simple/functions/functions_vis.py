import io
import networkx as nx
import matplotlib.pyplot as plt
from flask import send_file
from collections import defaultdict
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import matplotlib
matplotlib.use('Agg')  # 플롯을 파일로 저장하기 위해 필요

nlp = spacy.load("en_core_web_sm")

# TF-IDF 키워드 추출 함수
def extract_keywords_tfidf(text, num_keywords=15):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])
    indices = X[0].toarray().argsort()[0][-num_keywords:]
    feature_names = vectorizer.get_feature_names_out()
    keywords = [feature_names[i] for i in indices if not re.search(r'\d', feature_names[i])]
    return keywords[:num_keywords]

# 텍스트에서 관계 추출 함수
def extract_relationships_paragraph(text, keywords):
    paragraphs = text.split('\n\n')
    relationships = defaultdict(list)
    
    for para in paragraphs:
        doc = nlp(para)
        subj, obj, verb = None, None, None
        for sent in doc.sents:
            for token in sent:
                if token.dep_ == 'nsubj' and token.text in keywords:
                    subj = token.text
                if token.dep_ in ('dobj', 'pobj') and token.text in keywords:
                    obj = token.text
                if token.pos_ == 'VERB':
                    verb = token.text
            if subj and obj and verb:
                relationships[subj].append((verb, obj))
                subj, obj, verb = None, None, None  # 초기화 후 반복
                
    return relationships

# 지식 그래프 생성 및 시각화 함수
def create_knowledge_graph(relationships):
    G = nx.DiGraph()
    for cause, effects in relationships.items():
        for verb, effect in effects:
            G.add_edge(cause, effect, label=verb)
    return G