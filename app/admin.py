import os
from fastapi import HTTPException, Header, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import func
from app.database import Transaction as DbTransaction
from app.database import SessionLocal

admin_router = APIRouter()


@admin_router.get("/statistics")
async def statistics(token: str | None = Header(default=None)):
    db = SessionLocal()
    result = {}
    if token == os.getenv("ADMIN_TOKEN"):
        for transaction in db.query(func.count(DbTransaction.id), func.sum(DbTransaction.profit)).all():
            result["total transactions"] = transaction[0]
            result["platform profit"] = transaction[1]
        return JSONResponse(content=result)
    else:
        raise HTTPException(status_code=400, detail="Wrong token")
