
Conversation with Gemini
import os

import time

import csv

from flask import Flask, jsonify, request, render_template

import undetected_chromedriver as uc

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains

from selenium.common.exceptions import TimeoutException, NoSuchElementException

import anthropic

from dotenv import load_dotenv



# Load environment variables

load_dotenv()



# Initialize Flask app

app = Flask(__name__)



# Define paths for data and attachments

download_folder = os.path.join(os.getcwd(), "data") # Updated path to 'data' folder

attachments_folder = os.path.join(download_folder, "attachments")



# Ensure directories exist

try:

os.makedirs(download_folder, exist_ok=True)

os.makedirs(attachments_folder, exist_ok=True)

except PermissionError as e:

print(f"❌ Permission denied: {e}")

exit(1)



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

options.add_argument("--headless") # Run in headless mode

options.add_argument("--disable-gpu") # Disable GPU acceleration

options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")

return options



# Initialize Chrome driver

def init_driver():

options = setup_chrome_options()

driver = uc.Chrome(options=options)

return driver



# Extract broadcast time and tooltip data

def extract_broadcast_time(driver, row):

try:

broadcast_time_element = row.find_element(By.XPATH, ".//a[contains(@class, 'show_link')]")

broadcast_time = broadcast_time_element.text.strip()



actions = ActionChains(driver)

actions.move_to_element(broadcast_time_element).perform()

time.sleep(2) # Wait for the tooltip to appear



tooltip = row.find_element(By.CSS_SELECTOR, ".hover_table")

tooltip_data = tooltip.text.strip()



full_broadcast_time = f"{broadcast_time}\n{tooltip_data}"

return full_broadcast_time

except Exception as e:

print(f"❌ Failed to extract broadcast time: {e}")

return "N/A"



# Extract data from a specific tab

def extract_tab_data(driver, tab_name, company_filter=None):

try:

wait = WebDriverWait(driver, 10)

tab = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{tab_name}')]")))

tab.click()

print(f"✅ Switched to {tab_name} tab")

time.sleep(5) # Wait for the table to load

except TimeoutException:

print(f"⚠️ {tab_name} tab not found or already selected.")



rows = driver.find_elements(By.XPATH, "//table/tbody/tr")

extracted_data = []



for idx, row in enumerate(rows):

if idx >= 20: # Stop after 20 records

break



columns = row.find_elements(By.TAG_NAME, "td")

if len(columns) < 6:

continue # Skip incomplete rows



symbol = columns[0].text.strip()

company_name = columns[1].text.strip()

subject = columns[2].text.strip()

details = columns[3].text.strip()

broadcast_time = extract_broadcast_time(driver, row)



if company_filter and company_filter.lower() not in company_name.lower():

continue



try:

attachment = columns[5].find_element(By.TAG_NAME, "a")

attachment_link = attachment.get_attribute("href")

except NoSuchElementException:

attachment_link = "No Attachment"



attachment_filename = None

if attachment_link != "No Attachment":

safe_subject = "".join(c if c.isalnum() or c in (" ", "_") else "_" for c in subject)[:50]

attachment_filename = f"{symbol}_{safe_subject}.pdf"

download_attachment_with_selenium(driver, attachment, attachment_filename)



extracted_data.append([symbol, company_name, subject, details, broadcast_time, attachment_filename if attachment_filename else "No Attachment"])



return extracted_data



# Download attachment using Selenium

def download_attachment_with_selenium(driver, attachment_element, filename):

try:

driver.execute_script("arguments[0].scrollIntoView(true);", attachment_element)

time.sleep(1) # Wait for the page to adjust



wait = WebDriverWait(driver, 10)

wait.until(EC.element_to_be_clickable(attachment_element))



driver.execute_script("arguments[0].click();", attachment_element)

print(f"📥 Downloading: {filename}")



time.sleep(10) # Increase the delay to allow for slower downloads

except Exception as e:

print(f"❌ Failed to download {filename}: {e}")



# Load scraped data from CSV

def load_scraped_data(tab_name):

csv_file = os.path.join(download_folder, f"{tab_name.lower()}_announcements.csv")

print(f"📂 CSV file path: {csv_file}") # Debug: Print the CSV file path



data = []

try:

with open(csv_file, "r", encoding="utf-8") as file:

reader = csv.DictReader(file)

for row in reader:

data.append(row)

print(f"✅ Loaded {len(data)} rows from {csv_file}") # Debug: Print the number of rows loaded

except FileNotFoundError:

print(f"❌ CSV file not found: {csv_file}")

except Exception as e:

print(f"❌ Error reading CSV file: {e}")

return data



# AI Querying

@app.route("/query", methods=["POST"])

def query_data():

try:

query = request.json.get("query")

if not query:

return jsonify({"status": "error", "message": "Query is required."}), 400



tab_name = request.json.get("tab", "Equity")

data = load_scraped_data(tab_name)



client = anthropic.Anthropic(api_key=os.getenv("API_KEY"))

response = client.chat.completions.create(

model="claude-3-5-sonnet-20241022",

messages=[

{"role": "system", "content": "You are a helpful assistant that retrieves relevant announcements based on user queries."},

{"role": "user", "content": f"Query: {query}\n\nData: {data}"}

]

)



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



# Flask API endpoint for data extraction

@app.route("/extract", methods=["GET"])

def extract_data():

try:

tab_name = request.args.get("tab", "Equity")

company_filter = request.args.get("company")



driver = init_driver()

nse_url = "https://www.nseindia.com/companies-listing/corporate-filings-announcements"

driver.get(nse_url)

time.sleep(5)



extracted_data = extract_tab_data(driver, tab_name, company_filter)

driver.quit()



if not extracted_data:

print("⚠️ No data extracted. Check the website structure or filters.")

else:

print(f"✅ Extracted {len(extracted_data)} rows of data.")



csv_file = os.path.join(download_folder, f"{tab_name.lower()}_announcements.csv")

try:

with open(csv_file, "w", newline="", encoding="utf-8") as file:

writer = csv.writer(file)

writer.writerow(["Symbol", "Company Name", "Subject", "Details", "Broadcast Date and Time", "Attachment File"])

writer.writerows(extracted_data)

print(f"✅ Data successfully saved to {csv_file}")

except Exception as e:

print(f"❌ Failed to write CSV file: {e}")



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

return render_template("index1.html")



# Run the Flask app

if __name__ == "__main__":

app.run(host="0.0.0.0", port=5000
