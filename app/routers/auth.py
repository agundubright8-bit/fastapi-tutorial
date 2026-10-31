from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, utils, oauth2

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

'''
    login endpoint for user authentication. It accepts user credentials, verifies them, and returns an access token if the credentials are valid.
'''
@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    # check if user exists
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"invalid credentials")

    # check if password is correct
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"invalid credentials")

    # create a token
    #return it
    access_token = oauth2.create_access_token(data= {"user_id": user.id})
    return {"access_token": access_token, "token_type":"bearer"}