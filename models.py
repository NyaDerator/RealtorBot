from sqlalchemy import Column, Integer, String, DateTime, Boolean, text
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    is_admin = Column(Boolean, default=False)

class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    type = Column(String)
    sub_type = Column(String)
    region = Column(String)
    rooms = Column(String)
    material = Column(String)
    name = Column(String)
    phone = Column(String)
    status = Column(String, default='Новая')
    comment = Column(String(250))
    timestamp = Column(DateTime(timezone=True), server_default=text("TIMEZONE('Europe/Moscow', now())"))
