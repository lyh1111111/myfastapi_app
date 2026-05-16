# 从datetime模块导入日期时间类，用于处理时间字段
from datetime import datetime
# 从typing模块导入Optional类型注解，表示字段可以为空
from typing import Optional

# 从SQLAlchemy导入各种字段类型和约束
from sqlalchemy import Enum, Integer, String, DateTime, ForeignKey
# 从SQLAlchemy ORM模块导入声明式基类和映射工具
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# 从SQLAlchemy SQL模块导入内置函数（如now()）
from sqlalchemy.sql import functions
# 从SQLAlchemy schema模块导入索引构造器
from sqlalchemy.sql.schema import Index


# 定义ORM基类，所有模型类都继承自此类
class Base(DeclarativeBase):
    """
    基础模型类，提供创建时间和更新时间字段
    """
    # 定义创建时间字段，使用数据库服务器默认值
    created_at: Mapped[datetime] = mapped_column(
        # 指定字段类型为DateTime
        DateTime,
        # 设置数据库层面的默认值为当前时间
        server_default=functions.now(),
        # 设置Python层面的默认值为当前时间
        default=functions.now(),
        # 添加字段注释说明
        comment="创建时间",
    )
    # 定义更新时间字段，记录最后一次修改的时间
    updated_at: Mapped[datetime] = mapped_column(
        # 指定字段类型为DateTime
        DateTime,
        # 设置数据库层面的默认值为当前时间
        server_default=functions.now(),
        # 当记录更新时自动更新为当前时间
        onupdate=functions.now(),
        # 添加字段注释说明
        comment="更新时间",
    )

# 定义用户表模型类，继承自Base
class User(Base):
    """用户表模型"""

    # 指定数据库表名为"user"
    __tablename__ = "user"

    # 定义表的额外参数，如索引
    __table_args__ = (
        # 为用户名字段创建唯一索引，加速查询并保证唯一性
        Index("username_UNIQUE", "username"),
        # 为手机号字段创建唯一索引，加速查询并保证唯一性
        Index("phone_UNIQUE", "phone")
    )

    # 定义用户ID字段，作为主键并自动递增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    # 定义用户名字段，必须唯一且不能为空
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    # 定义密码字段，存储加密后的哈希值，长度为255
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码（加密存储）")
    # 定义昵称字段，可以为空
    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="昵称")
    # 定义头像URL字段，设置默认头像地址
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="头像URL", default="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg")
    # 定义性别字段，使用枚举类型限制为male/female/unknown
    gender: Mapped[Optional[str]] = mapped_column(Enum("male", "female", "unknown"), default="unknown", nullable=True, comment="性别")
    # 定义个人简介字段，设置默认提示文本
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="个人简介", default="这个人很懒,什么也没留下")
    # 定义手机号字段，必须唯一且可以为空
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, comment="手机号")

    # 定义对象的字符串表示方法，用于调试和日志输出
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, nickname={self.nickname}, avatar={self.avatar}, gender={self.gender}, bio={self.bio}, phone={self.phone})>"

# 定义用户令牌表模型类，用于存储认证token
class UserToken(Base):
    """用户Token表模型"""

    # 指定数据库表名为"user_token"
    __tablename__ = "user_token"

    # 定义表的额外参数，如索引
    __table_args__ = (
        # 为token字段创建唯一索引，加速查询
        Index("token_UNIQUE", "token"),
        # 为user_id字段创建普通索引，加速关联查询
        Index("fk_user_token_idx", "user_id")
    )

    # 定义令牌ID字段，作为主键并自动递增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="令牌ID")
    # 定义用户ID字段，作为外键关联到user表
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    # 定义令牌值字段，存储UUID字符串
    token: Mapped[str] = mapped_column(String(255), nullable=False, comment="令牌值")
    # 定义过期时间字段，记录令牌的有效期限
    expires_at: Mapped[datetime] = mapped_column(
        # 指定字段类型为DateTime
        DateTime,
        # 该字段不能为空
        nullable=False,
        # 设置数据库层面的默认值为当前时间
        server_default=functions.now(),
        # 添加字段注释说明
        comment="过期时间",
    )
    # 定义创建时间字段，记录令牌的生成时间
    created_at: Mapped[datetime] = mapped_column(
        # 指定字段类型为DateTime
        DateTime,
        # 该字段不能为空
        nullable=False,
        # 设置数据库层面的默认值为当前时间
        server_default=functions.now(),
        # 设置Python层面的默认值为当前时间
        default=functions.now(),
        # 添加字段注释说明
        comment="创建时间",
    )

    # 定义对象的字符串表示方法，用于调试和日志输出
    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id}, token={self.token}, expires_at={self.expires_at}, created_at={self.created_at})>"