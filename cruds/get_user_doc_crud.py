from datetime import datetime, timedelta
import io
from typing import Optional
from fastapi import Depends , HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from auth.dependency import get_current_user
from cruds.upload_crud import get_content_type_from_file_type
from database import get_db
from models.models import AccessLink, Documents, Roles
from utils.constants import ACCESS_LINK_NOT_FOUND, DOCUMENT_NOT_FOUND, FILE_NOT_FOUND, LINK_ALREADY_USED, LINK_EXPIRED, UNAUTHORIZED
from utils.enums import Role
from cryptography.fernet import Fernet
import os
from uuid import uuid4

def get_user_docs(
uploader_id : Optional[int],
doc_type : Optional[str],
date : Optional[datetime],
db: Session = Depends(get_db),
user = Depends(get_current_user)):
    try:
        records = db.query(Documents).filter(Documents.deleted_at == None)

        role = db.query(Roles).filter(user.role_id == Roles.id).first()

        if role.role_name == Role.UPLOADER:
            records = records.filter(Documents.user_id == user.id)

        else:
            if uploader_id:
                records = records.filter(Documents.user_id == uploader_id)
            if doc_type:
                records = records.filter(Documents.type == doc_type)
            if date:
                records = records.filter(Documents.uploaded_at >= date)

    
        records = records.all()

        return [
        {
            "id" : record.id,
            "doc_name" : record.doc_name,
            "type" : record.type,
            "file_path" : record.file_path,
            "uploaded_at" : record.uploaded_at,
            "user_id" : record.user_id
        }
        for record in records
        ]
    except Exception as ex:
        raise HTTPException(f"Could not fetch data from database due to : {ex}")


def get_user_documents_by_id(doc_id : int , db: Session = Depends(get_db) , user = Depends(get_current_user)):
    try:
        doc = db.query(Documents).filter(Documents.id == doc_id, Documents.deleted_at == None).first()

        if not doc:
            raise HTTPException(404, DOCUMENT_NOT_FOUND)
    
        role = db.query(Roles).filter(Roles.id == user.role_id).first()

        if role.role_name is  Role.UPLOADER and user.id is not doc.user_id:
            raise HTTPException(403, UNAUTHORIZED)
    

        return {
        "id": doc.id,
        "title": doc.doc_name,
        "file_type": doc.type,
        "uploaded_at": doc.uploaded_at,
        "file_path": doc.file_path
        }
    except Exception as ex:
        raise HTTPException(f"Could not fetch data from database due to : {ex}")
    


async def download_user_documents_by_id(
    doc_id: int,
    db: Session,
    user
):
    
    doc = db.query(Documents).filter(
        Documents.id == doc_id,
        Documents.deleted_at == None
    ).first()


    if not doc:
        raise HTTPException(404, DOCUMENT_NOT_FOUND)
    if user.id != doc.user_id:
        raise HTTPException(403, UNAUTHORIZED)

    UPLOAD_DIR = "uploads"
    file_path = os.path.join(UPLOAD_DIR, doc.doc_name)
    print("File Exists in **************", file_path)
    if not os.path.exists(file_path):
        raise HTTPException(404, FILE_NOT_FOUND)

    fernet = Fernet(os.getenv("ENCRYPTION_KEY"))
    encrypted_data = open(file_path, "rb").read()
    decrypted_data = fernet.decrypt(encrypted_data)


    buffer = io.BytesIO(decrypted_data)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type=get_content_type_from_file_type(doc.type),
        headers={
            "Content-Disposition": f'attachment; filename="{doc.doc_name}"'
        }
    )


def share_doc_public_link(
    doc_id : int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    exp: int = 10
):
    doc = db.query(Documents).filter(Documents.id == doc_id , Documents.deleted_at == None).first()

    if not doc:
        raise HTTPException(404, DOCUMENT_NOT_FOUND)
    
    if user.id != doc.user_id:
        raise HTTPException(403, UNAUTHORIZED)
    
    exp = datetime.utcnow() + timedelta(minutes=exp)

    token = str(uuid4())
    access_link = AccessLink(
        doc_id = doc_id,
        unique_token = token,
        created_at = datetime.utcnow(),
        expired_at = exp
    )

    db.add(access_link)
    db.commit()
    return {"url": f"/access-link/{doc_id}/{token}/download/"}

def download_file_from_public_link(
    token: str,
    db: Session = Depends(get_db)
):
    access_link = db.query(AccessLink).filter(AccessLink.unique_token == token).first()

    print("=============ACCESS LINK=============",access_link)
    if not access_link:
        raise HTTPException(404, ACCESS_LINK_NOT_FOUND)
    
    current_time = datetime.utcnow()
    
    if current_time > access_link.expired_at:
        raise HTTPException(403, LINK_EXPIRED)
    
    if access_link.downloaded == True:
        raise HTTPException(403, LINK_ALREADY_USED)
    
    doc = db.query(Documents).filter(Documents.id == access_link.doc_id).first()

    if not doc:
        raise HTTPException(404, DOCUMENT_NOT_FOUND)
    
    fernet = Fernet(os.getenv("ENCRYPTION_KEY"))

    file_path = os.path.join("uploads", doc.doc_name)
    decrypted = fernet.decrypt(open(file_path, "rb").read())
    
    buffer = io.BytesIO(decrypted)
    buffer.seek(0)

    access_link.downloaded = True
    db.commit()

    return StreamingResponse(
        buffer,
        media_type=get_content_type_from_file_type(doc.type),
        headers={"Content-Disposition": f'attachment; filename="{doc.doc_name}"'}
    )
