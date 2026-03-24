import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///contact.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    TO_EMAIL = os.getenv("TO_EMAIL")