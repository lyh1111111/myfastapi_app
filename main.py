# 从 fastapi 框架导入 FastAPI 类，用于创建应用实例
from fastapi import FastAPI
# 导入 uvicorn，这是一个 ASGI 服务器，用于运行 FastAPI 应用
import uvicorn

# 1. 创建 FastAPI 实例
# title 参数会在自动生成的 API 文档中显示为标题
app = FastAPI(title="我的图书管理 API")


# --- 基础接口 ---
# 定义根路径的 GET 请求处理函数
# 访问地址：http://127.0.0.1:8000/
@app.get("/")
async def read_root():
    """
    根路径接口，返回 API 在线状态信息
    异步函数，FastAPI 推荐使用 async/await 模式提高性能
    """
    return {"status": "online", "message": "Hello, uv!"}


# 定义带路径参数的 GET 请求处理函数
# 访问地址示例：http://127.0.0.1:8000/hello/zhangsan
@app.get("/hello/{name}")
async def say_hello(name: str):
    """
    问候接口，接收路径参数 name 并返回问候语
    
    参数:
        name (str): 要问候的人名，通过 URL 路径传递
        
    返回:
        dict: 包含问候消息的 JSON 对象
    """
    return {"message": f"Hello, {name}!"}



# 3. 启动配置
# 当直接运行此脚本时（而非作为模块导入），执行以下代码
if __name__ == "__main__":
    # 强制指定 127.0.0.1 避免之前的 127.0.0.0 错误
    # host: 监听地址，127.0.0.1 表示仅本地访问
    # port: 监听端口号，8000 是 FastAPI 默认端口
    uvicorn.run(app, host="127.0.0.1", port=8000)
