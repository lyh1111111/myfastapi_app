# 从FastAPI导入路由和依赖注入相关类
from fastapi import APIRouter, Depends
# 导入SQLAlchemy异步会话类型
from sqlalchemy.ext.asyncio import AsyncSession
# 导入Starlette状态码常量
from starlette import status
# 导入HTTP异常类
from starlette.exceptions import HTTPException

# 导入数据库会话依赖函数
from toutiao_app.config.db_conf import post_dbs
# 导入用户相关的CRUD操作函数
from toutiao_app.curd.users import get_user_by_name, create_user, creat_token_user
# 导入用户请求和响应数据模式
from toutiao_app.schemas.users import UserRequest, UserAuthResponse, UserInfoResponse
# 导入成功响应工具函数
from toutiao_app.utils.response import success_response

# 创建API路由器实例，设置URL前缀为/api/user，标签为users
router = APIRouter(prefix="/api/user", tags=["users"])

# 定义用户注册接口，处理POST请求到/api/user/register
@router.post("/register")
async def register(users_data: UserRequest, db: AsyncSession = Depends(post_dbs)):
    # 根据用户名查询数据库中是否已存在该用户
    exist_user = await get_user_by_name(db, users_data.username)
    # 如果用户已存在，返回400错误
    if exist_user:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    # 调用CRUD函数创建新用户，密码会自动加密
    user = await create_user(db, users_data)

    # 为用户生成认证令牌（token）
    token = await creat_token_user(db, user.id)
    # 使用Pydantic的model_validate将SQLAlchemy对象转换为响应模型
    # model_validate会自动映射字段并验证数据类型
    response_data = UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    # 返回统一格式的成功响应，包含token和用户信息
    return success_response(data=response_data)