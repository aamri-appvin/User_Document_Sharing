from fastapi import APIRouter , Depends
from cruds.auth_crud import get_user_data, register_user_data
from database import get_db
from schemas.schema import UserLogin, UserRegister
from utils.constants import AUTHENTICATION , USER_DATA_NOT_FOUND , INCOMPLETE_DATA_PROVIDED, USER_LOGIN_SUCCESSFUL, USER_REGISTRATION_SUCCESSFUL
from utils.response import error_response, success_response
from sqlalchemy.orm import Session

router = APIRouter(prefix="/user" , tags=[AUTHENTICATION])

@router.post("/login")
def user_login(user:UserLogin , db:Session = Depends(get_db)):
    if not user:
        return error_response(INCOMPLETE_DATA_PROVIDED, status_code=400)
    
    email = user.email
    password = user.password
    result = get_user_data( email, password ,db)

    return success_response(result , USER_LOGIN_SUCCESSFUL , 200)

@router.post("/register")
def user_registration(user:UserRegister , db:Session = Depends(get_db)):
    if not user:
        return error_response(INCOMPLETE_DATA_PROVIDED, status_code=400)
    
    result = register_user_data(user,db)
    return success_response(result , USER_REGISTRATION_SUCCESSFUL , 200)