"""
SQLAlchemy 书籍数据查询操作完整示例
每个查询操作都对应一个独立的路由接口
"""
from datetime import datetime, date
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String, Date, Float, func, select, and_, or_, not_, asc, desc
from fastapi import Depends
from typing import List, Optional


# ==========================================
# 1. 创建异步数据库引擎
# ==========================================
engine = create_async_engine(
    "mysql+aiomysql://root:123456@localhost:3306/fastapi_test?charset=utf8mb3",
    echo=True,
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=10,
    pool_recycle=3600
)


# ==========================================
# 2. 定义基础模型类
# ==========================================
class Base(DeclarativeBase):
    """基础模型类，包含创建时间和更新时间"""
    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )


# ==========================================
# 3. 定义请求体模型（Pydantic）
# ==========================================
class BookCreate(BaseModel):
    """创建书籍的请求体"""
    auther: str = Field(..., max_length=50, description="作者")
    title: str = Field(..., max_length=100, description="书名")
    published_date: date = Field(..., description="出版日期")
    price: float = Field(..., gt=0, description="价格")
    description: Optional[str] = Field(None, max_length=255, description="描述")


class BookUpdate(BaseModel):
    """更新书籍的请求体"""
    auther: Optional[str] = Field(None, max_length=50, description="作者")
    title: Optional[str] = Field(None, max_length=100, description="书名")
    published_date: Optional[date] = Field(None, description="出版日期")
    price: Optional[float] = Field(None, gt=0, description="价格")
    description: Optional[str] = Field(None, max_length=255, description="描述")


class BookBatchCreate(BaseModel):
    """批量创建书籍的请求体"""
    books: List[BookCreate] = Field(..., min_items=1, max_items=100, description="书籍列表")


# ==========================================
# 4. 定义书籍表模型
# ==========================================
class Book(Base):
    """书籍模型类"""
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment="书籍ID")
    auther: Mapped[str] = mapped_column(String(50), comment="作者")
    title: Mapped[str] = mapped_column(String(100), comment="书名")
    published_date: Mapped[datetime] = mapped_column(Date, comment="出版日期")
    price: Mapped[float] = mapped_column(Float, comment="价格")
    description: Mapped[str] = mapped_column(String(255), comment="描述")


# ==========================================
# 5. 创建数据库表
# ==========================================
async def create_tables():
    """创建所有数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ==========================================
# 6. 应用生命周期管理
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时的生命周期管理"""
    # 启动时执行
    await create_tables()
    print("数据库表创建成功")
    yield
    # 关闭时执行（清理操作）
    print("应用关闭")


app = FastAPI(lifespan=lifespan, title="书籍查询API", description="SQLAlchemy查询操作完整示例")


# ==========================================
# 7. 创建数据库会话工厂
# ==========================================
Async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


# ==========================================
# 8. 数据库依赖项
# ==========================================
async def get_db():
    """获取数据库会话的依赖项"""
    async with Async_session() as session:
        try:
            yield session
        except Exception as e:
            print(f"数据库会话出错: {e}")
            await session.rollback()
            raise e
        finally:
            await session.close()


# ==========================================
# 9. 首页路由
# ==========================================
@app.get("/")
async def read_root():
    """首页"""
    return {
        "message": "欢迎使用书籍查询API",
        "docs": "/docs",
        "total_routes": 30,
        "post_routes": [
            "/books/create - 创建单本书籍",
            "/books/create-batch - 批量创建书籍",
            "/books/update/{book_id} - 更新书籍",
            "/books/delete/{book_id} - 删除书籍"
        ]
    }


# ==========================================
# 9. 基本比较操作符查询
# ==========================================

@app.get("/books")
async def get_all_books(db: AsyncSession = Depends(get_db)):
    """查询所有书籍"""
    result = await db.execute(select(Book))
    books = result.scalars().all()
    return {"count": len(books), "data": books}


@app.get("/books/equal")
async def get_books_by_equal_price(price: float = Query(..., description="价格"), db: AsyncSession = Depends(get_db)):
    """等于查询：查询价格等于指定值的书籍"""
    result = await db.execute(select(Book).where(Book.price == price))
    books = result.scalars().all()
    return {"count": len(books), "price": price, "data": books}


@app.get("/books/not-equal")
async def get_books_by_not_equal_price(price: float = Query(..., description="价格"), db: AsyncSession = Depends(get_db)):
    """不等于查询：查询价格不等于指定值的书籍"""
    result = await db.execute(select(Book).where(Book.price != price))
    books = result.scalars().all()
    return {"count": len(books), "data": books}


