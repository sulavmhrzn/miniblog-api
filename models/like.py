import sqlalchemy as sa

from db import Base


class Like(Base):
    __tablename__ = "likes"
    id = sa.Column(sa.Integer, primary_key=True)
    post_id = sa.Column(sa.Integer, sa.ForeignKey("blogs.id", ondelete="CASCADE"))
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"))

    def __str__(self) -> str:
        return f"{self.post_id} - {self.user_id}"
