from fastapi import APIRouter, Depends, HTTPException, Response, status
from loguru import logger
from sqlalchemy.orm import Session

from dependencies import get_db
from models.blog import Blog
from models.like import Like
from models.user import User
from services.auth import Auth
from utils import get_object_or_404

router = APIRouter(prefix="/likes", tags=["Likes"])


@router.post("/{blog_id}")
def like_post(
    blog_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(Auth.get_current_user),
):
    """Like a given post if not already liked else remove the like"""
    blog = get_object_or_404(Blog, blog_id)
    is_already_liked = (
        db.query(Like).filter(Like.post_id == blog_id, Like.user_id == user.id).first()
    )
    if is_already_liked:
        logger.info(f"User: {user} has already liked blog: {blog}. Removing like")
        db.delete(is_already_liked)
        db.commit()
        return "Removed like"

    logger.info(f"User: {user} liked blog: {blog}")
    like = Like(post_id=blog_id, user_id=user.id)
    db.add(like)
    db.commit()

    return Response(status_code=status.HTTP_201_CREATED, content="Like added")
