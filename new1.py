import os 
import time
import csv
from flask import Flask, jsonify, request, render_template
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Define paths for data
download_folder = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(download_folder, exist_ok=True)

# Initialize Claude API client
claude_client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

def load_scraped_data(tab_name):
    """Loads scraped data from the CSV file."""
    csv_file = os.path.join(download_folder, f"{tab_name.lower()}_announcements.csv")
    data = []
    try:
        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except FileNotFoundError as e:
        print(f"❌ File not found: {csv_file}")
        raise e
    return data

@app.route("/query", methods=["POST"])
def query_data():
    try:
        query = request.json.get("query")
        if not query:
            return jsonify({"status": "error", "message": "Query is required."}), 400

        tab_name = request.json.get("tab", "Equity")
        data = load_scraped_data(tab_name)
        
        # Use Claude 3.5 Sonnet for querying
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "system", "content": "You are an AI that retrieves relevant financial announcements based on user queries."},
                {"role": "user", "content": f"Query: {query}\n\nData: {data}"}
            ]
        )
        
        result = response.content[0].text
        
        return jsonify({
            "status": "success",
            "query": query,
            "result": result
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
