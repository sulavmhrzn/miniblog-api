from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from dependencies import get_db
from models.user import User
from schemas.user import UserCreate, UserOut
from services.auth import Auth
from settings import settings

router = APIRouter(prefix=f"{settings.API_ENTRYPOINT}/users", tags=["User"])


@router.get("/")
def get_me():
    pass


@router.post("/create", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user if username does not exist in the database"""
    user_exist = db.query(User).filter(User.username == user.username).first()
    if user_exist:
        logger.info(f"User already exists, Raising HTTPException")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )
    user.password = Auth.create_hash_password(user.password.get_secret_value())
    new_user = User(**user.dict(exclude={"password2"}))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User created: {user.dict(exclude={'password', 'password2'})}")
    return new_user
