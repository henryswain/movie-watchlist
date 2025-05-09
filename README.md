# FilmTrack - Movie Watchlist Application
FilmTrack is a web application for tracking movies you've watched or want to watch. Users can add movies, rate them, write reviews, and organize them by watched status. The application features user authentication, with differentiated access for regular users and administrators.
# Project Overview
This project combines:

Frontend: Vue.js application with responsive UI  
Backend: FastAPI (Python) REST API  
Database: MongoDB for data storage  

# Key Features

- User authentication with JWT tokens
- Add movies with titles, comments, and ratings
- Mark movies as watched/unwatched
- Write and view movie reviews
- Filter movies by status (all, watched, not watched, my movies)
- Import picture as a background (.jpeg, .jpg, .png, .gif)
- Schedule viewing dates with calendar event export
- Administrative privileges for managing all content

# Installation & Setup
## Prerequisites

- Python 3.10+
- Node.js and npm
- MongoDB (local instance or MongoDB Atlas)

# Backend Setup

1. Clone the repository:
- git clone https://github.com/henryswain/movie-watchlist.git
- cd movie-watchlist

2. Create and activate a Python virtual environment:
###  On Windows
- python -m venv venv
- venv\Scripts\activate

### On macOS/Linux
- python -m venv venv
- source venv/bin/activate

3. Install Python dependencies:
- pip install -r requirements.txt

4. Configure your MongoDB connection:

- Create a .env file in the project root (or update my_config.py)  
- Add your MongoDB connection string:  
MONGODB_URL=mongodb+srv://yourusername:yourpassword@yourcluster.mongodb.net/filmtrack  
SECRET_KEY=your_jwt_secret_key




## Frontend Setup

1. Navigate to the frontend directory:  
cd frontend

- Install Node.js dependencies:  
- npm install


## Running the Application
# Starting the Backend Server  
From the project root directory (with virtual environment activated):  
uvicorn main:app --reload  
The API will be available at http://127.0.0.1:8000  
# Starting the Frontend Development Server
From the frontend directory (in a separate terminal, NOT in virtual environment):
npm run dev
The frontend will be available at http://localhost:5173 

## Testing
Run the unit tests to ensure everything is working correctly
bash# Make sure you're in the project root and virtual environment is activated
pytest test_password.py -v  
![Test Results](frontend/src/assets/pytest.png)
## Project Structure

main.py - FastAPI application entry point  
movie.py - Movie-related endpoints  
user.py - User authentication and management  
jwt_auth.py - JWT authentication logic  
movie_model.py - Database models  
user_model.py - User models  
db_context.py - Database connection setup  
frontend/ - Vue.js frontend application  

# Demo
## Login
- Users must be in the database to login (Update role in the database to switch between user and Admin access)
![Login Process](frontend/src/assets/Logintest.gif)  
## Basic User
- Basic can only delete/update movies based on userID
![Basicuser](frontend/src/assets/Basicuser.gif)  
## Admin User
- Admins can update/delete any movie
![Adminuser](frontend/src/assets/Adminuser.gif)  
## Background Image Upload
![Uploading images](frontend/src/assets/Upload.gif)