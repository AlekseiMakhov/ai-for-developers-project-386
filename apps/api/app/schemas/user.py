from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class UserCreate(CamelModel):
    email: EmailStr
    name: str
    password: str
    timezone: str = "UTC"
    slug: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(CamelModel):
    id: str
    email: str
    name: str
    timezone: str
    slug: str
    created_at: datetime

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class TokenResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"
