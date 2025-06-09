from sqlalchemy.orm import Session
from fastapi import Depends , HTTPException
from database import get_db
from models.models import Users
import bcrypt
from schemas.schema import UserRegister
from utils.constants import INVALID_CREDENTIALS, USER_ALREADY_EXISTS, USER_DATA_NOT_FOUND
from utils.jwt_token import get_jwt_token

def get_user_data(email: str, password: str, db: Session = Depends(get_db)):
    try:
        user = db.query(Users).filter(Users.email == email , Users.deleted_at == None).first()
        if not user:
            raise HTTPException(
            status_code=404,
            detail=USER_DATA_NOT_FOUND
        )
        registered_password = user.password

        is_valid = bcrypt.checkpw(password.encode('utf-8'),registered_password.encode('utf-8'))
        if not is_valid:
             raise HTTPException(
            status_code=401,
            detail=INVALID_CREDENTIALS
        )
    
        jwt_token = get_jwt_token(user.id , user.email)

        return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role_id": user.role_id, 
        "jwt_token": jwt_token
        }
    except Exception as ex:
        raise HTTPException(
         status_code=500,
         detail=f"Could not fetch data from database due to: {ex}"
        )

def register_user_data(user:UserRegister, db: Session = Depends(get_db)):
    try:

        existing_user = db.query(Users).filter(Users.email == user.email, Users.deleted_at == None).first()

        if existing_user:
            raise HTTPException(
            status_code=409,
            detail=USER_ALREADY_EXISTS
            )
        
        hash_password =  bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        new_user = Users(
        name=user.name,
        email=user.email,
        password=hash_password,
        role_id=user.role_id  
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role_id": new_user.role_id
        }
    except Exception as ex:
        raise HTTPException(
         status_code=500,
         detail=f"Could not register data to the  database due to: {ex}"
        )