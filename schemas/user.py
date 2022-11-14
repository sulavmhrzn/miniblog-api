import pydantic

from schemas.blog import BlogOut


class UserCreate(pydantic.BaseModel):
    username: str
    password: pydantic.SecretStr
    password2: pydantic.SecretStr

    @pydantic.validator("password2")
    @classmethod
    def validate_password_password2(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

    @pydantic.validator("username")
    @classmethod
    def validate_username(cls, v, values):
        if " " in v:
            raise ValueError("Username contains space")
        if len(v) > 20:
            raise ValueError("Username exceeds 20 characters")
        return v


class UserOut(pydantic.BaseModel):
    username: str
    profile_img: str

    class Config:
        orm_mode = True


class UserBlogs(UserOut):
    blogs: list[BlogOut]

    class Config:
        orm_mode = True


class UserInDB(pydantic.BaseModel):
    id: int
    username: str
