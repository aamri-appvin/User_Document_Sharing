from enum import Enum

class Status(str,Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Role(str,Enum):
    UPLOADER = "uploader"
    ADMIN = "admin"

class FileType(str,Enum):
    PDF = "pdf"
    DOCX = "docx"
    PNG = "png"
    JPG = "jpg"