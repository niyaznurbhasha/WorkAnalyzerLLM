"""
NLP Analyzer Module

This module contains functions to analyze text files in specified folders
and extract interest keywords that are highly relevant in modern NLP/LLM 
and machine learning job markets. It supports both basic keyword matching 
and advanced NLP extraction (using spaCy).

Candidate keywords (in lowercase) include:

    transformer, attention, neural network, deep learning, NLP, LLM, BERT, GPT, 
    prompt engineering, zero-shot, few-shot, transfer learning, sentiment analysis, 
    named entity recognition, summarization, and many more.
"""

import os
import re
import logging
import time

logger = logging.getLogger(__name__)

# Pre-defined candidate keywords (in lowercase)
CANDIDATE_KEYWORDS = [
    "machine learning", "deep learning", "neural network", "transformer", "attention",
    "nlp", "natural language processing", "llm", "large language model", "bert", "gpt",
    "roberta", "xlnet", "t5", "text generation", "sequence modeling", "prompt engineering",
    "zero-shot", "few-shot", "reinforcement learning", "data science", "python",
    "scikit-learn", "tensorflow", "pytorch", "feature engineering", "data preprocessing",
    "classification", "regression", "clustering", "dimensionality reduction", "autoencoder",
    "gan", "transfer learning", "explainable ai", "sentiment analysis", "entity recognition",
    "named entity recognition", "question answering", "summarization", "topic modeling", "lstm",
    "rnn", "cnn", "graph neural network", "self-supervised learning", "contrastive learning",
    "embedding", "vectorization", "api integration", "big data", "cloud computing", "scalable",
    "distributed computing"
]


def extract_interests_from_text(text):
    """
    Given a text string, searches for candidate keywords using regex and returns a list of matches.
    """
    found_keywords = set()
    lower_text = text.lower()
    for keyword in CANDIDATE_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, lower_text):
            found_keywords.add(keyword)
    return list(found_keywords)


def analyze_folders(folders, advanced=False, days=None):
    """
    Analyze all text files (.txt and .md) in the provided folder paths.
    
    Parameters:
      - advanced (bool): If True, use advanced NLP extraction via spaCy.
      - days (int): If provided, only include files modified in the last 'days' days.
      
    Returns a deduplicated list of interest keywords found across all files.
    """
    aggregated_text = ""
    now = time.time()
    for folder in folders:
        if not os.path.isdir(folder):
            logger.warning(f"Folder not found: {folder}")
            continue

        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".txt") or file.endswith(".md"):
                    file_path = os.path.join(folder, file)
                    # If days is specified, only include files modified within that range
                    if days:
                        mod_time = os.path.getmtime(file_path)
                        if (now - mod_time) > days * 86400:
                            continue
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        aggregated_text += "\n" + content
                    except Exception as e:
                        logger.error(f"Error reading {file_path}: {e}")

    if advanced:
        try:
            from advanced_nlp import extract_keywords_advanced
            logger.info("Using advanced NLP extraction via spaCy...")
            return extract_keywords_advanced(aggregated_text, CANDIDATE_KEYWORDS)
        except Exception as e:
            logger.error("Advanced NLP extraction failed, falling back to basic extraction: " + str(e))
    return extract_interests_from_text(aggregated_text)
