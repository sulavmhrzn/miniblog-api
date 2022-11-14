from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from sqlalchemy.orm import Session

from dependencies import get_db
from models.blog import Blog
from models.user import User
from schemas.user import UserBlogs, UserCreate, UserOut
from services.auth import Auth
from settings import settings

router = APIRouter(prefix=f"{settings.API_ENTRYPOINT}/users", tags=["User"])


@router.get("/", response_model=UserBlogs)
def get_me(db: Session = Depends(get_db), user: User = Depends(Auth.get_current_user)):
    """Get data about currently logged in user"""
    result = db.query(Blog).filter(Blog.user_id == user.id).all()
    return UserBlogs(username=user.username, blogs=result, profile_img=user.profile_img)


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
    profile_img = f"https://avatars.dicebear.com/api/identicon/{user.username}.svg"

    new_user = User(**user.dict(exclude={"password2"}), profile_img=profile_img)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User created: {user.dict(exclude={'password', 'password2'})}")
    return new_user


@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Return a access token if valid data"""
    user = Auth.authenticate_user(
        username=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or pasword",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = Auth.create_jwt_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
