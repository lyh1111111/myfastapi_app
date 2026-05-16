"""
用户数据模式定义
定义用户请求的数据结构和验证规则
"""
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict




class UserRequest(BaseModel):
    """用户注册请求模型"""
    username: str  # 用户名
    password: str  # 密码

class UserInfoBase(BaseModel):
    #定义用户基础信息模型
    nickname: Optional[str] = Field(None, max_length=50,description="昵称")  # 昵称
    bio: Optional[str] = Field(None, max_length=500,description="个人简介")
    avatar: Optional[str] = Field(None, max_length=255,description="头像")
    gender: Optional[str] = Field(None, max_length=10,description="性别")
    phone: Optional[str] = Field(None, max_length=11,description="手机号")



class UserInfoResponse(UserInfoBase):
    #模型类配置
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )
    """用户响应模型"""
    id: int
    username: str
    avatar: str
    bio: str
    gender: str
    phone: Optional[str] = None


class UserAuthResponse(BaseModel):
    #模型类配置
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )
    """用户响应模型"""
    token: str
    userInfo: UserInfoResponse = Field(...,alias="userInfo")

