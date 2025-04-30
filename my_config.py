from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class MyConfig(BaseSettings):
    connection_string: str
    secret_key: str
    db_name: str = "MovieTracker"

    model_config = SettingsConfigDict(env_file=".env")



@lru_cache
def get_settings():
    return MyConfig()