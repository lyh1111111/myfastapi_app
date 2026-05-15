# 导入FastAPI路由模块
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from toutiao_app.config.db_conf import post_dbs
from toutiao_app.curd.news import get_category

# 创建API路由器实例，设置路由前缀和标签
router = APIRouter(prefix="/api/news", tags=["news"])

# 定义获取新闻分类的GET接口
@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(post_dbs),skip: int = 0, limit: int = 100):
    categories = await get_category(db, skip, limit)
    return {
        "code": 200,
        "message": "success",
        "data": categories
    }
