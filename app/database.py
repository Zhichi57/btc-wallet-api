from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, ForeignKey, Integer, String, Float

import os

# Получение переменных из окружения
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Формирование адреса для подключения к базе данных
SQLALCHEMY_DATABASE_URL = "postgresql://{user}:{password}@db/{db}".format(user=POSTGRES_USER,
                                                                          password=POSTGRES_PASSWORD, db=POSTGRES_DB)
# Подключение к базе данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True)
    token = Column(String, unique=False)
    wallets = relationship("Wallet")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    address = Column(String, unique=True)
    balance = Column(Integer, unique=False)
    user_id = Column(Integer, ForeignKey('users.id'))


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_wallet_id = Column(Integer, ForeignKey("wallets.id"))
    destination_wallet_id = Column(Integer, ForeignKey("wallets.id"))
    amount = Column(Integer, unique=False)
    profit = Column(Integer, unique=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    source_wallet = relationship("Wallet", foreign_keys=[source_wallet_id])
    destination_wallet = relationship("Wallet", foreign_keys=[destination_wallet_id])
