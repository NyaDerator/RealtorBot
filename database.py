from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    has_application = Column(Boolean, default=False)

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    property_type = Column(String)
    building_status = Column(String, nullable=True)
    district = Column(String, nullable=True)
    rooms = Column(String, nullable=True)
    has_plot = Column(String, nullable=True)
    house_type = Column(String, nullable=True)
    name = Column(String)
    phone = Column(String)
    status = Column(String, default="new")  # new, in_progress, completed, cancelled
    admin_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Config(Base):
    __tablename__ = "config"
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    value = Column(Text)

async def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        default_configs = [
            ("districts", "Центральный,Северный,Южный,Восточный,Западный"),
            ("rooms", "1,2,3,4,5+"),
            ("house_types", "Камень,Дерево,Кирпич")
        ]
        
        for key, value in default_configs:
            config = db.query(Config).filter(Config.key == key).first()
            if not config:
                db.add(Config(key=key, value=value))
        
        db.commit()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()