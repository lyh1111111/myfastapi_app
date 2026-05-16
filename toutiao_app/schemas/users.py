"""
用户数据模式定义
定义用户请求的数据结构和验证规则
"""

from pydantic import BaseModel

class UserRequest(BaseModel):
    """用户注册请求模型"""
    username: str  # 用户名
    password: str  # 密码