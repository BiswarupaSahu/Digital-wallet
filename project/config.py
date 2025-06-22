import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/wallet_db')
    CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY', '')
    CURRENCY_API_URL = 'https://currencyapi.com/api/v3/latest'