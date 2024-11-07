import secrets
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, jsonify
from langchain_community.chat_models import ChatOllama

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Dictionary to store API keys along with their associated model
api_keys = {}

available_models = {
    "llama3.1": "Llama 3.1 Model",
    "mistral-nemo": "Mistral Nemo Model",
    "nemotron-mini": "Nemetron Mini Model",
    "llama2": "Llama 2 Model"
}

# Function to create a ChatOllama instance based on model selection
def get_chat_model(model_name):
    return ChatOllama(model_name=model_name)

# Function to create an API key associated with a model
def generate_api_key(model_name):
    api_key = secrets.token_hex(16)  # Generates a 32-character hexadecimal API key
    api_keys[api_key] = model_name  # Store the model name with the generated API key
    return api_key

# Route to render the frontend with available models
@app.route('/')
def index():
    return render_template('index.html', models=available_models.keys(), api_keys=api_keys)

# Route to generate API key for a specific model
@app.route('/generate_api_key', methods=['POST'])
def generate_api_key_route():
    model_name = request.json.get("model")
    if model_name not in available_models:
        return jsonify({"error": "Model not available"}), 400
    
    # Generate and store the API key with the associated model
    new_key = generate_api_key(model_name)
    return jsonify({"api_key": new_key, "model": model_name})

# Route to delete an API key
@app.route('/delete_api_key', methods=['POST'])
def delete_api_key_route():
    api_key = request.json.get("api_key")
    if api_key not in api_keys:
        return jsonify({"error": "API key not found"}), 404

    del api_keys[api_key]  # Delete the API key
    return jsonify({"message": "API key deleted successfully"})

# Route to get a response from the selected model using the API key
@app.route('/get_response', methods=['POST'])
def get_response():
    # Check if request contains a valid API key
    api_key = request.headers.get("Authorization")
    if api_key not in api_keys:
        return jsonify({"error": "Invalid API key"}), 403
    
    # Ensure the API key is associated with the requested model
    requested_model = request.json.get("model")
    if api_keys[api_key] != requested_model:
        return jsonify({"error": "API key does not have access to the requested model"}), 403

    # Get user input and load the selected model
    user_input = request.json.get("message")
    chat_model = get_chat_model(requested_model)
    messages = [{"role": "user", "content": user_input}]
    
    response = chat_model.invoke(messages)
    return jsonify({"response": response.content})

if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')