@app.get("/books/greater-than")
async def get_books_by_greater_price(price: float = Query(..., description="价格"), db: AsyncSession = Depends(get_db)):
    """大于查询：查询价格大于指定值的书籍"""
    result = await db.execute(select(Book).where(Book.price > price))
    books = result.scalars().all()
    return {"count": len(books), "data": books}


@app.get("/books/less-than")
async def get_books_by_less_price(price: float = Query(..., description="价格"), db: AsyncSession = Depends(get_db)):
    """小于查询：查询价格小于指定值的书籍"""
    result = await db.execute(select(Book).where(Book.price < price))
    books = result.scalars().all()
    return {"count": len(books), "data": books}


# ==========================================
# 10. 逻辑操作符查询 (AND, OR, NOT)
# ==========================================

@app.get("/books/and-query")
async def get_books_by_and(
    min_price: float = Query(..., description="最低价格"),
    max_price: float = Query(..., description="最高价格"),
    db: AsyncSession = Depends(get_db)
):
    """AND查询：查询价格在指定范围内的书籍"""
    result = await db.execute(
        select(Book).where(and_(Book.price >= min_price, Book.price <= max_price))
    )
    books = result.scalars().all()
    return {"count": len(books), "min_price": min_price, "max_price": max_price, "data": books}


@app.get("/books/or-query")
async def get_books_by_or(
    author: str = Query(..., description="作者"),
    min_price: float = Query(..., description="最低价格"),
    db: AsyncSession = Depends(get_db)
):
    """OR查询：查询指定作者或价格高于指定值的书籍"""
    result = await db.execute(
        select(Book).where(or_(Book.auther == author, Book.price > min_price))
    )
    books = result.scalars().all()
    return {"count": len(books), "data": books}


@app.get("/books/not-query")
async def get_books_by_not(
    max_price: float = Query(..., description="最高价格"),
    db: AsyncSession = Depends(get_db)
):
    """NOT查询：查询价格不高于指定值的书籍"""
    result = await db.execute(
        select(Book).where(not_(Book.price > max_price))
    )
    books = result.scalars().all()
    return {"count": len(books), "data": books}


# ==========================================
# 11. 模糊查询 (LIKE)
# ==========================================

@app.get("/books/like")
async def get_books_by_like(
    keyword: str = Query(..., description="搜索关键词"),
    db: AsyncSession = Depends(get_db)
):
    """模糊查询：查询书名包含关键词的书籍"""
    result = await db.execute(
        select(Book).where(Book.title.like(f"%{keyword}%"))
    )
    books = result.scalars().all()
    return {"count": len(books), "keyword": keyword, "data": books}


@app.get("/books/startswith")
async def get_books_by_startswith(
    prefix: str = Query(..., description="开头字符"),
    db: AsyncSession = Depends(get_db)
):
    """开头匹配：查询书名以指定字符开头的书籍"""
    result = await db.execute(
        select(Book).where(Book.title.like(f"{prefix}%"))
    )
    books = result.scalars().all()
    return {"count": len(books), "prefix": prefix, "data": books}


@app.get("/books/endswith")
async def get_books_by_endswith(
    suffix: str = Query(..., description="结尾字符"),
    db: AsyncSession = Depends(get_db)
):
    """结尾匹配：查询书名以指定字符结尾的书籍"""
    result = await db.execute(
        select(Book).where(Book.title.like(f"%{suffix}"))
    )
    books = result.scalars().all()
    return {"count": len(books), "suffix": suffix, "data": books}


# ==========================================
# 12. 范围查询 (BETWEEN, IN)
# ==========================================

@app.get("/books/between")
async def get_books_by_between(
    min_price: float = Query(..., description="最低价格"),
    max_price: float = Query(..., description="最高价格"),
    db: AsyncSession = Depends(get_db)
):
    """BETWEEN查询：查询价格在指定范围内的书籍"""
    result = await db.execute(
        select(Book).where(Book.price.between(min_price, max_price))
    )
    books = result.scalars().all()
    return {"count": len(books), "min_price": min_price, "max_price": max_price, "data": books}


@app.get("/books/in-list")
async def get_books_by_in_list(
    authors: str = Query(..., description="作者列表，用逗号分隔，例如：鲁迅,老舍,巴金"),
    db: AsyncSession = Depends(get_db)
):
    """IN查询：查询指定作者列表中的书籍"""
    author_list = [a.strip() for a in authors.split(",")]
    result = await db.execute(
        select(Book).where(Book.auther.in_(author_list))
    )
    books = result.scalars().all()
    return {"count": len(books), "authors": author_list, "data": books}


