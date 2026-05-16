from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import functions
from sqlalchemy.sql.schema import Index


class Base(DeclarativeBase):
   created_at: Mapped[datetime] = mapped_column(
       DateTime,
       server_default=functions.now(),
       default=functions.now(),
       comment="创建时间",
   )
   updated_at: Mapped[datetime] = mapped_column(
       DateTime,
       server_default=functions.now(),
       onupdate=functions.now(),
       comment="更新时间",
   )

class User(Base):

    __tablename__ = "user"

    __table_args__ = (
        Index("username_UNIQUE", "username"),
        Index("phone_UNIQUE", "phone")
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码（加密存储）")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="头像URL",default="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg")
    gender: Mapped[Optional[str]] = mapped_column(Enum("male", "female","unknown"), default="unknown", nullable=True, comment="性别",)
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="个人简介",default="这个人很懒,什么也没留下")
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True,nullable=True, comment="手机号")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, nickname={self.nickname}, avatar={self.avatar}, gender={self.gender}, bio={self.bio}, phone={self.phone})>"

    