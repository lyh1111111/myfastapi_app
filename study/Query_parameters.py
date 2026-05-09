# 从 fastapi 框架导入 FastAPI 类和 Query 参数校验工具
from fastapi import FastAPI,  Query
# 导入 uvicorn 服务器，用于运行 FastAPI 应用
import uvicorn

# 1. 创建 FastAPI 实例
# title 参数会在自动生成的 API 文档中显示为标题
app = FastAPI(title="我的图书管理 API")


# 定义新闻列表接口，使用查询参数进行分页
# 访问地址示例：http://127.0.0.1:8000/news/news_list?skip=5&limit=20
@app.get("/news/news_list")
async def get_news_list(
        # skip: 查询参数，表示起始页码偏移量，默认为 0，必须小于 10
        skip: int = Query(0, lt=10, description="默认的起始页"),
        # limit: 查询参数，表示每页数量，默认为 10，必须小于 100
        limit: int = Query(10, lt=100, description="最大的页码")):
    """
    获取新闻列表 - 支持分页查询
    
    查询参数:
        skip (int): 起始位置偏移量，默认值为 0，必须小于 10
        limit (int): 返回数量限制，默认值为 10，必须小于 100
        
    返回:
        dict: 包含 skip 和 limit 参数的 JSON 对象（实际应用中应返回新闻列表数据）
    """
    return {"skip": skip, "limit": limit}


# 启动配置
if __name__ == "__main__":
    # 强制指定 127.0.0.1 避免之前的 127.0.0.0 错误
    # host: 监听地址，127.0.0.1 表示仅本地访问
    # port: 监听端口号，8000 是 FastAPI 默认端口
    uvicorn.run(app, host="127.0.0.1", port=8000)