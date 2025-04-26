import logging
from beanie import init_beanie
from my_config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient

from model import Movie
from user import User

logger = logging.getLogger(__name__)


async def init_database():
    my_config = get_settings()
    client = AsyncIOMotorClient(my_config.connection_string)
    logger.info("database client created")
    db = client["todo_app"]
    await init_beanie(database=db, document_models=[User, Movie])