import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    ENV: str = os.getenv("ENV", "development")
    PORT: int = int(os.getenv("PORT", "8080"))

settings = Settings()
