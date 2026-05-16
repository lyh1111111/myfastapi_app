"""
用户相关数据库操作模块
提供用户查询、创建等数据库操作功能
"""
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from toutiao_app.models.users import User, UserToken
from toutiao_app.schemas.users import UserRequest
from toutiao_app.utils.security import *


async def get_user_by_name(db: AsyncSession, username: str):
    """
    根据用户名查询用户
    
    Args:
        db: 数据库会话
        username: 用户名
        
    Returns:
        User对象，如果不存在则返回None
    """
    Query = select(User).where(User.username == username)
    result = await db.execute(Query)
    return result.scalars().first()


async def create_user(db: AsyncSession, user_data: UserRequest):
    """
    创建新用户
    
    Args:
        db: 数据库会话
        user_data: 用户注册数据
        
    Returns:
        创建成功的User对象
    """
    hashed_password = hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user



async def creat_token_user(db: AsyncSession, user_id: str):
    """
    创建用户令牌

    Args:
        db: 数据库会话
        username: 用户名

    Returns:
        创建成功的User对象
    """
    token = str(uuid.uuid4())
    expire_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalars().first()

    if user_token:
        user_token.token = token
        user_token.expires_at = expire_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expire_at)
        db.add(user_token)
        await db.commit()
    return token