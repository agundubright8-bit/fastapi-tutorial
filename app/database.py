from sqlalchemy import create_engine, URL
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings
'''
    This module sets up the database connection and provides functions for interacting with the database using SQLAlchemy ORM.
    It defines the database URL, creates the SQLAlchemy engine, and establishes a session factory for managing database sessions. The module also includes a function to retrieve a database session for use in API endpoints.
    The database connection parameters are loaded from the application's configuration settings.
'''

# The SQLALCHEMY_DATABASE_URL variable constructs the database connection URL using the settings defined in the config module. It specifies the database driver, username, password, host, port, and database name for connecting to the PostgreSQL database.
SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.database_username,
    password=settings.database_password,
    host=settings.database_hostname,
    port=int(settings.database_port),
    database=settings.database_name,
)

# The create_engine function creates a SQLAlchemy engine that manages the connection to the database. It takes the constructed database URL as an argument and establishes a connection pool for efficient database interactions.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# The declarative_base function creates a base class for defining SQLAlchemy ORM models. It serves as the foundation for creating database tables and mapping them to Python classes.
Base = declarative_base()

# The get_db function is a dependency that provides a database session for use in API endpoints. It creates a new session using the SessionLocal factory, yields it for use in the endpoint, and ensures that the session is closed after the request is completed.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# while True:
#     try:
#         conn = psycopg.connect(host='localhost', dbname='fastapi', user='postgres', password='brightag@21', row_factory=dict_row)
#         cursor = conn.cursor()
#         print("Database connection successful")
#         break
#     except Exception as error:
#         print("Database connection failed")
#         print("Error: ", error)
#         time.sleep(5)

# my_posts  = [{"title": "title of post 1", "content" : "content of post 1", "id": 1}, {"title": "favorite foods", "content": "I like Rice", "id": 2}]


# def find_post(id):
#     for post in my_posts:
#         if post["id"] == id:
#             return post
