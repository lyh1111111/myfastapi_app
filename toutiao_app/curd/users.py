# 导入uuid模块用于生成唯一标识符
import uuid
# 导入日期时间类用于处理令牌过期时间
from datetime import datetime, timedelta

# 从SQLAlchemy导入查询构造器和更新语句
from sqlalchemy import select, update
# 导入异步会话类型注解
from sqlalchemy.ext.asyncio import AsyncSession
# 导入当前用户函数（未使用）
from sqlalchemy.sql.functions import current_user
# 导入HTTP异常类
from starlette.exceptions import HTTPException

# 导入用户和令牌数据模型
from toutiao_app.models.users import User, UserToken
# 导入用户请求和响应数据模式
from toutiao_app.schemas.users import UserRegisterLoginRequest, UserUpdateRequest, UserChangePasswordRequest, \
    UserInfoResponse
# 导入密码加密工具函数
from toutiao_app.utils.security import *


# 根据用户名查询用户的函数
async def get_user_by_username(db: AsyncSession, username: str):
    # 构造SELECT查询语句筛选指定用户名的记录
    query = select(User).where(User.username == username)
    # 执行查询并等待结果
    result = await db.execute(query)
    # 获取查询结果的第一条记录
    return result.scalars().first()


# 创建新用户的函数
async def create_user(db: AsyncSession, user_data: UserRegisterLoginRequest):
    # 调用密码加密函数将明文密码转换为哈希值
    hashed_password = hash_password(user_data.password)
    # 创建User实例设置用户名和加密后的密码
    user = User(username=user_data.username, password=hashed_password)
    # 将新用户对象添加到数据库会话中
    db.add(user)
    # 提交事务将数据写入数据库
    await db.commit()
    # 刷新用户对象获取数据库生成的自增ID等字段
    await db.refresh(user)
    # 返回创建成功的用户对象
    return user


# 为用户创建或更新令牌的函数
async def create_user_token(db: AsyncSession, user_id: str):
    # 生成UUID作为唯一的令牌值
    token = str(uuid.uuid4())
    # 计算令牌过期时间为当前时间加上7天
    expire_at = datetime.now() + timedelta(days=7)
    # 构造查询语句查找该用户是否已有令牌记录
    query = select(UserToken).where(UserToken.user_id == user_id)
    # 执行查询并等待结果
    result = await db.execute(query)
    # 获取查询结果的第一条记录
    user_token = result.scalars().first()

    # 判断用户是否已存在令牌记录
    if user_token:
        # 如果存在则更新令牌值和过期时间
        user_token.token = token
        user_token.expires_at = expire_at
    else:
        # 如果不存在则创建新的令牌记录
        user_token = UserToken(user_id=user_id, token=token, expires_at=expire_at)
        # 将新令牌对象添加到会话中
        db.add(user_token)
        # 提交事务到数据库
        await db.commit()
    # 返回生成的令牌字符串
    return token


# 验证用户账号和密码的函数
async def authenticate_user(db: AsyncSession, username: str, password: str):
    # 根据用户名查询用户
    user = await get_user_by_username(db, username)
    # 如果用户不存在则返回None
    if not user:
        return None
    # 使用密码验证函数验证密码是否正确
    if not verify_password(password, user.password):
        return None
    # 返回验证成功的用户对象
    return user


# 根据Token查询用户的函数
async def get_user_by_token(db: AsyncSession, token: str):
    # 构造查询语句查找指定token的记录
    query = select(UserToken).where(UserToken.token == token)
    # 执行查询并等待结果
    result = await db.execute(query)
    # 获取查询结果的第一条记录
    db_token = result.scalar_one_or_none()
    # 如果令牌不存在或已过期则返回None
    if not db_token or db_token.expires_at < datetime.now():
        return None
    # 根据令牌中的user_id查询用户
    query = select(User).where(User.id == db_token.user_id)
    # 执行查询并等待结果
    result = await db.execute(query)
    # 返回查询到的用户对象
    return result.scalar_one_or_none()


# 更新用户信息的函数
async def update_user_info(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    # 构造UPDATE语句更新指定用户名的记录
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        # 排除未设置的字段
        exclude_unset=True,
        # 排除值为None的字段
        exclude_none=True
    ))
    # 执行更新查询并等待结果
    result = await db.execute(query)
    # 提交事务使更新生效
    await db.commit()
    # 检查是否命中数据如果没有则抛出404异常
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    # 查询更新后的用户对象
    updated_user = await get_user_by_username(db, username)
    # 返回更新成功的用户对象
    return updated_user


# 修改用户密码的函数
async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    # 验证旧密码是否正确
    if not verify_password(old_password, user.password):
        # 如果旧密码错误则返回False
        return False
    # 对新密码进行加密
    hashed_new_password = hash_password(new_password)
    # 更新用户对象的密码字段
    user.password = hashed_new_password
    # 将用户对象添加到会话中
    db.add(user)
    # 提交事务使更改生效
    await db.commit()
    # 刷新用户对象获取最新数据
    await db.refresh(user)
    # 返回成功标志
    return True
