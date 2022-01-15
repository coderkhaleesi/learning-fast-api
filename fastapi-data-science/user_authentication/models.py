from datetime import datetime, timedelta

from pydantic import BaseModel, EmailStr, Field
from tortoise.models import Model

from tortoise import fields, timezone

from password import get_password_hash, generate_token, verify_password

def get_expiration_date() -> datetime:
    return timezone.now() + timedelta(seconds=86400)

class UserBase(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str

class UserDb(UserBase):
    hashed_password: str

class User(UserBase):
    id: int

class UserTortoise(Model):
    id = fields.IntField(pk=True, generated=True)
    email = fields.CharField(index=True, unique=True, null=False, max_length=255)
    hashed_password = fields.CharField(null=False, max_length=255)

    class Meta:
        db_table = "users"

class AccessToken(BaseModel): 
    user_id: int
    access_token: str = Field(default_factory=generate_token)
    expiration_date: datetime = Field(default_factory=get_expiration_date)

class AccessTokenTortoise(Model):
    access_token = fields.CharField(pk=True, max_length=255)
    user = fields.ForeignKeyField("models.UserTortoise", null=False)
    expiration_date = fields.DatetimeField(null=False)

    class Meta:
        db_table = "access_tokens"
