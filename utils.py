import re
import requests
import pandas as pd
from io import BytesIO
from database import SessionLocal, Application, User, Config
from config import ADMIN_IDS

def validate_phone(phone):
    pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
    return bool(re.match(pattern, phone))

def validate_name(name):
    return len(name) >= 2 and all(c.isalpha() or c.isspace() for c in name)

def is_admin(user_id):
    if user_id in ADMIN_IDS:
        return True
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id, User.is_admin == True).first()
        return user is not None
    finally:
        db.close()

def get_statistics():
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        total_applications = db.query(Application).count()
        apartment_apps = db.query(Application).filter(Application.property_type == "apartment").count()
        house_apps = db.query(Application).filter(Application.property_type == "house").count()
        
        return {
            "total_users": total_users,
            "total_applications": total_applications,
            "apartment_applications": apartment_apps,
            "house_applications": house_apps
        }
    finally:
        db.close()

def export_to_excel():
    db = SessionLocal()
    try:
        applications = db.query(Application).all()
        
        data = []
        for app in applications:
            user = db.query(User).filter(User.user_id == app.user_id).first()
            data.append({
                "ID": app.id,
                "Пользователь": user.first_name if user else "Неизвестно",
                "Тип недвижимости": "Квартира" if app.property_type == "apartment" else "Дом",
                "Статус строительства": app.building_status,
                "Район": app.district,
                "Комнаты": app.rooms,
                "Есть участок": app.has_plot,
                "Тип дома": app.house_type,
                "Имя": app.name,
                "Телефон": app.phone,
                "Дата создания": app.created_at.strftime("%d.%m.%Y %H:%M")
            })
        
        df = pd.DataFrame(data)
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        
        return buffer
    finally:
        db.close()

def get_config_value(key):
    db = SessionLocal()
    try:
        config = db.query(Config).filter(Config.key == key).first()
        return config.value if config else ""
    finally:
        db.close()

def set_config_value(key, value):
    db = SessionLocal()
    try:
        config = db.query(Config).filter(Config.key == key).first()
        if config:
            config.value = value
        else:
            config = Config(key=key, value=value)
            db.add(config)
        db.commit()
    finally:
        db.close()