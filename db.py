from sqlalchemy.engine import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from settings import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    url=DATABASE_URL, echo=settings.DEBUG, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
