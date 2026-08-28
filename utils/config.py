from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    gemini_api_key : str = os.getenv("GEMINI_API_KEY","")
    model_name : str = "gemini-2.5-flash"

settings = Settings()