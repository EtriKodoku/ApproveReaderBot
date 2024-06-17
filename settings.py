from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LINK: str = "Default"
    TOKEN: str = "Default"
    CHECK_CHANNEL_ID: int = 0
    JOING_CHANNEL_ID: int = 0
    LOG_CHAT_ID: int | None = None

    class Config:
        env_prefix = "AR_"
       

load_dotenv()
settings = Settings()
