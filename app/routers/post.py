
from typing import Optional
from sqlalchemy import func
from .. import models, schemas, oauth2
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)
'''
    This module defines the API endpoints for managing posts in the application. It includes routes for creating, retrieving, updating, and deleting posts.
    Each endpoint is protected by user authentication, ensuring that only authorized users can perform actions on their own posts. The endpoints interact with the database using SQLAlchemy ORM and return appropriate HTTP responses based on the outcome of each operation.
'''


@router.get("/", response_model=list[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()

    posts = db.query(models.Post).filter(
        models.Post.title.ilike(f"%{search}%")
    ).order_by(models.Post.id).offset(skip).limit(limit).all()

    votes = db.query(
        models.Post,
        func.count(models.Vote.post_id).label("votes")
    ).join(
        models.Vote,
        models.Vote.post_id == models.Post.id,
        isouter=True
    ).group_by(models.Post.id).all()

    vote_counts = {
        vote.Post.id: vote.votes
        for vote in votes
    }

    for post in posts:
        post.votes = vote_counts.get(post.id, 0)

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostOut)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    new_post = models.Post(**post.model_dump())
    new_post.user_id = current_user.id

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    new_post.votes = 0

    return new_post


@router.get("/latest", response_model=schemas.PostOut)
def get_latest_post(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts ORDER BY id DESC LIMIT 1""")
    # latest_post = cursor.fetchone()

    latest_post = db.query(models.Post).filter(
        models.Post.user_id == current_user.id
    ).order_by(models.Post.id.desc()).first()

    if not latest_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts found"
        )

    latest_post.votes = db.query(
        func.count(models.Vote.post_id)
    ).filter(
        models.Vote.post_id == latest_post.id
    ).scalar()

    return latest_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (id,))
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(
        models.Post.id == id,
        models.Post.user_id == current_user.id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found"
        )

    post.votes = db.query(
        func.count(models.Vote.post_id)
    ).filter(
        models.Vote.post_id == id
    ).scalar()

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    deleted_post = db.query(models.Post).filter(
        models.Post.id == id
    ).first()

    if not deleted_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found"
        )

    if deleted_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this post"
        )

    db.delete(deleted_post)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostOut)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post_to_update = db.query(models.Post).filter(
        models.Post.id == id
    ).first()

    if not post_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found"
        )

    if post_to_update.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this post"
        )

    for key, value in updated_post.model_dump().items():
        setattr(post_to_update, key, value)

    db.commit()
    db.refresh(post_to_update)

    post_to_update.votes = db.query(
        func.count(models.Vote.post_id)
    ).filter(
        models.Vote.post_id == id
    ).scalar()

    return post_to_update
