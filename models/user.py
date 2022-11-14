import sqlalchemy as sa

from db import Base


class User(Base):
    __tablename__ = "users"
    id: int = sa.Column(sa.Integer, primary_key=True)
    username: str = sa.Column(sa.String(200), index=True, unique=True)
    password: str = sa.Column(sa.String(200))
    profile_img: str = sa.Column(sa.String(200), nullable=True)

    def __repr__(self) -> str:
        return self.username
