
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from toutiao_app.models.users import User
from toutiao_app.schemas.users import UserRequest
from toutiao_app.utils.security import *


async def get_user_by_name(db: AsyncSession , username: str):
    Query = select(User).where(User.username == username)
    result = await db.execute(Query)
    return result.scalars().first()


async def create_user(db: AsyncSession, user_data:UserRequest):
    hashed_password = hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

