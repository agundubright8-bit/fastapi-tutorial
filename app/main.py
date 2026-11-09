from fastapi import FastAPI

from app.routers import vote
from .database import engine
from .routers import post, user, auth
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

'''
    This is the main entry point of the FastAPI application. It initializes the FastAPI app, sets up the database connection, and includes the API routers for handling different endpoints.
    The application is structured into separate modules for posts, users, and authentication, allowing for better organization and maintainability of the codebase. The database models are created using SQLAlchemy ORM, and the application is configured using settings defined in the config module.    
'''

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The app.include_router function is used to include the routers for different API endpoints. Each router corresponds to a specific module (post, user, auth) and defines the routes and their associated logic for handling requests related to posts, users, and authentication.
app.include_router(post.router)
app.include_router(user.router) 
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"message" : "Hello world!"}




