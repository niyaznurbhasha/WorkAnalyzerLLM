"""
Papers Fetcher Module

This module queries the arXiv API to fetch the latest research papers related to a list of interest keywords.
It supports an optional date filter (only including papers published within the last X days) and can download PDFs.
"""

import os
import requests
import logging
import xml.etree.ElementTree as ET
from urllib.parse import quote
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"


def fetch_papers(interests, max_results_per_interest=3, download_pdfs=False, output_dir="papers", days=None):
    """
    For each interest, fetch papers from the arXiv API.
    
    Parameters:
      - interests (list): List of interest keywords.
      - max_results_per_interest (int): Max number of papers per interest.
      - download_pdfs (bool): If True, download the paper PDFs.
      - output_dir (str): Directory to save PDFs.
      - days (int): (Optional) Only include papers published in the last 'days' days.
    
    Returns a list of dictionaries with paper metadata.
    """
    papers = []
    threshold = None
    if days:
        threshold = datetime.utcnow() - timedelta(days=days)

    for interest in interests:
        query = quote(interest)
        url = ARXIV_API_URL.format(query=query, max_results=max_results_per_interest)
        try:
            response = requests.get(url)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns).text.strip()
                published_str = entry.find("atom:published", ns).text.strip()
                published_dt = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
                
                # If a threshold is set, skip papers older than the threshold
                if threshold and published_dt < threshold:
                    continue

                summary = entry.find("atom:summary", ns).text.strip()
                pdf_url = None
                for link in entry.findall("atom:link", ns):
                    if link.attrib.get("type") == "application/pdf":
                        pdf_url = link.attrib.get("href")
                        break
                if not pdf_url:
                    entry_id = entry.find("atom:id", ns).text.strip().split("/")[-1]
                    pdf_url = f"http://arxiv.org/pdf/{entry_id}.pdf"

                paper = {
                    "interest": interest,
                    "title": title,
                    "published": published_str,
                    "summary": summary,
                    "pdf_url": pdf_url
                }
                papers.append(paper)

                if download_pdfs:
                    download_pdf(pdf_url, title, output_dir)
        except Exception as e:
            logger.error(f"Error fetching papers for interest '{interest}': {e}")

    return papers


def download_pdf(pdf_url, title, output_dir):
    """
    Download the PDF from the given URL and save it in output_dir using a sanitized title.
    """
    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()
        safe_title = "".join(c if c.isalnum() or c in " -_." else "_" for c in title)[:50]
        pdf_path = os.path.join(output_dir, f"{safe_title}.pdf")
        with open(pdf_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        logger.info(f"Downloaded PDF for paper '{title}'")
    except Exception as e:
        logger.error(f"Error downloading PDF from {pdf_url}: {e}")
