from fastapi import Request , Depends , HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.models import Users
from utils.constants import EXPIRED_TOKEN, UNAUTHORIZED, USER_DATA_NOT_FOUND 
import jwt
import os
from dotenv import load_dotenv
from datetime import datetime 

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

print(SECRET_KEY)
print(ALGORITHM)
def get_current_user(request:Request , db: Session = Depends(get_db)):

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401 , detail=UNAUTHORIZED)
    
    token = auth_header.split(" ")[1]
    print("=============token============",token)
    try:
        received_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("===========Received Data",received_data)
        user_id = received_data.get("id")
        email = received_data.get("email")
        exp = received_data.get("exp")
        now = datetime.utcnow()
        exp_time = datetime.utcfromtimestamp(exp)
        user = db.query(Users).filter(Users.id == user_id , Users.deleted_at == None).first()
        print("=================GOT USER=============", user.id)
        if not email:
            raise HTTPException(status_code= 401 , detail=UNAUTHORIZED)
        
        if not user:
            raise HTTPException(status_code= 404 , detail=USER_DATA_NOT_FOUND)
        
        if exp_time < now:
            raise HTTPException(status_code= 401, detail = EXPIRED_TOKEN)
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
