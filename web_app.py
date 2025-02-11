"""
Web Application Module

A minimal Flask web app to display the fetched GitHub repository data.
Make sure you have run the main script at least once so that 'output/github_repos.xlsx' exists.
"""

from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)


@app.route("/")
def index():
    excel_path = os.path.join("output", "github_repos.xlsx")
    repos = []
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
        repos = df.to_dict(orient="records")
    return render_template("index.html", repos=repos)


if __name__ == "__main__":
    app.run(debug=True)
