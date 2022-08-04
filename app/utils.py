import json
import requests
from app.database import User as DbUser
from app.database import Wallet as DbWallet
from app.database import SessionLocal
from sqlalchemy import and_


def get_usd_balance(satoshi):
    btc = satoshi / 100000000
    requests_usd_course = requests.get("https://cex.io/api/last_price/BTC/USD", timeout=30)
    usd_course = float(json.loads(requests_usd_course.text)["lprice"])
    return format(btc, '.8f'), btc * usd_course


def get_user_and_wallet(token, address=None):
    db = SessionLocal()
    user = db.query(DbUser).filter(DbUser.token == token).first()
    if user is None:
        return None, None
    if address is not None:
        wallet = db.query(DbWallet).filter(and_(DbWallet.address == address, DbWallet.user_id == user.id)).first()
        return user, wallet
    else:
        return user, None
