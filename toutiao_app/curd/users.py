# 导入uuid模块，用于生成唯一标识符
import uuid
# 导入日期时间相关类，用于处理令牌过期时间
from datetime import datetime, timedelta

# 从SQLAlchemy导入select语句构造器
from sqlalchemy import select
# 导入异步会话类型注解
from sqlalchemy.ext.asyncio import AsyncSession
# 导入用户和令牌数据模型
from toutiao_app.models.users import User, UserToken
# 导入用户请求数据模式
from toutiao_app.schemas.users import UserRequest
# 导入密码加密工具函数
from toutiao_app.utils.security import *


async def get_user_by_name(db: AsyncSession, username: str):
    """
    根据用户名查询用户
    
    Args:
        db: 数据库会话对象
        username: 要查询的用户名
        
    Returns:
        返回User对象，如果用户不存在则返回None
    """
    # 构造SELECT查询语句，筛选username字段等于传入值的记录
    Query = select(User).where(User.username == username)
    # 执行查询并等待结果
    result = await db.execute(Query)
    # 获取查询结果的第一条记录并返回
    return result.scalars().first()


async def create_user(db: AsyncSession, user_data: UserRequest):
    """
    创建新用户
    
    Args:
        db: 数据库会话对象
        user_data: 包含用户名和密码的注册数据
        
    Returns:
        返回创建成功的User对象
    """
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
    """
    创建或更新用户认证令牌

    Args:
        db: 数据库会话对象
        user_id: 用户ID

    Returns:
        返回生成的令牌字符串
    """
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