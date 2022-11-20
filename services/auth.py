import secrets
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db import engine
from models.user import User, ResetPassword
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

    @classmethod
    def get_password_reset_token(cls, user_id: int, token_expiry_in_hours: int) -> str:
        """Returns a password reset token

        Args:
            user_id (int): Valid user id for foreign key
            token_expiry (str): Password reset token expiry in hours

        Returns:
            str: Random token
        """
        with Session(engine) as db:
            logger.info("Generating password reset token")
            token = secrets.token_urlsafe(64)
            token_expiry = datetime.today() + timedelta(hours=token_expiry_in_hours)
            obj = ResetPassword(token=token, user_id=user_id, token_expiry=token_expiry)
            db.add(obj)
            db.commit()
        return token

    @classmethod
    def reset_password(cls, token: str, new_password: str) -> bool:
        """Validate and reset password

        Args:
            token (str): Password reset token
            new_password (str): New password for user

        Raises:
            HTTPException: If token is invalid

        Returns:
            bool: True if password reset was successfull
        """
        with Session(engine) as db:
            logger.info("Verifying reset token")
            token_available = db.query(ResetPassword).get(token)
            if not token_available:
                logger.info("Invalid password reset token")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invalid password reset token",
                )

            user_id = token_available.user_id

            logger.info(f"Reset token valid for user: {user_id}")

            db.query(ResetPassword).filter(ResetPassword.user_id == user_id).delete()
            db.commit()
            logger.info(f"Deleted all existing tokens for user id: {user_id}")

            # Convert a string from database to datetime object
            # token_expiry = datetime.strptime(
            #     token_available.token_expiry, "%Y-%m-%d %H:%M:%S.%f"
            # )

            if token_available.token_expiry < datetime.today():
                logger.info(
                    f"Password reset token expired. Token Expiry: {token_available.token_expiry} < Today: {datetime.today()}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password reset token expired. Request a new one",
                )

            user = db.query(User).get(user_id)
            user.password = cls.create_hash_password(new_password)
            db.commit()
            logger.info(f"Password reset for user: {user} successful")
            return True
