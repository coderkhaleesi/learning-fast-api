from password import verify_password
from models import AccessToken,AccessTokenTortoise, UserBase, UserCreate, UserDb, User, UserTortoise
from tortoise.exceptions import DoesNotExist


async def authenticate(email: str, password: str) -> UserDb:
    
    try:
        user = await UserTortoise.get(email=email)

    except DoesNotExist:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return User.from_orm(user)

async def create_access_token(user: User) -> AccessToken:
    
    token = AccessToken(user_id=user.id)

    token_tortoise = await AccessTokenTortoise.create(**token.dict())

    return AccessToken.from_orm(token_tortoise)