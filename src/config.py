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
    # WEBAPP_URL: str = "https://roomstar.serveo.net"
    # WEBHOOK_URL: str = "https://roomstar.serveo.net"
    # APP_HOST: str = "localhost"
    
    # Продакшен
    WEBAPP_URL: str = "https://roomstars.ru"
    WEBHOOK_URL: str = "https://xhackerfinnx-roomstar-1bf7.twc1.net"
    APP_HOST: str = "0.0.0.0"
    
    WEBHOOK_PATH: str = "/webhook"
    APP_PORT: int = 8000
    
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )
    
config = Settings()