from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Database
    database_url: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    runwayml_api_key: str | None = None
    huggingface_api_key: str | None = None
    # Google Gemini API
    google_api_key: str | None = None
    google_application_credentials: str | None = None
    app_name: str = "Domain Chatbot"
    debug: bool = True
    next_public_api_url: str  # Add this line

    class Config:
        env_file = ".env"
        case_sensitive = False

# Example of checking the environment variable
# print(f"NEXT_PUBLIC_API_URL: {os.environ.get('NEXT_PUBLIC_API_URL')}")

settings = Settings()