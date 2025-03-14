from pydantic import BaseModel


class LoginSchema(BaseModel):
    login: str
    password: str


class SignUpSchemas(BaseModel):
    login: str
    password: str


class UserSchema(BaseModel):
    id: int
    login: str
