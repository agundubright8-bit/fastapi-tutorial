from .. import models, schemas, utils
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from ..database  import get_db
'''
    This module defines the API endpoints for managing users in the application. It includes routes for creating new users and retrieving user information by ID.
    The endpoints interact with the database using SQLAlchemy ORM and return appropriate HTTP responses based on the outcome of each operation. User passwords are hashed before being stored in the database for security purposes.
'''
router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Create a new user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    user.password = utils.hash_password(user.password)

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Get a user by ID
@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")
    return user