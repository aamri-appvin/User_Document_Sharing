import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import jwt
load_dotenv()


ACCESS_TOKEN_EXP = int(os.getenv("ACCESS_TOKEN_EXP"))
REFRESH_TOKEN_EXP = os.getenv("REFRESH_TOKEN_EXP")
ALGORITHM = os.getenv("ALGORITHM")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")

def get_jwt_token(id:int , email: str):

    expires_in = datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXP)
    encode_data = {"id":id, "email":email , "exp": expires_in}

    jwt_token = "Bearer"+" "+str(jwt.encode(encode_data , JWT_SECRET_KEY , algorithm=ALGORITHM))

    return jwt_token



