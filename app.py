import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# Configure the Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# Function to generate bot's starting message based on selected language
def get_welcome_message(language):
    if language == 'hi':
        welcome_message = "नमस्ते, सखी फाइनेंस में आपका स्वागत है। मैं आपकी कैसे मदद कर सकती हूँ?"
    else:
        welcome_message = "Hello, welcome to Sakhi Finance. How may I help you?"
    
    return welcome_message

def generate_response(user_input, language):
    system_instruction = """
    You are a chatbot designed to empower rural women in India with financial knowledge. 
    Your role is to answer questions about saving money, budgeting, investment options, and other financial topics. 
    Many users may not be familiar with financial concepts, so your responses should be simple, clear, and helpful. 
    Use their regional language when responding.
    """

    generation_config = {
        "temperature": 0.5,  # Adjusted for better response variety
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 800,  # To keep responses brief
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )

    history = [{"role": "user", "parts": [user_input]}]
    chat_session = model.start_chat(history=history)
    response = chat_session.send_message(user_input)
    model_response = response.text.strip()

    # Return the response in a simple, line-by-line format
    response_lines = model_response.split("\n")
    
    # Prepare the response as plain text without any formatting tags
    if language == 'hi':
        response_text = "\n".join([f"• {line.strip()}" for line in response_lines if line.strip()])
    else:
        response_text = "\n".join([f"- {line.strip()}" for line in response_lines if line.strip()])

    return {
        'welcome_message': get_welcome_message(language),  # Include the welcome message
        'response': response_text,  # Returning plain text response
        'speech': model_response  # Text-to-speech integration
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.form
    user_input = data.get('user_input')
    language = data.get('language')

    response = generate_response(user_input, language)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
