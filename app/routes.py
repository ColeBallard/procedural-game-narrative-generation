import os
import yaml
import requests
from flask import Blueprint, jsonify, render_template, current_app, request

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main.route('/config')
def get_config():
    # Determine the path to the YAML file in the config directory
    yaml_path = os.path.join(current_app.root_path, '..', 'config', 'game_config.yaml')
    
    # Read and parse the YAML file
    with open(yaml_path, 'r') as file:
        config_data = yaml.safe_load(file)
        
    # Return the data as JSON
    return jsonify(config_data)

@main.route('/api/settings', methods=['GET'])
def get_settings():
    # Retrieve settings from database
    settings = {}  # This would be your actual call to fetch settings
    return jsonify(settings)

@main.route('/api/settings/save', methods=['POST'])
def save_settings():
    # Save settings to database
    return jsonify(status="success")

@main.route('/test-openai-key', methods=['POST'])
def test_openai_key():
    api_key = request.json['api_key']
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', json=body, headers=headers)
    if response.ok:
        return jsonify({'valid': True, 'message': 'API key is valid.'})
    else:
        return jsonify({'valid': False, 'message': 'API key is not valid.', 'error': response.json()}), 400

