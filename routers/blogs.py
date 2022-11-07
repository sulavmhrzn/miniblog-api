from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from dependencies import get_db
from models.blog import Blog
from models.user import User
from schemas.blog import BlogCreate, BlogOut
from services.auth import Auth
from settings import settings

router = APIRouter(prefix=f"{settings.API_ENTRYPOINT}/blogs", tags=["Blogs"])


@router.get("/", response_model=list[BlogOut])
def get_blogs(db: Session = Depends(get_db)):
    """Get all blogs"""
    logger.info("Getting blogs from database")
    return db.query(Blog).all()


@router.get("/{blog_id}", response_model=BlogOut)
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    """Get a single blog with given id"""
    logger.info(f"Getting a blog from database with id {blog_id}")
    blog = db.query(Blog).get(blog_id)

    if not blog:
        logger.info(f"Blog with id {blog_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with id {blog_id} not found.",
        )

    return blog


@router.post("/", response_model=BlogOut)
def create_blog(
    new_blog: BlogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(Auth.get_current_user),
):
    """Create a new blog passing in the authenticated user"""
    blog = Blog(**new_blog.dict(), user_id=user.id)
    logger.info(f"Creating new blog: {blog}")
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


@router.delete("/{blog_id}")
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(Auth.get_current_user),
):
    """Delete a blog with given id"""
    logger.info(f"Getting a blog from database with id {blog_id}")
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id, Blog.user_id == user.id).one()
    except NoResultFound:
        logger.info(f"Blog with id {blog_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with id {blog_id} not found.",
        )

    db.delete(blog)
    db.commit()
    logger.info(f"Blog with id {blog_id} deleted by user {user.username}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{blog_id}", response_model=BlogOut)
def update_blog(
    blog_id: int,
    new_blog: BlogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(Auth.get_current_user),
):
    """Update a blog with given id"""
    logger.info(f"Getting a blog from database with id {blog_id}")
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id, Blog.user_id == user.id).one()
    except NoResultFound:
        logger.info(f"Blog with id {blog_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with id {blog_id} not found.",
        )
    blog.title = new_blog.title
    blog.content = new_blog.content
    db.commit()
    db.refresh(blog)
    logger.info(f"Blog with id {blog_id} updated")

    return blog
