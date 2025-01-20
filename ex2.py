from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask_cors import CORS



# Load API key from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')  # Ensure your .env file contains this variable

# Configure the genai module
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="gemini-pro")

# Setup Flask app and SQLite database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# SQLite model for storing chat history
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.String(200), nullable=False)
    response_text = db.Column(db.String(500), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    
    # Generate content using the generative model
    response = model.generate_content(user_input)
    response_text = response.text

    # Save chat history to SQLite database
    new_chat = ChatHistory(user_input=user_input, response_text=response_text)
    db.session.add(new_chat)
    db.session.commit()

    return jsonify({"response": response_text})
CORS(app)

if __name__ == '__main__':
    app.run(debug=True)
