import logging
from beanie import init_beanie
from my_config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient

from movie_model import Movie, Review, Watchlist
from user_model import User

logger = logging.getLogger(__name__)


async def init_database():
    print("init_database called")
    my_config = get_settings()
    client = AsyncIOMotorClient(my_config.connection_string)
    print("connection String: ", my_config.connection_string)
    print("secret key: ", my_config.secret_key)
    logger.info("database client created")
    db = client["MovieTracker"]
    await init_beanie(database=db, document_models=[User, Movie, Review, Watchlist])