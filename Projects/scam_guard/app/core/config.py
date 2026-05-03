from dotenv import load_dotenv
from pydantic_settings import BaseSettings
load_dotenv()

class Settings(BaseSettings):
    openai_api_key : str
    # model config
    openai_model: str = "gpt-4o-mini"
    default_prompt_version: str = "v1_zero_shot"


def get_setings():
    return Settings()
