from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from toutiao_app.models.news import *



async def get_category(db: AsyncSession, skip: int , limit: int ):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news(db: AsyncSession, category_id: int, skip: int , limit: int):
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news_count(db: AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()
