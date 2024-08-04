import os
import subprocess
import re
import datetime
import threading

import yaml
import requests
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from mysql.connector import pooling
from flask import Flask, request, jsonify, send_from_directory, url_for, send_file
from werkzeug.utils import secure_filename
from fpdf import FPDF
import tiktoken

import prompt_templates as pt

app = Flask(__name__, static_folder='.', static_url_path='')

# Load environment variables
load_dotenv()

# Database configuration
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_NAME"),
    "port": os.getenv("DB_PORT")
}

# Initialize connection pool
pool = pooling.MySQLConnectionPool(
    pool_name = "pgng_pool",
    pool_size = 5,
    **db_config
)

def createDB():
    # Database configuration
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB_NAME"),
        "port": os.getenv("DB_PORT")
    }

    # Create the connection string
    connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

    # Create the SQLAlchemy engine
    engine = create_engine(connection_string)

    # Generate ORM models
    subprocess.run(["sqlacodegen", connection_string, "--outfile", "orm.py"])

# ROUTES

@app.route('/', methods=['GET', 'POST'])
def index():
    return send_from_directory('.', 'index.html')

@app.route('/config')
def get_config():
    # Determine the path to the YAML file in the root directory
    yaml_path = os.path.join(app.root_path, 'game_config.yaml')
    
    # Read and parse the YAML file
    with open(yaml_path, 'r') as file:
        config_data = yaml.safe_load(file)
        
    # Return the data as JSON
    return jsonify(config_data)

if __name__ == '__main__':
    createDB()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
