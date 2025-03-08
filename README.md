Voice-Controlled Web Navigation for Visually Impaired Users

This project provides a voice-controlled web navigation assistant designed for visually impaired users. It enables users to browse websites, interact with web elements, and extract content using speech commands.

Features

Voice Recognition: Uses Vosk for speech-to-text conversion.

Text-to-Speech (TTS): Uses pyttsx3 to read content aloud.

Web Scraping: Extracts page content using BeautifulSoup.

Dynamic Web Interaction: Navigates and interacts with websites via Selenium.

ChatGPT Integration: Uses OpenAI's API for intelligent responses.

Cookie Handling & Popup Removal: Automatically manages cookie consent and removes overlays.

Installation

Prerequisites

Ensure you have Python installed and install the required dependencies:

pip install pyttsx3 vosk pyaudio openai beautifulsoup4 requests selenium

Setup

Download and set up the Vosk model for speech recognition.

Install Google Chrome and the corresponding Chrome WebDriver.

Replace 'your gpt api' with your actual OpenAI API key.

Usage

Run the script:

python script.py

Commands:

Speak to navigate or interact with content.

Use phrases like "Go to [section]" to move within a webpage.

Ask questions about the page content.

Say "Exit" to close the session.

Future Improvements

Support for additional voice commands.

Enhanced AI-based navigation.

Multi-language support.

License

This project is licensed under the MIT License.

