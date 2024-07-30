from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json

app = Flask(__name__)
load_dotenv()  # Load environment variables from .env file

# Configure the Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Path to the JSON file where interactions will be saved
INTERACTIONS_FILE = 'interactions.json'

# Function to clean up the response text
def clean_response(response_text):
    terms_to_remove = ["**", "*"]
    for term in terms_to_remove:
        response_text = response_text.replace(term, "")
    return response_text.strip()

# Function to get Generative AI response
def get_generative_ai_response(question):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(question)
    return response.text

# Function to get suitable emoji based on message
def get_suitable_emoji(message):
    emoji_map = {
        "hello": "👋",
        "hi": "👋",
        "thank you": "🙏",
        "goodbye": "👋",
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "love": "❤️",
        "congrats": "🎉",
        "yes": "👍",
        "joke": "😄",
        "no": "👎",
        "sorry": "🙇",
        "wow": "😲",
        "laugh": "😂",
        "comedy": "😂",
        "cool": "😎",
        "help": "🆘",
        "please": "🙏",
        "good night": "🌙",
        "good morning": "🌞",
        "good afternoon": "☀️",
        "good evening": "🌆"
        # Add more mappings as needed
    }
    for key, emoji in emoji_map.items():
        if key in message:
            return emoji
    return None

# Function to save interaction to a JSON file
def save_interaction_to_json(question, response, emoji):
    interaction = {
        'user': question,
        'bot': response,
        'emoji': emoji
    }
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, 'r') as file:
            data = json.load(file)
    else:
        data = []

    data.append(interaction)

    with open(INTERACTIONS_FILE, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.form['question'].lower()
    try:
        if "what is your name" in question or "who are you" in question:
            response_text = "My name is Thikse School Bot."
        else:
            response_text = get_generative_ai_response(question)
            if "google" not in question:
                response_text = response_text.replace("Google", "Thikse")
                response_text = response_text.replace("Gemini", "Thikse")
            response_text = clean_response(response_text)

        # Get a suitable emoji for the message
        emoji = get_suitable_emoji(question)
        
        # Save the interaction to the JSON file
        save_interaction_to_json(question, response_text, emoji)

        return jsonify({'response': response_text, 'emoji': emoji})
    except Exception as e:
        return jsonify({'response': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
