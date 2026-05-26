from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"
    APP_ENV: str = "development"
    SECRET_KEY: str
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""
    
    NOTIFICATION_PROVIDER: str = "mock"   # mock | msg91 | twilio
    MSG91_AUTH_KEY: str = ""
    MSG91_SENDER_ID: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
