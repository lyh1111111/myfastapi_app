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
from toutiao_app.curd.users import get_user_by_name, create_user, creat_token_user, authenticate_user
from toutiao_app.curd.users import update_user_info_curd, change_password
# 导入用户请求和响应数据模式
from toutiao_app.schemas.users import UserRegisterLoginRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
# 导入用户模型
from toutiao_app.models.users import User
from toutiao_app.utils.auth import get_current_user

# 导入成功响应工具函数
from toutiao_app.utils.response import success_response

# 创建API路由器实例，设置URL前缀为/api/user，标签为users
router = APIRouter(prefix="/api/user", tags=["users"])


# 定义用户注册接口，处理POST请求到/api/user/register
@router.post("/register")
async def register(users_data: UserRegisterLoginRequest, db: AsyncSession = Depends(post_dbs)):
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


@router.post("/login")
async def login(users_data: UserRegisterLoginRequest, db: AsyncSession = Depends(post_dbs)):
    user = await authenticate_user(db, users_data.username, users_data.password)
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token = await creat_token_user(db, user.id)
    response_data = UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    return success_response(data=response_data)


@router.get("/info")
async def get_user_info(current_user: User = Depends(get_current_user)):

    # 将ORM对象转换为响应模型，自动过滤敏感字段
    user_info = UserInfoResponse.model_validate(current_user)
    return success_response(data=user_info)


@router.put("/update")
async def update_user_info(
        user_data: UserUpdateRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(post_dbs)
):

    # 调用CURD层更新用户信息
    updated_user = await update_user_info_curd(db, current_user.username, user_data)
        
    # 转换为响应模型并返回
    return success_response(data=UserInfoResponse.model_validate(updated_user))

@router.put("/password")
async def update_password(
        password_data: UserChangePasswordRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(post_dbs)
):
    res_change_password = await change_password(db, current_user, password_data.oldPassword, password_data.newPassword)
    if not res_change_password:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败")
    
    return success_response(data=True)



    
