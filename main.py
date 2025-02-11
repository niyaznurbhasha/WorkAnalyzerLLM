#!/usr/bin/env python
"""
Main entry point for the Advanced NLP/LLM Intelligent Document Analyzer & Aggregator.
This project extracts your interests from personal files, then fetches 
GitHub repositories and arXiv research papers that match those interests.
"""

import argparse
import os
import logging

from nlp_analyzer import analyze_folders
from github_fetcher import fetch_github_repos
from papers_fetcher import fetch_papers
from utils import safe_mkdir

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze your personal documents & ChatGPT history to fetch "
                    "relevant GitHub repositories and research papers based on your interests."
    )
    parser.add_argument(
        "-f", "--folders",
        nargs="+",
        required=True,
        help="List of folder paths to analyze (e.g., Documents, ChatGPT history folder, etc.)"
    )
    parser.add_argument(
        "-m", "--manual_interests",
        type=str,
        default="",
        help="(Optional) Path to a text file that contains additional manual interests."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="(Optional) Only consider files and online content from the last X days."
    )
    parser.add_argument(
        "--advanced_nlp",
        action="store_true",
        help="Use advanced NLP extraction with spaCy."
    )
    parser.add_argument(
        "--download_pdfs",
        action="store_true",
        help="If set, download PDFs of the research papers from arXiv."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Create output folders if they do not exist
    safe_mkdir("output")
    safe_mkdir("papers")

    # Analyze the provided folders to extract interests (with optional advanced NLP and date filtering)
    logger.info("Analyzing folders for interests...")
    extracted_interests = analyze_folders(args.folders, advanced=args.advanced_nlp, days=args.days)
    logger.info(f"Extracted interests: {extracted_interests}")

    # If a manual interests file is provided, add its contents
    if args.manual_interests and os.path.isfile(args.manual_interests):
        with open(args.manual_interests, "r", encoding="utf-8") as f:
            manual_text = f.read()
        # We always use basic extraction for the manual text
        from nlp_analyzer import extract_interests_from_text
        manual_interests = extract_interests_from_text(manual_text)
        logger.info(f"Manual interests found: {manual_interests}")
        all_interests = list(set(extracted_interests + manual_interests))
    else:
        all_interests = extracted_interests

    if not all_interests:
        logger.warning("No interests were extracted. Please check your input folders or provide a manual interests file.")
        return

    # Fetch GitHub repositories for the interests (with optional days filter)
    logger.info("Fetching GitHub repositories...")
    github_results = fetch_github_repos(all_interests, max_results_per_interest=5, days=args.days)
    logger.info(f"Fetched {len(github_results)} repositories from GitHub.")

    # Save GitHub repos to an Excel file
    excel_path = os.path.join("output", "github_repos.xlsx")
    df = pd.DataFrame(github_results)
    df.to_excel(excel_path, index=False)
    logger.info(f"GitHub repository data saved to {excel_path}")

    # Fetch research papers from arXiv for the interests (with optional days filter)
    logger.info("Fetching research papers from arXiv...")
    papers = fetch_papers(all_interests, max_results_per_interest=3,
                           download_pdfs=args.download_pdfs, output_dir="papers", days=args.days)
    logger.info(f"Fetched {len(papers)} research papers from arXiv.")

    # Save arXiv papers metadata to an Excel file (for use with the paper summarizer)
    arxiv_excel_path = os.path.join("output", "arxiv_papers.xlsx")
    df_papers = pd.DataFrame(papers)
    df_papers.to_excel(arxiv_excel_path, index=False)
    logger.info(f"arXiv papers metadata saved to {arxiv_excel_path}")

if __name__ == "__main__":
    main()
