from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from toutiao_app.config.db_conf import post_dbs
from toutiao_app.curd.users import get_user_by_token


async def get_current_user(
        db: AsyncSession = Depends(post_dbs),
        Authorization: str = Header(..., description="Bearer <token>"),
):
    """
    根据Token查询用户

    Args:
        db: 数据库会话对象
        token: 要查询的令牌

    Returns:
        返回User对象，如果用户不存在则返回None
    """
    # 构造SELECT查询语句，筛选token字段等于传入值的记录
    Token = Authorization.replace("Bearer ", "")
    user = await get_user_by_token(db, Token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌或已过期")

    return user
    