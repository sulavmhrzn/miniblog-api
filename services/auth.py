from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db import engine
from models.user import User
from settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")


class Auth:
    pwd_context = CryptContext(schemes=[settings.HASH_ALGORITHM], deprecated="auto")

    @classmethod
    def create_hash_password(cls, plain_password: str) -> str:
        """Generate a hashed password

        Args:
            plain_password (str): Password to hash

        Returns:
            str: Hashed password
        """
        logger.info("Creating a hash password")
        return cls.pwd_context.hash(plain_password)

    @classmethod
    def verify_password(cls, plain_password, hashed_password) -> bool:
        """Verify plain password with hash

        Args:
            plain_password (_type_): Plain password from front end
            hashed_password (bool): Hashed password from database

        Returns:
            bool: True if verified
        """
        logger.info("Verifying password")
        result = cls.pwd_context.verify(plain_password, hashed_password)
        logger.info(f"Password verification returned: {result}")
        return result

    @classmethod
    def create_jwt_token(cls, data: dict) -> dict:
        """Create a new jwt token

        Args:
            data (dict): claims to be encoded

        Returns:
            dict: New claims with expiration time
        """
        logger.info(f"Creating jwt token for data: {data}")
        to_encode = data.copy()
        to_encode.update(
            {"exp": datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)}
        )
        logger.info(f"Update data with exp: {to_encode}")
        return jwt.encode(
            to_encode, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    @classmethod
    def get_user(cls, username: str) -> bool | User:
        """Get user from database if exists

        Args:
            username (str): Username to check against

        Returns:
            bool | User: User model if user exists else False
        """
        logger.info(f"Getting user: {username}")
        with Session(engine) as session:
            user = session.query(User).filter(User.username == username).first()

        if not user:
            logger.info(f"User not found: {username}")
            return False

        logger.info(f"User found: {username}")
        return user

    @classmethod
    def authenticate_user(cls, username: str, password: str) -> User:
        """Authenticate a user using username and password

        Args:
            username (str): Users username
            password (str): Users password

        Returns:
            bool: True if user exists and password is verified else False
        """
        logger.info(f"Authenticating user: {username} with password {password}")
        user = cls.get_user(username=username)
        if not user:
            return False
        if not cls.verify_password(password, user.password):
            return False
        logger.info(f"User authenticated: {username}")

        return user

    @classmethod
    def get_current_user(cls, token: str = Depends(oauth2_scheme)) -> User:
        """Validate token and return user

        Args:
            token (str, optional):

        Raises:
            HTTPException: If validation fails

        Returns:
            User: User model
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        logger.info(f"Decoding token: {token}")
        try:
            payload = jwt.decode(
                token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            username: str = payload.get("sub")
            logger.info(f"Data from token: {payload}")

            if username is None:
                logger.info("Username not found in token")
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = cls.get_user(username)
        if not user:
            raise credentials_exception
        return user
