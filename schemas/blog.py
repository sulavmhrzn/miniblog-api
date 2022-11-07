import pydantic


class BlogCreate(pydantic.BaseModel):
    title: str
    content: str


class BlogOut(pydantic.BaseModel):
    id: int
    title: str
    content: str

    class Config:
        orm_mode = True
