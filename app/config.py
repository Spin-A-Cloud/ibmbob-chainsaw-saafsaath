"""
Centralised configuration loaded once from environment variables / .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # WhatsApp Business Cloud API
    whatsapp_verify_token: str
    whatsapp_api_token: str
    whatsapp_phone_number_id: str

    # Instagram Graph API
    instagram_access_token: str
    instagram_account_id: str

    # Reverse geocoding
    nominatim_user_agent: str = "CleanBengaluru/1.0"

    # Caption hashtags
    instagram_hashtags: str = "#CleanBengaluru #SwachhBharat #WasteManagement #Bengaluru"

    # Public base URL of this server (needed so Instagram can fetch the image)
    # e.g. https://your-domain.com  or  https://abc123.ngrok.io
    base_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
