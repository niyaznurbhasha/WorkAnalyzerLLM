#!/usr/bin/env python
import argparse
import os
import time
import datetime
import logging
import itertools

import matplotlib.pyplot as plt
import pandas as pd

from nlp_analyzer import extract_interests_from_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_time_and_topics(folders):
    records = []
    for folder in folders:
        if not os.path.isdir(folder):
            logger.warning(f"Folder not found: {folder}")
            continue
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".txt") or file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        mod_time = os.path.getmtime(file_path)
                        mod_date = datetime.datetime.fromtimestamp(mod_time).date()
                        with open(file_path, "r", encoding="utf-8") as f:
                            text = f.read()
                        topics = extract_interests_from_text(text)
                        for topic in topics:
                            records.append({"date": mod_date, "topic": topic})
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {e}")
    return records

def generate_report(records):
    df = pd.DataFrame(records)
    if df.empty:
        logger.info("No records found.")
        return
    pivot = df.groupby(["date", "topic"]).size().unstack(fill_value=0)
    ax = pivot.plot(kind="bar", stacked=True, figsize=(12,6))
    plt.xlabel("Date")
    plt.ylabel("Number of Files")
    plt.title("Files by Topic and Date")
    plt.tight_layout()
    output_chart = "output/time_analysis.png"
    plt.savefig(output_chart)
    plt.show()
    output_csv = "output/time_analysis.csv"
    df.to_csv(output_csv, index=False)
    print(f"Report generated: {output_chart} and {output_csv}")

def main():
    parser = argparse.ArgumentParser(description="Time Analysis and Topic Tracking from Text Files")
    parser.add_argument("-f", "--folders", nargs="+", required=True, help="Folders to analyze")
    args = parser.parse_args()
    
    records = analyze_time_and_topics(args.folders)
    generate_report(records)

if __name__ == "__main__":
    main()
