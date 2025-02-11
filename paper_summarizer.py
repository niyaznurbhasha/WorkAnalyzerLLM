#!/usr/bin/env python
import argparse
import os
import logging
import pandas as pd

from transformers import pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_papers(metadata_file, output_file):
    if not os.path.exists(metadata_file):
        logger.error(f"Metadata file {metadata_file} not found.")
        return
    df = pd.read_excel(metadata_file)
    if df.empty:
        logger.error("No papers found in the metadata file.")
        return
    summarizer = pipeline("summarization")
    summaries = []
    for idx, row in df.iterrows():
        title = row.get("title", "No Title")
        summary_text = row.get("summary", "")
        if summary_text:
            try:
                summarized = summarizer(summary_text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
            except Exception as e:
                logger.error(f"Error summarizing paper '{title}': {e}")
                summarized = "Summary not available"
        else:
            summarized = "No summary provided."
        summaries.append({"title": title, "original_summary": summary_text, "generated_summary": summarized})
    
    # Write summaries to a markdown file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Paper Summaries\n\n")
        for item in summaries:
            f.write(f"## {item['title']}\n\n")
            f.write("**Original Summary:**\n\n")
            f.write(f"{item['original_summary']}\n\n")
            f.write("**Generated Summary:**\n\n")
            f.write(f"{item['generated_summary']}\n\n")
            f.write("---\n\n")
    print(f"Paper summaries written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Summarize Research Papers from Metadata")
    parser.add_argument("-m", "--metadata", type=str, default="output/arxiv_papers.xlsx", help="Path to arXiv papers metadata Excel file")
    parser.add_argument("-o", "--output", type=str, default="output/paper_summaries.md", help="Output markdown file for summaries")
    args = parser.parse_args()
    
    summarize_papers(args.metadata, args.output)

if __name__ == "__main__":
    main()
