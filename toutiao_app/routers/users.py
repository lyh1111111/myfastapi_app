from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from toutiao_app.config.db_conf import post_dbs
from toutiao_app.curd.users import get_user_by_name, create_user
from toutiao_app.schemas.users import UserRequest

router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def register(users_data: UserRequest, db: AsyncSession = Depends(post_dbs)):
    # 检查用户名是否已存在
    exist_user = await get_user_by_name(db, users_data.username)
    if exist_user:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    # 创建新用户
    user = await create_user(db, users_data)
    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "token": "用户访问令牌",
            "userInfo": {
                "id": user.id,
                "bio": user.bio,
                "username": user.username,
                "avatar": user.avatar
            }
        }
    }