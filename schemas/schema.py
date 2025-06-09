from typing import Optional
from pydantic import BaseModel, Field
from utils.enums import Role
from datetime import datetime
class UserLogin(BaseModel):
    email: str
    password:str 

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role_id: int

