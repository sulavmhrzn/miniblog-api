import pydantic


class Settings(pydantic.BaseSettings):
    DEBUG: bool
    API_ENTRYPOINT: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
