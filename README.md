# Overview

This project is a web service that scrapes NSE (National Stock Exchange) data and provides insights using OpenAI's LLM. The application is built using Flask and is deployed on Render. It features a web interface where users can input queries and receive processed results.

## Project Structure

NSE_scrapping/
```
│── new1.py # Main Flask application
│── templates/ │ └── index1.html # Frontend interface
│── data/ │ └── equityannouncements.csv # Stored scraped data
│── requirements.txt # Dependencies
│── Procfile # Deployment instructions
│── .env # API keys and environment variables
```

## Features

- Scrapes real-time equity announcements from NSE.
- Uses OpenAI API for intelligent query handling.
- Provides a simple web-based interface for user interaction.
- Deployed on Render for live access.

   
# Setup

Configure environment variables
Create a .env file and add the following:
Run the Flask application
Access the Web Interface

Open a browser and navigate to http://127.0.0.1:5000/

# Deployment on Render

Extract the repo to Render
Build and deploy the application
Copy the generated link
Navigate to the link to use the service

## Deployment Process

1. Extract the repository to [Render](https://render.com/).
2. Render builds and deploys the project.
3. After successful deployment, a link is generated.
4. Navigating to the link opens the interface where users can enter queries.

# Technologies Used
```
Python (Flask, selenium,Pandas, Requests)
HTML, CSS, JavaScript (Frontend)
OpenAI API (For query handling)
Render (Deployment)
```
# Future Enhancements
Add authentication for API usage.
Improve data visualization.
Automate scraping at regular intervals.

## Connect with Me

If you have any questions or suggestions, feel free to reach out:

- **Email**:hanitharajeswari9@gmail.com

# Deployment on render
![Screenshot 2025-03-17 215310](https://github.com/user-attachments/assets/41d24d17-092c-45f7-9e4a-c94cf24b2591)
# Web Scrapping on dynamic website on postman
![ScreenRecording2025-03-17202641-ezgif com-video-to-gif-converter gif](https://github.com/user-attachments/assets/2859aef8-ae9b-4b08-bb90-dc7735e9e044)



🚀 Happy Coding!
