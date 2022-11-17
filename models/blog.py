from datetime import datetime

import sqlalchemy as sa

from db import Base


class Blog(Base):
    __tablename__ = "blogs"
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(200))
    content = sa.Column(sa.Text)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    user_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    def __repr__(self):
        return self.title
