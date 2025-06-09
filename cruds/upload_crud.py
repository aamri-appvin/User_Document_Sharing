from sqlalchemy.orm import Session 
from fastapi import Depends , UploadFile , HTTPException
from auth.dependency import get_current_user
from database import get_db
from models.models import Documents
from utils.constants import DOC_UPLOADED_SUCCESSFULLY, FILE_SIZE_LIMIT_EXCEEDED
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from uuid import uuid4
import os
from utils.enums import FileType
from utils.response import success_response

load_dotenv()
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
def map_file_type(content_type:str):
    mapping = {
        "image/png": FileType.PNG,
        "image/jpeg": FileType.JPG,
        "application/pdf": FileType.PDF,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.DOCX,
    }
    return mapping.get(content_type)

def get_content_type_from_file_type(file_type: FileType):
    reverse_mapping = {
        FileType.PNG: "image/png",
        FileType.JPG: "image/jpeg",
        FileType.PDF: "application/pdf",
        FileType.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    return reverse_mapping.get(file_type)

def process_file_contents(
        file: UploadFile ,
        db: Session = Depends(get_db) ,
        user=Depends(get_current_user)
        ):
    try:
        file_size_limit = 1 * 1024 *1024 #file size in bytes
        file_data = file.file.read() # reads the file data in bytes
        if len(file_data) > file_size_limit:
            raise HTTPException(status_code=400 , detail = FILE_SIZE_LIMIT_EXCEEDED)
    
        fernet = Fernet(ENCRYPTION_KEY)

        enc_content = fernet.encrypt(file_data)
        UPLOAD_DIR = "uploads"
        # file_id = str(uuid4())
        # file_path = f"/uploads/{file.filename}"

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as f:
            f.write(enc_content)

        mapped_type = map_file_type(file.content_type)
        print("=============Successfully wrote content to the file =======================")
        print("============Current User================",user)
        doc = Documents(
        doc_name=file.filename,
        type=mapped_type,
        file_path=file_path,
        user_id=user.id
        )
        print("=================created documents===================")
        db.add(doc)
        db.commit()
        db.refresh(doc)

        return {
        "id": doc.id,
        "type": doc.type,
        "path": doc.file_path,
        "user_id": user.id
        }
    except Exception as ex:
        raise HTTPException(
         status_code=500,
         detail=f"Could not upload data to database due to : {ex}"
        )