# ==========================================
# 13. NULL 值查询
# ==========================================

@app.get("/books/is-null")
async def get_books_with_null_description(db: AsyncSession = Depends(get_db)):
    """IS NULL查询：查询描述为空的书籍"""
    result = await db.execute(
        select(Book).where(Book.description.is_(None))
    )
    books = result.scalars().all()
    return {"count": len(books), "data": books}


@app.get("/books/is-not-null")
async def get_books_with_not_null_description(db: AsyncSession = Depends(get_db)):
    """IS NOT NULL查询：查询描述不为空的书籍"""
    result = await db.execute(
        select(Book).where(Book.description.isnot(None))
    )
    books = result.scalars().all()
    return {"count": len(books), "data": books}


# ==========================================
# 14. 排序查询 (ORDER BY)
# ==========================================

@app.get("/books/order-by-price-asc")
async def get_books_order_by_price_asc(db: AsyncSession = Depends(get_db)):
    """升序排序：按价格从低到高排序"""
    result = await db.execute(select(Book).order_by(asc(Book.price)))
    books = result.scalars().all()
    return {"count": len(books), "data": books}


@app.get("/books/order-by-price-desc")
async def get_books_order_by_price_desc(db: AsyncSession = Depends(get_db)):
    """降序排序：按价格从高到低排序"""
    result = await db.execute(select(Book).order_by(desc(Book.price)))
    books = result.scalars().all()
    return {"count": len(books), "data": books}


@app.get("/books/order-by-multi")
async def get_books_order_by_multi(db: AsyncSession = Depends(get_db)):
    """多字段排序：先按作者升序，再按价格降序"""
    result = await db.execute(select(Book).order_by(asc(Book.auther), desc(Book.price)))
    books = result.scalars().all()
    return {"count": len(books), "data": books}


# ==========================================
# 15. 分页查询 (LIMIT, OFFSET)
# ==========================================

