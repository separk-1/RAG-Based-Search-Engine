import os
import yaml

# Load configuration from config.yml
with open('../config/config_classify_sentences.yml', 'r') as file:
    config = yaml.safe_load(file)

# Load keywords from config
failure_keywords = config['keywords']['failure_keywords']
countermeasure_keywords = config['keywords']['countermeasure_keywords']
preventive_keywords = config['keywords']['preventive_keywords']

# Function to classify sentences based on keywords, allowing multiple categories
def classify_sentence(sentence):
    sentence_lower = sentence.lower()
    categories = []

    # Check if the sentence matches any keywords in each category
    if any(keyword in sentence_lower for keyword in failure_keywords):
        categories.append("failure")
    if any(keyword in sentence_lower for keyword in countermeasure_keywords):
        categories.append("countermeasure")
    if any(keyword in sentence_lower for keyword in preventive_keywords):
        categories.append("preventive")

    # If no categories match, return unclassified
    if not categories:
        return ["unclassified"]
    
    return categories

# Load file paths from config
input_file = config['paths']['output_file']
output_folder = config['paths']['classified_output_folder']

# Read sentences from the file
if not os.path.exists(input_file):
    print(f"File {input_file} not found.")
else:
    with open(input_file, 'r') as file:
        sentences = file.readlines()

    # Initialize lists to store classified sentences
    failure_sentences = []
    countermeasure_sentences = []
    preventive_sentences = []
    unclassified_sentences = []
    multiple_categories_sentences = []

    # Classify each sentence
    for sentence in sentences:
        categories = classify_sentence(sentence)
        # Append the sentence to all relevant categories
        if "failure" in categories:
            failure_sentences.append(sentence)
        if "countermeasure" in categories:
            countermeasure_sentences.append(sentence)
        if "preventive" in categories:
            preventive_sentences.append(sentence)
        if "unclassified" in categories:
            unclassified_sentences.append(sentence)
        
        # Check if a sentence belongs to multiple categories
        if len(categories) > 1:
            multiple_categories_sentences.append(sentence)

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save classified sentences to separate files
    with open(os.path.join(output_folder, 'failure_sentences.txt'), 'w') as file:
        file.writelines(failure_sentences)
    
    with open(os.path.join(output_folder, 'countermeasure_sentences.txt'), 'w') as file:
        file.writelines(countermeasure_sentences)
    
    with open(os.path.join(output_folder, 'preventive_sentences.txt'), 'w') as file:
        file.writelines(preventive_sentences)
    
    with open(os.path.join(output_folder, 'unclassified_sentences.txt'), 'w') as file:
        file.writelines(unclassified_sentences)
    
    with open(os.path.join(output_folder, 'multiple_categories_sentences.txt'), 'w') as file:
        file.writelines(multiple_categories_sentences)

    # Print summary
    print(f"Total sentences: {len(sentences)}")
    print(f"Failure sentences: {len(failure_sentences)}")
    print(f"Countermeasure sentences: {len(countermeasure_sentences)}")
    print(f"Preventive sentences: {len(preventive_sentences)}")
    print(f"Unclassified sentences: {len(unclassified_sentences)}")
    print(f"Sentences in multiple categories: {len(multiple_categories_sentences)}")