# 导入FastAPI框架
from fastapi import FastAPI
# 导入新闻路由模块
from toutiao_app.routers import news



# 创建FastAPI应用实例
app = FastAPI()
# 定义根路径GET请求处理函数
@app.get("/")
def read_root():
    return {"Hello": "World"}

# 注册新闻路由到应用中
app.include_router(news.router)


# 程序入口点
if __name__ == '__main__':
    # 导入uvicorn ASGI服务器
    import uvicorn
    # 启动应用，绑定地址127.0.0.1，端口8000
    uvicorn.run(app, host="127.0.0.1", port=8001)