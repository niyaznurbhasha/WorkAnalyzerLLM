#!/usr/bin/env python
import argparse
import os
import logging
import itertools

import networkx as nx
import matplotlib.pyplot as plt

from nlp_analyzer import extract_interests_from_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_cooccurrence_graph(folders):
    cooccurrences = {}
    topics_set = set()
    for folder in folders:
        if not os.path.isdir(folder):
            logger.warning(f"Folder not found: {folder}")
            continue
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".txt") or file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            text = f.read()
                        topics = extract_interests_from_text(text)
                        topics_set.update(topics)
                        # Update co-occurrence counts for each unique pair in the file
                        for pair in itertools.combinations(set(topics), 2):
                            sorted_pair = tuple(sorted(pair))
                            cooccurrences[sorted_pair] = cooccurrences.get(sorted_pair, 0) + 1
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {e}")
    return cooccurrences, topics_set

def visualize_graph(cooccurrences, topics_set):
    G = nx.Graph()
    # Add nodes
    for topic in topics_set:
        G.add_node(topic)
    # Add edges with weights
    for (topic1, topic2), weight in cooccurrences.items():
        G.add_edge(topic1, topic2, weight=weight)
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    plt.figure(figsize=(10, 10))
    weights = [G[u][v]['weight'] for u, v in G.edges()]
    nx.draw(G, pos, with_labels=True, node_color="skyblue", edge_color="gray", 
            width=[w * 0.5 for w in weights], font_size=10)
    plt.title("Knowledge Graph of Topics")
    output_path = "output/knowledge_graph.png"
    plt.savefig(output_path)
    plt.show()
    print(f"Knowledge graph saved as {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Build a Knowledge Graph from Text Files")
    parser.add_argument("-f", "--folders", nargs="+", required=True, help="Folders to analyze")
    args = parser.parse_args()
    
    cooccurrences, topics_set = build_cooccurrence_graph(args.folders)
    if not topics_set:
        logger.info("No topics found in the provided folders.")
        return
    visualize_graph(cooccurrences, topics_set)

if __name__ == "__main__":
    main()
