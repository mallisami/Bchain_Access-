import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    WEB3_PROVIDER_URL = os.getenv('WEB3_PROVIDER_URL', 'http://localhost:8545')
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')
    CONTRACT_ABI_PATH = os.getenv('CONTRACT_ABI_PATH', '')
    PATIENT_PRIVATE_KEY = os.getenv('PATIENT_PRIVATE_KEY', '')