@app.get("/books/paginated")
async def get_books_paginated(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """分页查询：获取指定页码的书籍"""
    offset = (page - 1) * page_size
    result = await db.execute(select(Book).offset(offset).limit(page_size))
    books = result.scalars().all()
    return {"page": page, "page_size": page_size, "data": books}


# ==========================================
# 16. 聚合函数查询
# ==========================================

@app.get("/books/count")
async def get_books_count(db: AsyncSession = Depends(get_db)):
    """COUNT查询：统计书籍总数"""
    result = await db.execute(select(func.count(Book.id)))
    count = result.scalar()
    return {"total_books": count}


@app.get("/books/sum-price")
async def get_books_sum_price(db: AsyncSession = Depends(get_db)):
    """SUM查询：计算所有书籍的总价格"""
    result = await db.execute(select(func.sum(Book.price)))
    total = result.scalar()
    return {"total_price": total}


@app.get("/books/avg-price")
async def get_books_avg_price(db: AsyncSession = Depends(get_db)):
    """AVG查询：计算书籍的平均价格"""
    result = await db.execute(select(func.avg(Book.price)))
    avg = result.scalar()
    return {"average_price": avg}


@app.get("/books/max-price")
async def get_books_max_price(db: AsyncSession = Depends(get_db)):
    """MAX查询：查询最高价格的书籍"""
    result = await db.execute(select(func.max(Book.price)))
    max_price = result.scalar()
    return {"max_price": max_price}


@app.get("/books/min-price")
async def get_books_min_price(db: AsyncSession = Depends(get_db)):
    """MIN查询：查询最低价格的书籍"""
    result = await db.execute(select(func.min(Book.price)))
    min_price = result.scalar()
    return {"min_price": min_price}


# ==========================================
# 17. 分组查询 (GROUP BY, HAVING)
# ==========================================

@app.get("/books/group-by-author")
async def get_books_group_by_author(db: AsyncSession = Depends(get_db)):
    """GROUP BY查询：按作者分组统计书籍数量"""
    result = await db.execute(
        select(Book.auther, func.count(Book.id))
        .group_by(Book.auther)
    )
    rows = result.all()
    return {"data": [{"author": author, "count": count} for author, count in rows]}


@app.get("/books/group-by-author-having")
async def get_books_group_by_author_having(
    min_count: int = Query(1, ge=1, description="最小数量"),
    db: AsyncSession = Depends(get_db)
):
    """HAVING查询：统计出版数量大于指定值的作者"""
    result = await db.execute(
        select(Book.auther, func.count(Book.id))
        .group_by(Book.auther)
        .having(func.count(Book.id) > min_count)
    )
    rows = result.all()
    return {"min_count": min_count, "data": [{"author": author, "count": count} for author, count in rows]}


# ==========================================
# 18. 日期查询
# ==========================================

@app.get("/books/after-date")
async def get_books_after_date(
    year: int = Query(..., description="年份"),
    month: int = Query(1, ge=1, le=12, description="月份"),
    day: int = Query(1, ge=1, le=31, description="日期"),
    db: AsyncSession = Depends(get_db)
):
    """日期比较：查询指定日期之后出版的书籍"""
    target_date = date(year, month, day)
    result = await db.execute(
        select(Book).where(Book.published_date > target_date)
    )
    books = result.scalars().all()
    return {"count": len(books), "after_date": str(target_date), "data": books}


@app.get("/books/date-range")
async def get_books_in_date_range(
    start_year: int = Query(..., description="开始年份"),
    end_year: int = Query(..., description="结束年份"),
    db: AsyncSession = Depends(get_db)
):
    """日期范围：查询指定年份范围内出版的书籍"""
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    result = await db.execute(
        select(Book).where(Book.published_date.between(start_date, end_date))
    )
    books = result.scalars().all()
    return {"count": len(books), "start_year": start_year, "end_year": end_year, "data": books}


@app.get("/books/by-year")
async def get_books_by_year(
    year: int = Query(..., description="年份"),
    db: AsyncSession = Depends(get_db)
):
    """年份查询：查询指定年份出版的书籍"""
    result = await db.execute(
        select(Book).where(func.year(Book.published_date) == year)
    )
    books = result.scalars().all()
    return {"count": len(books), "year": year, "data": books}


# ==========================================
# 19. 字符串函数查询
# ==========================================

@app.get("/books/title-length")
async def get_books_by_title_length(
    min_length: int = Query(5, ge=1, description="最小标题长度"),
    db: AsyncSession = Depends(get_db)
):
    """字符串长度：查询书名长度大于指定值的书籍"""
    result = await db.execute(
        select(Book).where(func.length(Book.title) > min_length)
    )
    books = result.scalars().all()
    return {"count": len(books), "min_length": min_length, "data": books}


# ==========================================
# 20. 复杂组合查询
# ==========================================

@app.get("/books/complex-query")
async def get_books_complex_query(
    min_price: float = Query(30, description="最低价格"),
    max_price: float = Query(50, description="最高价格"),
    keyword: str = Query("", description="书名关键词"),
    after_year: int = Query(1990, description="出版年份"),
    db: AsyncSession = Depends(get_db)
):
    """
    复杂组合查询：
    - 价格在指定范围内
    - 书名包含关键词（可选）
    - 指定年份之后出版
    - 按价格降序排序
    """
    conditions = [
        Book.price.between(min_price, max_price),
        Book.published_date > date(after_year, 1, 1)
    ]
    
    # 如果提供了关键词，添加到条件中
    if keyword:
        conditions.append(Book.title.like(f"%{keyword}%"))
    
    result = await db.execute(
        select(Book).where(and_(*conditions)).order_by(desc(Book.price))
    )
    books = result.scalars().all()
    return {
        "count": len(books),
        "min_price": min_price,
        "max_price": max_price,
        "keyword": keyword,
        "after_year": after_year,
        "data": books
    }


@app.get("/books/search")
async def search_books(
    keyword: str = Query("", description="搜索关键词"),
    author: str = Query("", description="作者"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    db: AsyncSession = Depends(get_db)
):
    """
    综合搜索接口：
    支持多条件可选组合搜索
    """
    conditions = []
    
    if keyword:
        conditions.append(or_(
            Book.title.like(f"%{keyword}%"),
            Book.description.like(f"%{keyword}%")
        ))
    
    if author:
        conditions.append(Book.auther.like(f"%{author}%"))
    
    if min_price is not None:
        conditions.append(Book.price >= min_price)
    
    if max_price is not None:
        conditions.append(Book.price <= max_price)
    
    # 如果有条件则添加where，否则查询所有
    if conditions:
        result = await db.execute(select(Book).where(and_(*conditions)))
    else:
        result = await db.execute(select(Book))
    
    books = result.scalars().all()
    return {"count": len(books), "data": books}


@app.get("/books/{book_id}")
async def get_book_by_id(book_id: int, db: AsyncSession = Depends(get_db)):
    """根据ID查询单本书籍"""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    if not book:
        return {"error": "书籍不存在"}
    return book


# ==========================================
# 21. POST 请求 - 创建数据
# ==========================================

@app.post("/books/create")
async def create_book(book_data: BookCreate, db: AsyncSession = Depends(get_db)):
    """
    POST请求 - 创建单本书籍
    
    请求体示例：
    {
        "auther": "张三",
        "title": "Python编程",
        "published_date": "2024-01-01",
        "price": 59.9,
        "description": "一本关于Python编程的书"
    }
    """
    # 创建书籍对象
    new_book = Book(
        auther=book_data.auther,
        title=book_data.title,
        published_date=book_data.published_date,
        price=book_data.price,
        description=book_data.description
    )
    
    # 添加到数据库
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    
    return {
        "message": "书籍创建成功",
        "data": new_book
    }


@app.post("/books/create-batch")
async def create_books_batch(batch_data: BookBatchCreate, db: AsyncSession = Depends(get_db)):
    """
    POST请求 - 批量创建书籍
    
    请求体示例：
    {
        "books": [
            {
                "auther": "张三",
                "title": "Python编程",
                "published_date": "2024-01-01",
                "price": 59.9,
                "description": "Python入门教程"
            },
            {
                "auther": "李四",
                "title": "Java编程",
                "published_date": "2024-02-01",
                "price": 69.9,
                "description": "Java入门教程"
            }
        ]
    }
    """
    # 创建书籍对象列表
    new_books = [
        Book(
            auther=book.auther,
            title=book.title,
            published_date=book.published_date,
            price=book.price,
            description=book.description
        )
        for book in batch_data.books
    ]
    
    # 批量添加到数据库
    db.add_all(new_books)
    await db.commit()
    
    # 刷新所有对象以获取ID
    for book in new_books:
        await db.refresh(book)
    
    return {
        "message": f"成功创建 {len(new_books)} 本书籍",
        "count": len(new_books),
        "data": new_books
    }


# ==========================================
# 22. PUT 请求 - 更新数据
# ==========================================

@app.put("/books/update/{book_id}")
async def update_book(
    book_id: int, 
    book_data: BookUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """
    PUT请求 - 更新书籍信息
    
    请求体示例（只更新需要修改的字段）：
    {
        "price": 79.9,
        "description": "更新后的描述"
    }
    """
    # 查询书籍是否存在
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    
    # 更新字段（只更新提供的字段）
    if book_data.auther is not None:
        book.auther = book_data.auther
    if book_data.title is not None:
        book.title = book_data.title
    if book_data.published_date is not None:
        book.published_date = book_data.published_date
    if book_data.price is not None:
        book.price = book_data.price
    if book_data.description is not None:
        book.description = book_data.description
    
    # 提交更新
    await db.commit()
    await db.refresh(book)
    
    return {
        "message": "书籍更新成功",
        "data": book
    }


# ==========================================
# 23. DELETE 请求 - 删除数据
# ==========================================

@app.delete("/books/delete/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    """
    DELETE请求 - 删除书籍
    
    返回：
    - 成功：返回删除的书籍信息
    - 失败：返回404错误
    """
    # 查询书籍是否存在
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    
    # 删除书籍
    await db.delete(book)
    await db.commit()
    
    return {
        "message": "书籍删除成功",
        "deleted_book": {
            "id": book.id,
            "title": book.title,
            "auther": book.auther
        }
    }


@app.delete("/books/delete-batch")
async def delete_books_batch(
    book_ids: List[int] = Query(..., description="要删除的书籍ID列表"),
    db: AsyncSession = Depends(get_db)
):
    """
    DELETE请求 - 批量删除书籍
    
    参数：
    - book_ids: 要删除的书籍ID列表，例如：?book_ids=1&book_ids=2&book_ids=3
    """
    # 查询所有要删除的书籍
    result = await db.execute(select(Book).where(Book.id.in_(book_ids)))
    books = result.scalars().all()
    
    if not books:
        raise HTTPException(status_code=404, detail="没有找到要删除的书籍")
    
    # 删除所有书籍
    for book in books:
        await db.delete(book)
    
    await db.commit()
    
    return {
        "message": f"成功删除 {len(books)} 本书籍",
        "deleted_count": len(books),
        "deleted_ids": [book.id for book in books]
    }


# ==========================================
# 启动应用
# ==========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
