import sqlalchemy as sa

from db import Base


class Comment(Base):
    __tablename__ = "comments"
    id = sa.Column(sa.Integer, primary_key=True)
    content = sa.Column(sa.Text)
    post_id = sa.Column(sa.Integer, sa.ForeignKey("blogs.id", ondelete="CASCADE"))
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"))

    def __repr__(self):
        return self.content
