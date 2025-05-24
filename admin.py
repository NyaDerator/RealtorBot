from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from models import Application
from sqlalchemy.orm import Session
from config import ADMINS
import openpyxl
from io import BytesIO

def is_admin(user_id):
    return user_id in ADMINS

def get_applications_keyboard(applications, page, total_pages):
    kb = InlineKeyboardMarkup(row_width=1)
    for app in applications:
        btn_text = f"{app.status or 'Новая'} - {app.timestamp.strftime('%d.%m.%Y %H:%M')}"
        kb.add(InlineKeyboardButton(btn_text, callback_data=f"view_{app.id}"))

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"page_{page-1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"page_{page+1}"))

    if nav_buttons:
        kb.add(*nav_buttons)

    kb.add(InlineKeyboardButton("📊 Статистика", callback_data="stats"))
    kb.add(InlineKeyboardButton("📤 Экспорт в Excel", callback_data="export"))
    return kb

def get_application_detail_kb(app_id):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_{app_id}"),
        InlineKeyboardButton("💬 Коммент", callback_data=f"comment_{app_id}"),
        InlineKeyboardButton("📌 Статус", callback_data=f"status_{app_id}")
    )
    return kb

def generate_excel(applications):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append([
        "ID", "Пользователь", "Тип", "Подтип", "Район", "Комнаты", "Материал",
        "Имя", "Телефон", "Статус", "Комментарий", "Дата"
    ])

    for app in applications:
        ws.append([
            app.id, app.user_id, app.type, app.sub_type, app.region,
            app.rooms, app.material, app.name, app.phone,
            app.status, app.comment, app.timestamp.strftime('%Y-%m-%d %H:%M')
        ])

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream
