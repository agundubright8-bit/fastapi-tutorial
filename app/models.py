from .database import Base    
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey 
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

'''
    This module defines the database models for the application using SQLAlchemy ORM. It includes models for posts, users, and votes, representing the structure of the corresponding database tables.
'''

# The Post model represents the "posts" table in the database. It includes columns for id, title, user_id, content, published status, and created_at timestamp. The user_id column is a foreign key referencing the "users" table, establishing a relationship between posts and their owners.
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default="true", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    owner = relationship("User")


# The User model represents the "users" table in the database. It includes columns for id, email, password, and created_at timestamp. The email column is unique, ensuring that each user has a distinct email address. The model establishes a relationship with the Post model through the user_id foreign key in the posts table.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


# The Vote model represents the "votes" table in the database. It includes columns for user_id and post_id, both of which are foreign keys referencing the "users" and "posts" tables, respectively. The combination of user_id and post_id serves as the primary key for the votes table, ensuring that each user can vote only once per post.
class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)


