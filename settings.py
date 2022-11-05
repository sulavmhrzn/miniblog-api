import pydantic


class Settings(pydantic.BaseSettings):
    DEBUG: bool
    API_ENTRYPOINT: str
    DATABASE_URL: str
    HASH_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    class Config:
        env_file = ".env"


settings = Settings()
