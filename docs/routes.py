
from typing import Optional
from fastapi import APIRouter , UploadFile , Depends , HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from auth.dependency import get_current_user
from cruds.auth_crud import get_user_data
from cruds.get_user_doc_crud import download_file_from_public_link, download_user_documents_by_id, get_user_docs, get_user_documents_by_id, share_doc_public_link
from cruds.upload_crud import process_file_contents
from database import get_db
from utils.constants import DOC_UPLOADED_SUCCESSFULLY, DOCUMENTS, FETCHED_THE_DATA_SUCCESSFULLY, GENERATED_PUBLIC_LINK, NOT_A_VALID_FILE_FORMAT
from utils.response import success_response

router = APIRouter(prefix = "/documents" , tags = [DOCUMENTS])

allowed_file_types = ["image/jpeg" , "image/png" , "application/pdf" , "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

@router.post("/")
def upload_user_docs(file: UploadFile , db: Session = Depends(get_db), user = Depends(get_current_user)):
    if file.content_type not in allowed_file_types:
        raise HTTPException(status_code=400 , detail =NOT_A_VALID_FILE_FORMAT)
    
    result = process_file_contents(file , db , user)
    return success_response(result , DOC_UPLOADED_SUCCESSFULLY , 201)
    
@router.get("/")
def get_uploaded_docs(
uploader_id : Optional[int],
doc_type : Optional[str],
date : Optional[datetime],
db: Session = Depends(get_db),
user = Depends(get_current_user)):
    result = get_user_docs(uploader_id , doc_type , date , db , user)

    return success_response(result , FETCHED_THE_DATA_SUCCESSFULLY , 200)

@router.get("/{id}")
def get_documents_by_id(doc_id : int,db: Session = Depends(get_db),user = Depends(get_current_user)):

    results = get_user_documents_by_id(doc_id , db , user)

    return success_response(results , FETCHED_THE_DATA_SUCCESSFULLY , 200)


@router.get("/{id}/download")
def download_doc_by_id(doc_id : int,db: Session = Depends(get_db),user = Depends(get_current_user)):

    results = download_user_documents_by_id(doc_id , db , user)


@router.post("/{id}/share")
def share_public_link(
    doc_id : int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    exp: int = 10):


    results = share_doc_public_link( doc_id , db , user , exp )
    return success_response(results , GENERATED_PUBLIC_LINK , 201)


@router.get("/access-link/{doc_id}/{token}/download/")
def download_from_public_link(
    token: str,
    db: Session = Depends(get_db)
):
    print("===========SHARABLE PUBLIC LINK===========")
    results = download_file_from_public_link(token , db)
    # /access-link/2/27ca19a8-b818-408c-91ec-583f5e274f22/download/