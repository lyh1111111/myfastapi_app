# 导入 uvicorn 服务器，用于运行 FastAPI 应用
import uvicorn
# 从 fastapi 框架导入 FastAPI 类和 HTTPException 异常类
from fastapi import FastAPI, HTTPException
# 导入 JSONResponse 用于返回自定义 JSON 响应
from fastapi.responses import JSONResponse



# 创建 FastAPI 应用实例
app = FastAPI()

# 定义根路径的 GET 请求处理函数
# response_class=JSONResponse 指定响应类型为 JSON，虽然默认就是 JSON，但这里显式声明作为示例
@app.get("/", response_class=JSONResponse)

async def index():
    """
    根路径接口，返回问候消息和状态码
    
    返回:
        dict: 包含消息和状态码的 JSON 对象
    """
    return {"message": "Hello World", "status": 200}

# 定义带路径参数的 POST 请求处理函数
# 访问地址示例：http://127.0.0.1:8000/news/1
@app.post("/news/{id}")
async def error(id: int):
    """
    获取新闻详情 - 演示 HTTP 异常处理
    
    路径参数:
        id (int): 新闻 ID
        
    返回:
        dict: 包含新闻信息的 JSON 对象
        
    异常:
        HTTPException: 当新闻 ID 不存在时，抛出 404 错误
    """
    # 定义有效的新闻 ID 列表
    id_list = [1, 2, 3, 4, 5,]
    # 检查 ID 是否在有效列表中
    if id not in id_list:
        # 如果 ID 不存在，抛出 404 异常
        raise HTTPException(status_code=404, detail="你访问的新闻不存在！ ")

    # 返回模拟的新闻数据
    return {"id": id, "title": "新闻标题", "content": "新闻内容"}


# 启动配置
if __name__ == '__main__':
    # 运行 FastAPI 应用
    # host: 监听地址为本地回环地址
    # port: 监听端口为 8002
    uvicorn.run(app, host="127.0.0.1", port=8000)