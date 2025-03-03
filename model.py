import datetime
from sqlalchemy import Column, Integer, String, REAL, ForeignKey, DateTime
from sqlalchemy.testing.schema import mapped_column

from database import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True)
    password = Column(String(50))
    ipn = Column(Integer, unique=False)
    full_name = Column(String(150))
    contacts = Column(String(150))
    photo = Column(String(150))
    passport = Column(String(150), unique=True)
    email = Column(String(120), nullable=True)

    def __init__(self, id=None, login=None, password=None, ipn=None, full_name=None, contacts=None, photo=None, passport=None):
        self.id = id
        self.login = login
        self.password = password
        self.ipn = ipn
        self.full_name = full_name
        self.contacts = contacts
        self.photo = photo
        self.passport = passport



class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    photo = Column(String(150))
    name = Column(String(150), nullable=False)
    description = Column(String(150))
    price_hour = Column(REAL)
    price_day = Column(REAL)
    price_week = Column(Integer)
    price_month = Column(REAL)
    owner = mapped_column(ForeignKey('user.id'))

    def __init__(self, id=None, photo=None, name=None, description=None, price_hour=None, price_day=None, price_week=None, price_month=None, owner=None):
        self.id = id
        self.photo = photo
        self.name = name
        self.description = description
        self.price_hour = price_hour
        self.price_day = price_day
        self.price_week = price_week
        self.price_month = price_month
        self.owner = owner

class Contract(Base):
    __tablename__ = 'contract'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(800))
    start_day = Column(Integer)
    end_day = Column(Integer)
    leaser = mapped_column(ForeignKey('user.id'))
    taker = mapped_column(ForeignKey('user.id'))
    item = mapped_column(ForeignKey('item.id'))
    status = Column(Integer)
    signed_datetime = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, id=None, text=None, start_day=None, end_day=None, leaser=None, taker=None, item=None, status=None):
        self.id = id
        self.text = text
        self.start_day = start_day
        self.end_day = end_day
        self.leaser = leaser
        self.taker = taker
        self.item = item
        self.status = status

class Favorite(Base):
    __tablename__ = 'favorite'
    id = Column(Integer, primary_key=True, autoincrement=True)
    item = mapped_column(ForeignKey('item.id'))
    user = mapped_column(ForeignKey('user.id'))
    timestamp = Column(DateTime, default=datetime.datetime.now, nullable=True)

    def __init__(self, id=None, item=None, user=None):
        self.id = id
        self.item = item
        self.user = user

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author = mapped_column(ForeignKey('user.id'))
    user = mapped_column(ForeignKey('user.id'))
    text = Column(String(800))
    grade = Column(Integer)
    contact = mapped_column(ForeignKey('contract.id'))
    timestamp = Column(DateTime, default=datetime.datetime.now(), server_default="datetime()", nullable=False)

    def __init__(self, id=None, author=None, user=None, text=None, grade=None, contact=None):
        self.id = id
        self.author = author
        self.user = user
        self.text = text
        self.grade = grade
        self.contact = contact

class Search_History(Base):
    __tablename__ = 'search_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = mapped_column(ForeignKey('user.id'))
    search_item = mapped_column(ForeignKey('item.id'))
    timestamp = Column(Integer)

    def __init__(self, id=None, user=None, search_item=None, timestamp=None):
        self.id = id
        self.user = user
        self.search_item = search_item
        self.timestamp = timestamp
