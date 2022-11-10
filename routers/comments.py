from fastapi import APIRouter, Depends, HTTPException, Response, status
from loguru import logger
from sqlalchemy.orm import Session

from dependencies import get_db
from models.blog import Blog
from models.comment import Comment
from models.user import User
from schemas.comment import CommentCreate, CommentOut
from services.auth import Auth
from settings import settings

router = APIRouter(prefix=f"{settings.API_ENTRYPOINT}/blogs", tags=["Comments"])


@router.get("/{blog_id}/comments", response_model=list[CommentOut])
def get_comments(blog_id: int, db: Session = Depends(get_db)):
    """Get comments for a blog"""
    logger.info(f"Getting a blog from database with id {blog_id}")
    blog = db.query(Blog).get(blog_id)

    if not blog:
        logger.info(f"Blog with id {blog_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with id {blog_id} not found.",
        )

    comments = db.query(Comment).filter(Comment.post_id == blog_id).all()
    return comments


@router.post("/{blog_id}/comments", response_model=CommentOut)
def create_comment(
    blog_id: int,
    new_comment: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(Auth.get_current_user),
):
    """Create a new comment for a blog"""
    logger.info(f"Getting a blog from database with id {blog_id}")
    blog = db.query(Blog).get(blog_id)

    if not blog:
        logger.info(f"Blog with id {blog_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with id {blog_id} not found.",
        )

    comment = Comment(content=new_comment.content, post_id=blog.id, user_id=user.id)
    logger.info(f"Creating comment with data: {comment}")
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(Auth.get_current_user),
):
    """Delete a comment with given id"""
    logger.info(f"Getting comment with id {comment_id}")
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.user_id == user.id)
        .first()
    )

    if not comment:
        logger.info(f"Comment with id {comment_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    logger.info(f"Deleting comment with id {comment_id}")
    db.delete(comment)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/comments/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int,
    new_comment: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(Auth.get_current_user),
):
    """Update a comment with given id"""
    logger.info(f"Getting comment with id {comment_id}")
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.user_id == user.id)
        .first()
    )

    comment.content = new_comment.content
    db.commit()
    db.refresh(comment)
    logger.info(f"Updated comment with id {comment_id}: {comment}")
    return comment
