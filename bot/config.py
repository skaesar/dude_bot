from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "db")
    user: str = os.getenv("DB_USER")
    password: str = os.getenv("DB_PASSWORD")
    name: str = os.getenv("DB_NAME")

@dataclass
class Config:
    tg_token: str = os.getenv("BOT_TOKEN")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY")
    model: str = "google/gemma-4-26b-a4b-it:free"
    history_limit: int = 10
    system_prompt: str = "Ты дружелюбный ассистент."
    db: DatabaseConfig = None

    def __post_init__(self):
        self.db = DatabaseConfig()

config = Config()