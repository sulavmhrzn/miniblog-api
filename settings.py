import pydantic


class Settings(pydantic.BaseSettings):
    DEBUG: bool
    API_ENTRYPOINT: str
    DATABASE_URL: str
    HASH_ALGORITHM: str

    class Config:
        env_file = ".env"


settings = Settings()
