from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from toutiao_app.config.db_conf import post_dbs
from toutiao_app.curd.users import get_user_by_name, create_user
from toutiao_app.schemas.users import UserRequest

router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def register(users_data: UserRequest, db: AsyncSession = Depends(post_dbs)):
    # 检查用户名是否已存在
    exist_user = await get_user_by_name(db, users_data.username)
    if exist_user:
        return {
            "code": 400,
            "message": f"用户名 '{users_data.username}' 已存在，请选择其他用户名",
            "data": None
        }
    
    # 创建新用户
    user = await create_user(db, users_data)
    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "token": "用户访问令牌",
            "userInfo": {
                "id": user.id,
                "bio": user.bio if hasattr(user, 'bio') else "这个人很懒,什么都没留下",
                "username": user.username,
                "avatar": user.avatar if hasattr(user, 'avatar') else "https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
            }
        }
    }