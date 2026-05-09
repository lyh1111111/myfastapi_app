# 导入 uvicorn 服务器，用于运行 FastAPI 应用
import uvicorn
# 从 fastapi 框架导入 FastAPI 类
from fastapi import FastAPI

# 创建 FastAPI 应用实例
app = FastAPI()


# 定义第一个 HTTP 中间件（按代码顺序应该是第二个执行的中间件）
# 中间件在请求处理之前和响应返回之后执行，可以处理请求日志、认证等通用逻辑
@app.middleware("http")
async def add_process_time_header(request, call_next):
    """
    HTTP 中间件 B：处理请求流程
    
    参数:
        request: 请求对象，包含请求的所有信息
        call_next: 调用函数，将请求传递给下一个中间件或路由处理器
        
    返回:
        Response: 处理后的响应对象
    """
    print("请求 B 来了")  # 打印请求到达信息
    # 调用下一个中间件或路由处理器，并获取响应
    response = await call_next(request)
    print("请求 B 处理完毕")  # 打印请求处理完成信息
    return response

# 定义第二个 HTTP 中间件（按代码顺序应该是第一个执行的中间件）
# 注意：中间件的执行顺序是倒序的，最后定义的中间件最先执行
@app.middleware("http")
async def add_process_time_header(request, call_next):
    """
    HTTP 中间件 A：处理请求流程
    
    参数:
        request: 请求对象，包含请求的所有信息
        call_next: 调用函数，将请求传递给下一个中间件或路由处理器
        
    返回:
        Response: 处理后的响应对象
    """
    print("请求 A 来了")  # 打印请求到达信息
    # 调用下一个中间件或路由处理器，并获取响应
    response = await call_next(request)
    print("请求 A 处理完毕")  # 打印请求处理完成信息
    return response

# 定义根路径的 GET 请求处理函数
@app.get("/")
async def read_root():
    """
    根路径接口，返回简单的问候消息
    
    返回:
        dict: 包含问候消息的 JSON 对象
    """
    return {"message": "Hello World"}

# 启动配置
if __name__ == '__main__':
    # 运行 FastAPI 应用
    # host: 监听地址为本地回环地址
    # port: 监听端口为 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)