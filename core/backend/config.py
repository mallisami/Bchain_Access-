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

    DEMO_MODE = os.getenv('DEMO_MODE', 'true').lower() == 'true'

    PATIENT_PRIVATE_KEY = os.getenv('PATIENT_PRIVATE_KEY', '')
    if not PATIENT_PRIVATE_KEY:
        if DEMO_MODE:
            print("=" * 80)
            print("DEVELOPMENT ONLY:")
            print("Known Hardhat test key with no production value.")
            print("Never use this key on a public, shared, or production network.")
            print("=" * 80)
            PATIENT_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        else:
            raise RuntimeError(
                "PATIENT_PRIVATE_KEY environment variable is required in production mode."
            )
