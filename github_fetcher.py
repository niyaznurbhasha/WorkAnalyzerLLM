"""
GitHub Fetcher Module

This module queries the GitHub API for repositories matching a set of interest keywords.
It supports an optional date filter (only fetching repos updated within the last X days)
and includes modern machine learning and NLP buzzwords in its query.
"""

import os
import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com/search/repositories"


def fetch_github_repos(interests, max_results_per_interest=5, days=None):
    """
    For each interest keyword, fetch GitHub repositories using the GitHub API.
    
    Parameters:
      - interests (list): List of interest keywords.
      - max_results_per_interest (int): Max number of repos per interest.
      - days (int): (Optional) Only fetch repos updated within the last 'days' days.
      
    Returns a list of dictionaries with repo information.
    """
    all_repos = []
    headers = {}
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    for interest in interests:
        # Build query string with date filter if specified
        if days:
            threshold_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
            query = f"{interest} pushed:>={threshold_date}"
        else:
            query = interest

        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": max_results_per_interest
        }
        try:
            response = requests.get(GITHUB_API_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            for item in items:
                repo_info = {
                    "interest": interest,
                    "name": item.get("full_name"),
                    "html_url": item.get("html_url"),
                    "description": item.get("description"),
                    "language": item.get("language"),
                    "last_pushed": item.get("pushed_at")
                }
                all_repos.append(repo_info)
        except Exception as e:
            logger.error(f"Error fetching GitHub repos for interest '{interest}': {e}")

    return all_repos
