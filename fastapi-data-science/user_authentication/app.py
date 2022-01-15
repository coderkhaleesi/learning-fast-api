from typing import cast
from tortoise import timezone

from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.contrib.fastapi import register_tortoise

from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from authenticate import authenticate, create_access_token
from models import AccessTokenTortoise, UserBase, UserCreate, UserDb, User, UserTortoise
from password import get_password_hash

app = FastAPI()

async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/token"))) -> UserTortoise:
    try:
        access_token: AccessTokenTortoise = await AccessTokenTortoise.get(
                                                access_token=token, expiration_date__gte=timezone.
                                                now()).prefetch_related("user")

        return cast(UserTortoise, access_token.user)

    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def user_register(user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    
    try:
        user_tortoise = await UserTortoise.create(**user.dict(),
                                                    hashed_password=hashed_password)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists!"
        )

    return User.from_orm(user_tortoise)

@app.post("/token")
async def create_token(form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)):
    email = form_data.username
    password = form_data.password
    user = await authenticate(email, password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        print("HTTP wrror")
    
    token = await create_access_token(user)

    return {"access_token": token.access_token, "token_type": "bearer"}

@app.get("/anything-protected", response_model=User)
async def anything_protected(user: UserDb = Depends(get_current_user)):
    return User.from_orm(user)

TORTOISE_ORM = {
    "connections": {"default": "sqlite://authentication.db"},
    "apps": {
        "models": {
            "models": ["models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
}

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)