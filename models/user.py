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


class ResetPassword(Base):
    __tablename__ = "reset_password"
    token: str = sa.Column(sa.String(200), unique=True, primary_key=True)
    user_id: str = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"))
    token_expiry: str = sa.Column(sa.DateTime())
