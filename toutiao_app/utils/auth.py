from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from toutiao_app.config.db_conf import post_dbs
from toutiao_app.curd.users import get_user_by_token
from toutiao_app.models.users import User


async def get_current_user(
        db: AsyncSession = Depends(post_dbs),
        Authorization: str = Header(..., description="Bearer <token>"),
) -> User:
    """
    根据Token查询用户

    Args:
        db: 数据库会话对象
        Authorization: 认证头，格式为 "Bearer <token>"

    Returns:
        返回User ORM对象
        
    Raises:
        HTTPException: 当令牌无效或已过期时抛出401错误
    """
    # 从Authorization头中提取token（移除"Bearer "前缀）
    Token = Authorization.replace("Bearer ", "")
    user = await get_user_by_token(db, Token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌或已过期")

    return user
    