from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
