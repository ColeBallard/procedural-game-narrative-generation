import os
import subprocess
import yaml
from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import shutil
import logging
from .orm import Base

def createApp():
    app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # Load environment variables
    load_dotenv()

    # Load YAML configuration
    config_path = os.path.join(app.root_path, 'config', 'game_config.yaml')
    with open(config_path, 'r') as config_file:
        config_data = yaml.safe_load(config_file)

    # Store the configuration in the app config
    app.config.update(config_data)

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
    Base.metadata.create_all(engine)

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)

    # Store the session factory in the app config
    app.config['SESSION_FACTORY'] = Session

    # Register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    logging.info("App creation complete")
    
    return app
