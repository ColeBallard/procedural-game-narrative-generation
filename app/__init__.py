import os
import subprocess
import yaml
from dotenv import load_dotenv
from flask import Flask
from mysql.connector import pooling
from sqlalchemy import create_engine
import shutil
import logging

def createApp():
    app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

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

    # Create the connection string
    connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

    # Create the SQLAlchemy engine
    engine = create_engine(connection_string)

    # Register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    logging.info("App creation complete")
    
    return app
