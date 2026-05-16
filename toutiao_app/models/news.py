from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Index, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import functions


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


class Category(Base):
    __tablename__ = "news_category"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分类ID", )
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="分类名称", )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="排序", )

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, sort_order={self.sort_order})>"


class News(Base):
    __tablename__ = "news"
    # 创建索引
    __table_args__ = (
        Index("fk_news_category_idx", "category_id"),
        Index("fk_news_created_at_idx", "created_at")
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="标题")
    description: Mapped[str] = mapped_column(String(500), nullable=False, comment="描述")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="内容")
    image: Mapped[str] = mapped_column(String(255), nullable=False, comment="图片")
    author: Mapped[str] = mapped_column(String(50), nullable=False, comment="作者")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("news_category.id"), nullable=False, comment="分类ID")
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="浏览量")
    publish_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), nullable=False, comment="发布时间")

    def __repr__(self):
        return f"<News(id={self.id}, title={self.title}, category_id={self.views})>"
