from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Literal, Optional


'''
    This module defines the Pydantic models (schemas) used for data validation and serialization in the application.
    The models represent the structure of the data that is sent and received through the API endpoints.
'''

# The PostBase model serves as a base class for post-related schemas. It includes common attributes such as title, content, and published status.
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


# The PostCreate model inherits from PostBase and is used for creating new posts. It does not add any additional attributes but serves as a distinct schema for post creation requests.
class PostCreate(PostBase):
    pass


# The Post model inherits from PostBase and adds additional attributes such as id, created_at timestamp, user_id, and owner information. It is used for representing posts in API responses.
class Post(PostBase):
    id: int
    created_at: datetime
    user_id: int
    owner: UserOut
    model_config = ConfigDict(from_attributes=True)


class PostOut(Post):
    votes: int
    model_config = ConfigDict(from_attributes=True)


# The UserCreate model is used for creating new users. It includes attributes for email and password, which are required for user registration.
class UserCreate(BaseModel):

    email: EmailStr
    password: str


# The UserOut model is used for representing user information in API responses. It includes attributes for id, email, and created_at timestamp. The model_config attribute specifies that the model should be populated from attributes of the underlying object.
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# The UserLogin model is used for user authentication requests. It includes attributes for email and password, which are required for logging in.
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# The Token model is used for representing authentication tokens in API responses. It includes attributes for access_token and token_type, which are returned upon successful user authentication.
class Token(BaseModel):
    access_token: str
    token_type: str


# The TokenData model is used for representing the data contained within an authentication token. It includes an optional id attribute, which can be used to identify the user associated with the token.
class TokenData(BaseModel):
    id: Optional[int] = None


# The Vote model is used for representing voting actions in the application. It includes attributes for post_id and dir, which indicate the post being voted on and the direction of the vote (0 for downvote, 1 for upvote).
class Vote(BaseModel):
    post_id: int
    dir: Literal[0, 1]  # 0 or 1