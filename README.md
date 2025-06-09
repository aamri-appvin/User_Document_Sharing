Setup Instructions :-

git clone https://github.com/your-username/secure-doc-share.git
cd secure-doc-share
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
dotenv setup
uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile cert.key --ssl-certfile cert.crt

Project Description :-

This project is an RBAC based project for 
Uploading , downloading , sharing documents via public links
admin has the permission to view all documents ,but user only can view his documents

