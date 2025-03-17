from flask import Flask, jsonify, request, render_template
import os
import time
import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Define paths for data and attachments
download_folder = "C:/Users/HANITHA/Downloads/NSE_Announcements"
attachments_folder = os.path.join(download_folder, "attachments")

# Ensure directories exist
os.makedirs(download_folder, exist_ok=True)
os.makedirs(attachments_folder, exist_ok=True)

# Set up Chrome options
def setup_chrome_options():
    options = uc.ChromeOptions()
    prefs = {
        "download.default_directory": attachments_folder,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
    return options

# Initialize Chrome driver
def init_driver():
    options = setup_chrome_options()
    driver = uc.Chrome(options=options)
    return driver

# Extract broadcast time and tooltip data
def extract_broadcast_time(driver, row):
    """Extracts broadcast time and tooltip data from a table row."""
    try:
        # Locate the broadcast time element
        broadcast_time_element = row.find_element(By.XPATH, ".//a[contains(@class, 'show_link')]")
        broadcast_time = broadcast_time_element.text.strip()

        # Simulate a hover action to make the tooltip visible
        actions = ActionChains(driver)
        actions.move_to_element(broadcast_time_element).perform()
        time.sleep(2)  # Wait for the tooltip to appear

        # Extract the tooltip data
        tooltip = row.find_element(By.CSS_SELECTOR, ".hover_table")
        tooltip_data = tooltip.text.strip()

        # Combine broadcast time and tooltip data
        full_broadcast_time = f"{broadcast_time}\n{tooltip_data}"
        return full_broadcast_time
    except Exception as e:
        print(f"❌ Failed to extract broadcast time: {e}")
        return "N/A"

# Extract data from a specific tab
def extract_tab_data(driver, tab_name, company_filter=None):
    """Extracts announcements from the specified tab, including attachments and broadcast time."""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Click on the specified tab (Equity or SME)
        tab = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{tab_name}')]")))
        tab.click()
        print(f"✅ Switched to {tab_name} tab")
        time.sleep(5)  # Wait for the table to load
    except TimeoutException:
        print(f"⚠️ {tab_name} tab not found or already selected.")

    # Extract table rows
    rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
    extracted_data = []

    # Loop through the rows, limit to 20 records
    for idx, row in enumerate(rows):
        if idx >= 20:  # Stop after 20 records
            break

        columns = row.find_elements(By.TAG_NAME, "td")
        if len(columns) < 6:
            continue  # Skip incomplete rows

        # Extract text data safely
        symbol = columns[0].text.strip()
        company_name = columns[1].text.strip()
        subject = columns[2].text.strip()
        details = columns[3].text.strip()

        # Extract broadcast time and tooltip data
        broadcast_time = extract_broadcast_time(driver, row)

        # Apply company filter if provided
        if company_filter and company_filter.lower() not in company_name.lower():
            continue

        # Extract attachment link safely
        try:
            attachment = columns[5].find_element(By.TAG_NAME, "a")
            attachment_link = attachment.get_attribute("href")
        except NoSuchElementException:
            attachment_link = "No Attachment"  # Handle missing links

        # Download and save attachment
        attachment_filename = None
        if attachment_link != "No Attachment":
            # Generate a unique filename
            safe_subject = "".join(c if c.isalnum() or c in (" ", "_") else "_" for c in subject)[:50]
            attachment_filename = f"{symbol}_{safe_subject}.pdf"
            download_attachment_with_selenium(driver, attachment, attachment_filename)

        extracted_data.append([symbol, company_name, subject, details, broadcast_time, attachment_filename if attachment_filename else "No Attachment"])

    return extracted_data

# Download attachment using Selenium
def download_attachment_with_selenium(driver, attachment_element, filename):
    """Downloads the attachment file using Selenium."""
    try:
        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", attachment_element)
        time.sleep(1)  # Wait for the page to adjust

        # Wait until the element is clickable
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable(attachment_element))

        # Use JavaScript to click the element
        driver.execute_script("arguments[0].click();", attachment_element)
        print(f"📥 Downloading: {filename}")

        # Wait for the file to download (adjust time to 100 seconds)
        time.sleep(10)  # Increase the delay to allow for slower downloads
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")

# Load scraped data from CSV
def load_scraped_data(tab_name):
    """Loads scraped data from the CSV file."""
    csv_file = os.path.join(download_folder, f"{tab_name.lower()}_announcements.csv")
    data = []
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

# AI Querying (Part 2)
@app.route("/query", methods=["POST"])
def query_data():
    try:
        # Get the user's natural language query
        query = request.json.get("query")
        if not query:
            return jsonify({"status": "error", "message": "Query is required."}), 400

        # Get the tab name (default to Equity)
        tab_name = request.json.get("tab", "Equity")

        # Load the scraped data from CSV
        data = load_scraped_data(tab_name)

        # Use OpenAI's GPT to interpret the query and retrieve relevant data
        client = OpenAI(api_key=os.getenv("API_KEY"))  # Load API key from environment
        response = client.chat.completions.create(
            model="gpt-4",  # Use GPT-4 or any other suitable model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that retrieves relevant announcements based on user queries."},
                {"role": "user", "content": f"Query: {query}\n\nData: {data}"}
            ]
        )

        # Extract the AI's response
        result = response.choices[0].message.content

        return jsonify({
            "status": "success",
            "query": query,
            "result": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Flask API endpoint for data extraction (Part 1)
@app.route("/extract", methods=["GET"])
def extract_data():
    try:
        # Get query parameters
        tab_name = request.args.get("tab", "Equity")  # Default to Equity tab
        company_filter = request.args.get("company")  # Optional company filter

        # Initialize the Chrome driver
        driver = init_driver()

        # Open NSE website
        nse_url = "https://www.nseindia.com/companies-listing/corporate-filings-announcements"
        driver.get(nse_url)
        time.sleep(5)  # Allow time for the page to load

        # Extract data for the specified tab
        extracted_data = extract_tab_data(driver, tab_name, company_filter)

        # Close the driver
        driver.quit()

        # Save extracted data to CSV
        csv_file = os.path.join(download_folder, f"{tab_name.lower()}_announcements.csv")
        with open(csv_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Symbol", "Company Name", "Subject", "Details", "Broadcast Date and Time", "Attachment File"])
            writer.writerows(extracted_data)

        print(f"✅ Data successfully saved to {csv_file}")

        # Return the extracted data as JSON
        return jsonify({
            "status": "success",
            "message": "Data extracted and saved successfully.",
            "data": extracted_data,
            "csv_file": csv_file
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Serve the frontend interface
@app.route("/")
def index():
    return "Welcome to the NSE Scraping API!"

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
