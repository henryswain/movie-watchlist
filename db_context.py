import logging
from beanie import init_beanie
from my_config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient

from movie_model import Movie, Review, Watchlist
from user_model import User

logger = logging.getLogger(__name__)

async def init_database():
    my_config = get_settings()
    # Add tlsAllowInvalidCertificates=true to the connection string
    connection_string = my_config.connection_string
    if "?" in connection_string:
        connection_string += "&tlsAllowInvalidCertificates=true"
    else:
        connection_string += "?tlsAllowInvalidCertificates=true"
    try:
        client = AsyncIOMotorClient(connection_string)
        logger.info("database client created")
        db = client["MovieTracker"]
        await init_beanie(database=db, document_models=[User, Movie, Review, Watchlist])
        logger.info("Beanie ORM initialized successfully with all document models")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise