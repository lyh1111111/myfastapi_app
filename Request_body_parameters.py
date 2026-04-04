# 导入 uvicorn 服务器，用于运行 FastAPI 应用
import uvicorn
# 从 fastapi 框架导入 FastAPI 类
from fastapi import FastAPI
# 从 pydantic 导入 BaseModel 用于定义数据模型，Field 用于字段校验
from pydantic import BaseModel,Field

# 创建 FastAPI 应用实例
app = FastAPI()


# 注释掉的代码：使用 Field 进行简单的字段校验
# class User(BaseModel):
#     username: str = Field(..., min_length=3, description="用户名至少 3 位")
#     password: str = Field(..., min_length=8, description="密码至少 8 位")
#
# @app.get("/")
# async def root():
#     return {"message": "hello world"}
# @app.post("/register")
#
# async def register(user: User):
#     return {"username": user.username, "password": user.password}


# 重新导入（实际上面的导入已经足够，这里可以省略）
import uvicorn
from fastapi import FastAPI
# 从 pydantic 导入 field_validator 用于自定义字段验证逻辑
from pydantic import BaseModel, field_validator

# 创建 FastAPI 应用实例
app = FastAPI()

# 1. 定义数据模型
# 使用 Pydantic BaseModel 定义用户数据结构，自动进行数据验证和序列化
class User(BaseModel):
    """
    用户数据模型
    
    属性:
        username (str): 用户名
        password (str): 密码
    """
    username: str  # 用户名字段，字符串类型
    password: str  # 密码字段，字符串类型

    # 自定义用户名验证器
    # field_validator 装饰器指定要验证的字段为 'username'
    # @classmethod 表示这是一个类方法
    @field_validator('username')
    @classmethod
    def username_must_be_long(cls, v: str):
        """
        用户名验证器：检查用户名长度
        
        参数:
            cls: 类本身
            v (str): 用户名的值
            
        返回:
            str: 验证通过的用户名
            
        异常:
            ValueError: 如果用户名长度小于 3 个字符
        """
        if len(v) < 3:
            raise ValueError('用户名太短啦，起码要 3 个字！')
        return v

    # 自定义密码验证器
    @field_validator('password')
    @classmethod
    def password_check(cls, v: str):
        """
        密码验证器：检查密码强度
        
        参数:
            cls: 类本身
            v (str): 密码的值
            
        返回:
            str: 验证通过的密码
            
        异常:
            ValueError: 如果密码长度小于 8 个字符
        """
        if len(v) < 8:
            raise ValueError('密码强度不够，必须 8 位以上')
        return v

# 2. 定义路由（千万不能注释掉这些！）
# 定义根路径的 GET 请求处理函数
@app.get("/")
async def root():
    """
    根路径接口，返回问候消息
    
    返回:
        dict: 包含问候消息的 JSON 对象
    """
    return {"message": "hello world"}

# 定义用户注册接口，使用 POST 方法
# response_model=User 指定响应数据模型，FastAPI 会自动将返回的数据转换为 User 模型格式
@app.post("/register", response_model=User)
async def register(user: User):
    """
    用户注册接口
    
    请求体参数:
        user (User): 用户信息，包含用户名和密码
        
    返回:
        User: 验证通过的用户信息
        
    注意:
        - 请求体必须是 JSON 格式
        - 会自动触发 User 模型中的验证器
        - 如果验证失败，会返回 422 错误
    """
    return user

# 3. 启动服务
if __name__ == "__main__":
    # 注意：这里我们用了 8002 端口
    # host: 监听地址为本地回环地址
    # port: 监听端口为 8002（不同于默认的 8000）
    uvicorn.run(app, host="127.0.0.1", port=8000)

