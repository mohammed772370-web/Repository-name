import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    
    ADMIN_IDS: List[int] = [
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") 
        if x.strip().isdigit()
    ]
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Riyadh")
    EDUCATION_POST_TIMES: List[str] = os.getenv("EDUCATION_POST_TIMES", "10:00,18:00").split(",")
    NEWS_POST_TIMES: List[str] = os.getenv("NEWS_POST_TIMES", "08:00,14:00").split(",")
    ECONOMIC_CALENDAR_CHECK_INTERVAL: int = int(os.getenv("ECONOMIC_CALENDAR_CHECK_INTERVAL", "60"))
    
    LANGUAGE: str = os.getenv("LANGUAGE", "ar")
    ENABLE_AI_GENERATION: bool = os.getenv("ENABLE_AI_GENERATION", "True").lower() == "true"
    ENABLE_ECONOMIC_NEWS: bool = os.getenv("ENABLE_ECONOMIC_NEWS", "True").lower() == "true"
    ENABLE_EDUCATION: bool = os.getenv("ENABLE_EDUCATION", "True").lower() == "true"

    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    FRED_API_KEY: str = os.getenv("FRED_API_KEY", "")

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN مطلوب! احصل عليه من @BotFather")
        if not cls.CHANNEL_ID:
            print("⚠️ تحذير: CHANNEL_ID غير محدد، لن يتم النشر التلقائي للقناة")

config = Config()
