import datetime
from pydantic import BaseModel , Field 
from sqlalchemy import Column, Integer, String, Float , Enum , JSON , ForeignKey ,DateTime , Boolean
from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
from database import base
from utils.enums import FileType, Status , Role

Base = base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String,unique=True, index=True)
    password = Column(String,index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, index=True)
    deleted_at = Column(DateTime, nullable=True, index=True)
    role = relationship("Roles" , backref = "users")

class Documents(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_name = Column(String,index=True)
    type = Column(Enum(FileType), index=True)
    file_path = Column(String)
    user_id = Column(Integer, ForeignKey("users.id") , index=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow,nullable = True ,  index=True)
    deleted_at = Column(DateTime, nullable=True, index=True)
    upload = relationship("Users" , backref="documents")

class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(Enum(Role), unique=True, index=True)
    permissions = Column(JSON, nullable=True) 
    created_at = Column(DateTime, default=datetime.datetime.utcnow,nullable = True ,  index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable = True , index=True)
    deleted_at = Column(DateTime, nullable=True, index=True)


class AccessLink(Base):
    __tablename__= "access_link"

    id = Column(Integer, primary_key=True)
    doc_id = Column(Integer, ForeignKey("documents.id"))
    unique_token = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expired_at = Column(DateTime, nullable=True, index=True)
    downloaded = Column(Boolean , default=False)