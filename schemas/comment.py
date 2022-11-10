import pydantic


class CommentOut(pydantic.BaseModel):
    id: int
    content: str
    post_id: int
    user_id: int

    class Config:
        orm_mode = True


class CommentCreate(pydantic.BaseModel):
    content: str
