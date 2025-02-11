"""
Advanced NLP Module

This module leverages spaCy to perform more advanced extraction of interest keywords.
It uses the spaCy pipeline (with the 'en_core_web_sm' model) to extract noun chunks 
and named entities from the aggregated text, then matches them against candidate keywords.
"""

import spacy

# Load the spaCy English model (ensure you've run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")


def extract_keywords_advanced(text, candidate_keywords):
    """
    Use spaCy to process the text and extract noun chunks and named entities that
    match candidate keywords.
    
    Parameters:
      - text (str): The aggregated text to analyze.
      - candidate_keywords (list): A list of candidate keywords to search for.
    
    Returns a list of matched keywords.
    """
    doc = nlp(text)
    extracted = set()

    # Extract noun chunks
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        for keyword in candidate_keywords:
            if keyword in chunk_text:
                extracted.add(keyword)

    # Extract named entities
    for ent in doc.ents:
        ent_text = ent.text.lower().strip()
        for keyword in candidate_keywords:
            if keyword in ent_text:
                extracted.add(keyword)
    return list(extracted)
