from fastapi import FastAPI
from auth.routes import router as auth_routes
from docs.routes import router as docs_routes

app = FastAPI()


app.include_router(auth_routes)
app.include_router(docs_routes)

