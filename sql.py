from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import google.generativeai as genai
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
load_dotenv()  # Load environment variables from .env file

# Configure the Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Interaction model
class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    response = db.Column(db.Text, nullable=False)
    emoji = db.Column(db.String(10), nullable=True)

# Create the database tables
with app.app_context():
    db.create_all()

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
        "hi":"👋",
        "thank you": "🙏",
        "goodbye": "👋",
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "love": "❤️",
        "congrats": "🎉",
        "yes": "👍",
        "jock":"😄",
        "no": "👎",
        "sorry": "🙇",
        "wow": "😲",
        "laugh": "😂",
        "comedy":"😂",
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
        
        # Save the interaction to the database
        new_interaction = Interaction(question=question, response=response_text, emoji=emoji)
        db.session.add(new_interaction)
        db.session.commit()

        return jsonify({'response': response_text, 'emoji': emoji})
    except Exception as e:
        return jsonify({'response': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
