from loguru import logger
from passlib.context import CryptContext

from settings import settings


class Auth:
    pwd_context = CryptContext(schemes=[settings.HASH_ALGORITHM], deprecated="auto")

    @classmethod
    def create_hash_password(cls, plain_password) -> str:
        logger.info("Creating a hash password")
        return cls.pwd_context.hash(plain_password)

    @classmethod
    def verify_password(cls, plain_password, hashed_password) -> bool:
        logger.info("Verifying password")
        return cls.pwd_context.verify(plain_password, hashed_password)
