# NSE Web Scraping and AI Query Handling

This project is a web-based application that scrapes equity announcements from the NSE website, stores the data in a CSV file, and allows users to interact with it using OpenAI's GPT model. The project is built using Flask for the backend and deployed on Render.

## Features
- **Web Scraping**: Extracts equity announcements from the NSE website.
- **Data Storage**: Stores scraped data in `equityannouncements.csv`.
- **AI-Powered Query Handling**: Uses OpenAI's GPT model to respond to user queries about the data.
- **Web Interface**: Provides a simple frontend (`index1.html`) for user interaction.
- **Deployment**: Hosted on Render for live access.

## Project Structure
```
NSE_scrapping/
│── new1.py             # Main Flask application
│── index1.html         # Frontend interface
│── requirements.txt    # Dependencies
│── Procfile            # Deployment instructions
│── .env                # API keys and environment variables
│── equityannouncements.csv  # Stored scraped data
```

## Setup and Installation
1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/NSE_scrapping.git
   cd NSE_scrapping
   ```

2. **Create a Virtual Environment** (Optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   - Create a `.env` file and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

5. **Run the Application Locally**
   ```bash
   python new1.py
   ```
   Open `http://127.0.0.1:5000` in your browser.

## Deployment on Render
1. Extract the repo to Render.
2. Render builds and deploys automatically.
3. Once deployed, copy the generated link and navigate to open the web interface.

## Usage
- Open the web interface.
- Enter queries about NSE equity announcements.
- Receive AI-generated responses powered by OpenAI's GPT model.

## Contributing
Feel free to fork and improve the project! Pull requests are welcome.

## License
This project is licensed under the MIT License.
