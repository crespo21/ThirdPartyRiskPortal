import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tprm.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    # AZURE_APP_INSIGHTS_KEY = os.getenv("AZURE_APP_INSIGHTS_KEY", "")

settings = Settings()
