from sqlalchemy import create_engine
from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, Float
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from tgbot.data.loader import engine, Session

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=naming_convention)
Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    requisites = relationship('Requisite')


class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer(), primary_key=True)
    trader_id = Column(Integer(), ForeignKey('traders.user_id'))
    amount = Column(Float())
    state = Column(Integer(), default=0)
    trader = relationship('Trader', back_populates='trades')
    date = Column(String(), default='')  # %Y-%m-%d %H:%M:%S


class Trader(Base):
    __tablename__ = 'traders'
    user_id = Column(Integer(), primary_key=True)
    balance = Column(Float(), default=0)
    requisites = relationship('Requisite')
    trades = relationship(Trade, back_populates='trader')
    wallet = Column(String(), default='')
    is_active = Column(Integer(), default=1)
    account_id = Column(Integer(), default=0)


class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer(), primary_key=True)
    api_key = Column(String())
    escrow = Column(Float(), default=0)
    refill_address = Column(String(), default='Адрес для пополнения')


class Requisite(Base):
    __tablename__ = 'requisites'
    id = Column(Integer(), primary_key=True)
    bank = Column(String())
    value = Column(String())
    user_id = Column(Integer, ForeignKey(Trader.user_id))


def create_db():
    Base.metadata.create_all(bind=engine)


create_db()
