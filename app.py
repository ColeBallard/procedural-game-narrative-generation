from flask import Flask, request, jsonify, send_from_directory, url_for, send_file
from werkzeug.utils import secure_filename
from fpdf import FPDF
import os
import re
import datetime
import requests
import tiktoken
import threading

import prompt_templates as pt

app = Flask(__name__, static_folder='.', static_url_path='')

# ROUTES

@app.route('/', methods=['GET', 'POST'])
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
