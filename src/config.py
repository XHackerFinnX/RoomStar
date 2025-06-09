from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    POSTGRESQL_USER: SecretStr
    POSTGRESQL_PASSWORD: SecretStr
    POSTGRESQL_HOST: SecretStr
    POSTGRESQL_PORT: SecretStr
    POSTGRESQL_DATABASE: SecretStr
    
    # Локальный запуск
    WEBAPP_URL: str = "https://roomstar.serveo.net"
    WEBHOOK_URL: str = "https://roomstar.serveo.net"
    WEBHOOK_PATH: str = "/webhook"
    APP_HOST: str = "localhost"
    APP_PORT: int = 8000
    
    # Продакшен
    # WEBAPP_URL: str = "https://racerandom.ru"
    # WEBHOOK_URL: str = "https://xhackerfinnx-randombot-b4ef.twc1.net"
    # WEBHOOK_PATH: str = "/webhook"
    # APP_HOST: str = "0.0.0.0"
    # APP_PORT: int = 8000
    
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )
    
config = Settings()