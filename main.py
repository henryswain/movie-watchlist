from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from db_context import init_database
from movie import movie_router
from user import user_router
from db_context import init_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup event
    print("Application starts...")
    await init_database()
    yield
    # on shutdown event
    print("Application shuts down...")

app = FastAPI(title="Vacation App", version="2.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the movie router
app.include_router(movie_router, tags=["Movies"], prefix="/movies")
app.include_router(user_router, tags=["Users"], prefix="/users")

# Mount static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


# Root route
@app.get("/")
async def read_index():
    return FileResponse("./frontend/index.html")
