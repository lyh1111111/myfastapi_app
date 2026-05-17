# 导入uuid模块，用于生成唯一标识符
import uuid
# 导入日期时间相关类，用于处理令牌过期时间
from datetime import datetime, timedelta

# 从SQLAlchemy导入select语句构造器
from sqlalchemy import select, update
# 导入异步会话类型注解
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import current_user
from starlette.exceptions import HTTPException

# 导入用户和令牌数据模型
from toutiao_app.models.users import User, UserToken
# 导入用户请求数据模式
from toutiao_app.schemas.users import UserRegisterLoginRequest, UserUpdateRequest, UserChangePasswordRequest, \
    UserInfoResponse
# 导入密码加密工具函数
from toutiao_app.utils.security import *


async def get_user_by_name(db: AsyncSession, username: str):
    # 构造SELECT查询语句，筛选username字段等于传入值的记录
    Query = select(User).where(User.username == username)
    # 执行查询并等待结果
    result = await db.execute(Query)
    # 获取查询结果的第一条记录并返回
    return result.scalars().first()


async def create_user(db: AsyncSession, user_data: UserRegisterLoginRequest):
    # 调用密码加密函数，将明文密码转换为哈希值
    hashed_password = hash_password(user_data.password)
    # 创建User实例，设置用户名和加密后的密码
    user = User(username=user_data.username, password=hashed_password)
    # 将新用户对象添加到数据库会话中
    db.add(user)
    # 提交事务，将数据写入数据库
    await db.commit()
    # 刷新用户对象，获取数据库生成的自增ID等字段
    await db.refresh(user)
    # 返回创建成功的用户对象
    return user


async def creat_token_user(db: AsyncSession, user_id: str):
    # 生成UUID作为唯一的令牌值
    token = str(uuid.uuid4())
    # 计算令牌过期时间，当前时间加上7天
    expire_at = datetime.now() + timedelta(days=7)
    # 构造查询语句，查找该用户是否已有令牌记录
    query = select(UserToken).where(UserToken.user_id == user_id)
    # 执行查询并等待结果
    result = await db.execute(query)
    # 获取查询结果的第一条记录
    user_token = result.scalars().first()

    # 判断用户是否已存在令牌记录
    if user_token:
        # 如果存在，更新令牌值和过期时间
        user_token.token = token
        user_token.expires_at = expire_at
    else:
        # 如果不存在，创建新的令牌记录
        user_token = UserToken(user_id=user_id, token=token, expires_at=expire_at)
        # 将新令牌对象添加到会话中
        db.add(user_token)
        # 提交事务到数据库
        await db.commit()
    # 返回生成的令牌字符串
    return token


async def authenticate_user(db: AsyncSession, username: str, password: str):
    # 根据用户名查询用户
    user = await get_user_by_name(db, username)
    # 如果用户不存在，返回None
    if not user:
        return None
    # 使用密码验证函数验证密码
    if not verify_password(password, user.password):
        return None
    # 返回验证成功的用户对象
    return user


# 根据Token查询用户：验证Token→查询用户
async def get_user_by_token(db: AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()
    if not db_token or db_token.expires_at < datetime.now():
        return None
    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_user_info_curd(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    # 构造查询语句，查找该用户ID对应的用户记录
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    # 执行查询并等待结果
    result = await db.execute(query)
    await db.commit()
    # 检查是否命中数据
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    # 返回更新成功的用户对象
    update_user = await get_user_by_name(db, username)
    return update_user


async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    if not verify_password(old_password, user.password):
        return False
    hashed_new_password = hash_password(new_password)
    user.password = hashed_new_password
    db.add(user)
    await db.commit()
    db.refresh(user)
    return True
