import uuid
import secrets
from fastapi import HTTPException, Header, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import exc, and_

from app.database import User as DbUser
from app.database import Wallet as DbWallet
from app.database import Transaction as DbTransaction
from app.database import SessionLocal
from app.utils import get_usd_balance, get_user_and_wallet

router = APIRouter()


class User(BaseModel):
    username: str


class Wallet(BaseModel):
    username: str


class Token(BaseModel):
    token: str


class Transaction(BaseModel):
    source_address: str
    destination_address: str
    value: int


@router.post("/user")
async def user(get_user: User):
    token = secrets.token_hex(16)
    db = SessionLocal()
    new_user = DbUser(
        username=get_user.username,
        token=token
    )
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except exc.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    return {"token": token}


@router.post("/wallets")
async def wallets(token: str | None = Header(default=None)):
    db = SessionLocal()
    get_user = db.query(DbUser).filter(DbUser.token == token).first()
    if get_user is None:
        raise HTTPException(status_code=400, detail="Wrong token")
    count_wallets = db.query(DbWallet).filter(DbWallet.user_id == get_user.id).count()
    if count_wallets == 10:
        raise HTTPException(status_code=400, detail="User has the maximum number of wallets")
    new_wallet = DbWallet(
        address=str(uuid.uuid4()),
        balance=100000000,
        user_id=get_user.id
    )
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)

    return {"address": new_wallet.address, "btc": get_usd_balance(new_wallet.balance)[0],
            "usd": get_usd_balance(new_wallet.balance)[1]}


@router.get("/wallets/{address}")
async def get_wallet(address: str, token: str | None = Header(default=None)):
    get_user, wallet = get_user_and_wallet(token, address)
    if get_user is None:
        raise HTTPException(status_code=400, detail="Wrong token")
    if wallet is None:
        raise HTTPException(status_code=400, detail="Wrong address")
    return {"address": wallet.address, "btc": get_usd_balance(wallet.balance)[0],
            "usd": get_usd_balance(wallet.balance)[1]}


@router.get("/wallets/{address}/transactions")
async def list_transactions(address: str, token: str | None = Header(default=None)):
    db = SessionLocal()
    get_user, source_wallet = get_user_and_wallet(token, address)
    if get_user is None:
        raise HTTPException(status_code=400, detail="Wrong token")
    if source_wallet is None:
        raise HTTPException(status_code=400, detail="Wrong address")
    result = []
    for transaction in db.query(DbTransaction).filter(
            and_(DbTransaction.user_id == get_user.id, DbTransaction.source_wallet_id == source_wallet.id)).all():
        result.append(
            {"source_address": transaction.source_wallet.address,
             "destination_address": transaction.destination_wallet.address,
             "amount": transaction.amount})
    return JSONResponse(content=result)


@router.post("/transactions")
async def make_transaction(transaction: Transaction, token: str | None = Header(default=None)):
    db = SessionLocal()
    get_user, source_wallet = get_user_and_wallet(token, transaction.source_address)
    if get_user is None:
        raise HTTPException(status_code=400, detail="wrong token")
    if source_wallet is None:
        raise HTTPException(status_code=400, detail="wrong address")
    if source_wallet.balance < transaction.value:
        raise HTTPException(status_code=400, detail="Not enough balance")

    destination_wallet = db.query(DbWallet).filter(DbWallet.address == transaction.destination_address).first()
    if source_wallet.user_id != destination_wallet.user_id:
        profit = round(transaction.value * 0.015)
        amount = transaction.value - profit
        db.query(DbWallet).filter(DbWallet.address == transaction.destination_address).update(
            {'balance': DbWallet.balance + amount})
        db.query(DbWallet).filter(DbWallet.address == transaction.source_address).update(
            {'balance': DbWallet.balance - transaction.value})

        new_transaction = DbTransaction(
            source_wallet_id=source_wallet.id,
            destination_wallet_id=destination_wallet.id,
            amount=amount,
            profit=profit,
            user_id=get_user.id
        )
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
    else:
        db.query(DbWallet).filter(DbWallet.address == transaction.destination_address).update(
            {'balance': DbWallet.balance + transaction.value})
        db.query(DbWallet).filter(DbWallet.address == transaction.source_address).update(
            {'balance': DbWallet.balance - transaction.value})
        new_transaction = DbTransaction(
            source_wallet_id=source_wallet.id,
            destination_wallet_id=destination_wallet.id,
            amount=transaction.value,
            profit=0,
            user_id=get_user.id
        )
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
    return {"status": "Success"}


@router.get("/transactions")
async def list_transactions(token: str | None = Header(default=None)):
    db = SessionLocal()
    result = []
    get_user, _ = get_user_and_wallet(token)
    if get_user is None:
        raise HTTPException(status_code=400, detail="wrong token")
    for transaction in db.query(DbTransaction).all():
        result.append(
            {"source_address": transaction.source_wallet.address,
             "destination_address": transaction.destination_wallet.address,
             "amount": transaction.amount})
    return JSONResponse(content=result)
