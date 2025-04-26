import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from movie import movie_router
from user import user_router

app = FastAPI()


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
