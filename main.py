from fastapi import FastAPI
from app.database import Base, engine
from app.main import router
from app.admin import admin_router

app = FastAPI()

app.include_router(router)
app.include_router(admin_router)
Base.metadata.create_all(bind=engine)
