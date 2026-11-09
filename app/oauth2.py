from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from .config import settings
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
'''
    This module provides functions for handling OAuth2 authentication and JWT token management in the application. It includes functions for creating and verifying access tokens, as well as retrieving the currently authenticated user based on the provided token.
    The module uses the FastAPI framework and SQLAlchemy ORM for database interactions. It also utilizes the jose library for JWT encoding and decoding.
'''
# OAuth2PasswordBearer is a class provided by FastAPI that helps in implementing OAuth2 authentication. It is used to extract the access token from the request's Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# The following constants are used for JWT token creation and verification. They are loaded from the application's configuration settings.  
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# The create_access_token function generates a JWT access token. It takes a dictionary of data (usually containing user information) and encodes it into a JWT token with an expiration time. The token is signed using the SECRET_KEY and ALGORITHM specified in the settings.
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# The verify_access_token function decodes and verifies a JWT access token. It checks if the token is valid, not expired, and contains the expected user information. If the token is invalid or expired, it raises an HTTPException with a 401 Unauthorized status code.
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=user_id)
    except JWTError:
        raise credentials_exception
    return token_data


# The get_current_user function is a dependency that retrieves the currently authenticated user based on the provided JWT access token. It extracts the token from the request, verifies it, and fetches the corresponding user from the database. If the token is invalid or the user does not exist, it raises an HTTPException with a 401 Unauthorized status code.
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token_data = verify_access_token(token, credentials_exception)
    db_user = db.query(models.User).filter(
        models.User.id == token_data.id
    ).first()

    if db_user is None:
        raise credentials_exception
    return db_user

    