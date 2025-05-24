from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Application, User
from oauth2client.service_account import ServiceAccountCredentials
import gspread

engine = create_engine("sqlite:///bot.db", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_gsheet_client(json_keyfile_path: str):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
    client = gspread.authorize(creds)
    return client

def sync_applications_to_gsheet(json_keyfile_path: str, spreadsheet_name: str, worksheet_name: str = "Заявки"):
    client = get_gsheet_client(json_keyfile_path)
    sheet = client.open(spreadsheet_name)

    try:
        worksheet = sheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=worksheet_name, rows="100", cols="20")

    headers = [
        "ID", "Telegram ID", "Тип", "Подтип", "Регион", "Комнат", "Материал", 
        "Имя", "Телефон", "Статус", "Комментарий", "Дата"
    ]
    worksheet.clear()
    worksheet.append_row(headers)

    db = SessionLocal()
    applications = db.query(Application).all()

    rows = []
    for app in applications:
        user = db.query(User).filter(User.id == app.user_id).first()
        rows.append([
            app.id,
            user.telegram_id if user else "N/A",
            app.type,
            app.sub_type,
            app.region,
            app.rooms,
            app.material,
            app.name,
            app.phone,
            app.status,
            app.comment,
            app.timestamp.strftime('%Y-%m-%d %H:%M') if app.timestamp else ''
        ])

    if rows:
        worksheet.append_rows(rows)

    db.close()
    print("Синхронизация завершена.")