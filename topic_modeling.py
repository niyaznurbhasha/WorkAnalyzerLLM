#!/usr/bin/env python
import argparse
import os
import logging
import time

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import gensim
from gensim import corpora

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Make sure NLTK resources are available
nltk.download('punkt')
nltk.download('stopwords')

def load_text_from_folders(folders):
    aggregated_texts = []
    for folder in folders:
        if os.path.isdir(folder):
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.txt') or file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                aggregated_texts.append(f.read())
                        except Exception as e:
                            logger.error(f"Error reading {file_path}: {e}")
    return aggregated_texts

def preprocess_texts(texts):
    stop_words = set(stopwords.words('english'))
    processed_texts = []
    for text in texts:
        tokens = word_tokenize(text.lower())
        tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
        processed_texts.append(tokens)
    return processed_texts

def perform_topic_modeling(texts, num_topics=5, passes=10):
    processed_texts = preprocess_texts(texts)
    dictionary = corpora.Dictionary(processed_texts)
    corpus = [dictionary.doc2bow(text) for text in processed_texts]
    lda_model = gensim.models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=passes)
    topics = lda_model.print_topics(num_words=5)
    return topics

def main():
    parser = argparse.ArgumentParser(description="Topic Modeling on Aggregated Text Files")
    parser.add_argument("-f", "--folders", nargs="+", required=True, help="Folders to aggregate text from")
    parser.add_argument("--num_topics", type=int, default=5, help="Number of topics to extract")
    args = parser.parse_args()
    
    texts = load_text_from_folders(args.folders)
    if not texts:
        logger.error("No text files found in the provided folders.")
        return
    
    topics = perform_topic_modeling(texts, num_topics=args.num_topics)
    print("Extracted Topics:")
    for topic in topics:
        print(topic)

if __name__ == "__main__":
    main()
