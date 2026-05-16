"""
用户相关数据库操作模块
提供用户查询、创建等数据库操作功能
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from toutiao_app.models.users import User
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

