from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from toutiao_app.models.news import Category



async def get_category(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()