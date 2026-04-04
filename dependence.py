# 从 fastapi 框架导入 FastAPI 类和 Query 参数校验工具
from fastapi import FastAPI, Query
# 导入 Depends 依赖注入工具，用于声明接口之间的依赖关系
from fastapi import Depends

# 创建 FastAPI 应用实例
app = FastAPI()


# 定义根路径的 GET 请求处理函数
@app.get("/")
def read_root():
    """
    根路径接口，返回简单的问候消息
    
    返回:
        dict: 包含 Hello World 消息的 JSON 对象
    """
    return {"Hello": "World"}


# 定义公共参数处理函数，用于依赖注入
# 这是一个异步函数，会被其他接口依赖使用
async def common_parameters(q: str = None, skip: int = Query(0, title="Skip parameter"),
                            limit: int = Query(10, title="Limit parameter"), description="Common parameters"):
    """
    公共参数处理器 - 作为依赖项被其他接口使用
    
    查询参数:
        q (str, optional): 搜索关键词，默认为 None
        skip (int): 起始位置偏移量，默认值为 0，标题为"Skip parameter"
        limit (int): 返回数量限制，默认值为 10，标题为"Limit parameter"
        description: 参数描述信息
        
    返回:
        dict: 包含所有参数的字典对象
    """
    return {"q": q, "skip": skip, "limit": limit}


# 定义物品列表接口，使用依赖注入获取公共参数
# 访问地址示例：http://127.0.0.1:8000/items/?skip=5&limit=20&q=test
@app.get("/items/")
def read_items(commons: dict = Depends(common_parameters)):
    """
    获取物品列表 - 使用依赖注入处理公共参数
    
    依赖注入:
        commons (dict): 由 common_parameters 函数返回的公共参数字典
        
    返回:
        dict: 包含公共参数的 JSON 对象
    """
    return commons


# 带路径参数的物品详情接口，同样使用依赖注入
# 访问地址示例：http://127.0.0.1:8000/items/123?skip=5&limit=20
@app.get("/items/{item_id}")
def read_items(item_id: int, commons: dict = Depends(common_parameters)):
    """
    获取物品详情 - 结合路径参数和依赖注入
    
    路径参数:
        item_id (int): 物品 ID
        
    依赖注入:
        commons (dict): 由 common_parameters 函数返回的公共参数字典
        
    返回:
        dict: 包含物品 ID 和公共参数的 JSON 对象
    """
    # **commons 将字典解包并合并到返回的字典中
    return {"item_id": item_id, **commons}


# 启动配置
if __name__ == '__main__':
    # 导入 uvicorn 服务器
    import uvicorn

    # 运行 FastAPI 应用
    # host: 监听地址为本地回环地址
    # port: 监听端口为 8000
    uvicorn.run(app, host='127.0.0.1', port=8000)
