import telebot
from telebot.types import Message, CallbackQuery, InputFile
from config import TOKEN, ADMINS
from models import Base, User, Application
from database import engine, SessionLocal
from forms import *
from admin import *
from utils import is_valid_phone
from sqlalchemy import func

bot = telebot.TeleBot(TOKEN)
Base.metadata.create_all(bind=engine)

user_states = {}

@bot.message_handler(commands=['start'])
def cmd_start(message: Message):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not user:
        user = User(telegram_id=message.from_user.id, is_admin=message.from_user.id in ADMINS)
        session.add(user)
        session.commit()

    bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup=start_keyboard())
    session.close()

@bot.message_handler(commands=['admin'])
def cmd_start(message: Message):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not user:
        user = User(telegram_id=message.from_user.id, is_admin=message.from_user.id in ADMINS)
        session.add(user)
        session.commit()

    if user.is_admin:
        show_admin_panel(message.chat.id, page=1)
    else:
        bot.send_message(message.chat.id, "Вы не являетесь администратором")
    session.close()

@bot.callback_query_handler(func=lambda c: c.data == "start_form")
def start_form(callback: CallbackQuery):
    session = SessionLocal()
    existing = session.query(Application).filter_by(user_id=callback.from_user.id).first()
    session.close()
    if existing:
        bot.answer_callback_query(callback.id, "Вы уже оставили заявку.")
        return
    user_states[callback.from_user.id] = {'step': 'type'}
    bot.edit_message_text("Что вы хотите купить?", callback.message.chat.id, callback.message.message_id, reply_markup=property_type_keyboard())

@bot.callback_query_handler(func=lambda c: c.data.startswith("apt") or c.data.startswith("house") or c.data.startswith("land"))
def handle_type(callback: CallbackQuery):
    state = user_states.get(callback.from_user.id)
    if not state: return

    data = callback.data
    if data == "apt":
        state.update({'type': 'Квартира', 'step': 'apt_stage'})
        bot.edit_message_text("Строящаяся или сданная?", callback.message.chat.id, callback.message.message_id, reply_markup=apt_stage_keyboard())

    elif data == "apt_new":
        state.update({'sub_type': 'Строящаяся', 'step': 'rooms'})
        bot.edit_message_text("Сколько комнат?", callback.message.chat.id, callback.message.message_id, reply_markup=rooms_keyboard())

    elif data == "apt_ready":
        state.update({'sub_type': 'Сданная', 'step': 'region'})
        bot.edit_message_text("Выберите район", callback.message.chat.id, callback.message.message_id, reply_markup=region_keyboard())

    elif data == "house":
        state.update({'type': 'Дом', 'step': 'land'})
        bot.edit_message_text("Участок уже есть?", callback.message.chat.id, callback.message.message_id, reply_markup=house_land_keyboard())

    elif data == "land_yes":
        state.update({'sub_type': 'Есть участок', 'step': 'material'})
        bot.edit_message_text("Какой материал дома?", callback.message.chat.id, callback.message.message_id, reply_markup=material_keyboard())

    elif data == "land_no":
        state.update({'sub_type': 'Нет участка', 'step': 'region'})
        bot.edit_message_text("Выберите район для покупки", callback.message.chat.id, callback.message.message_id, reply_markup=region_keyboard())

@bot.callback_query_handler(func=lambda c: c.data.endswith("_rooms"))
def handle_rooms(callback: CallbackQuery):
    state = user_states.get(callback.from_user.id)
    if not state: return
    state['rooms'] = callback.data.replace("_rooms", "")
    state['step'] = 'name'
    bot.send_message(callback.message.chat.id, "Введите ваше имя", reply_markup=cancel_keyboard())

@bot.callback_query_handler(func=lambda c: c.data.startswith("region_"))
def handle_region(callback: CallbackQuery):
    state = user_states.get(callback.from_user.id)
    if not state: return
    state['region'] = callback.data.replace("region_", "")
    if state['type'] == "Квартира":
        state['step'] = 'rooms'
        bot.edit_message_text("Сколько комнат?", callback.message.chat.id, callback.message.message_id, reply_markup=rooms_keyboard())
    else:
        state['step'] = 'name'
        bot.send_message(callback.message.chat.id, "Введите ваше имя", reply_markup=cancel_keyboard())

@bot.callback_query_handler(func=lambda c: c.data.startswith("mat_"))
def handle_material(callback: CallbackQuery):
    state = user_states.get(callback.from_user.id)
    if not state: return
    state['material'] = "Камень" if "stone" in callback.data else "Дерево"
    state['step'] = 'name'
    bot.send_message(callback.message.chat.id, "Введите ваше имя", reply_markup=cancel_keyboard())

@bot.message_handler(func=lambda m: m.from_user.id in user_states and user_states[m.from_user.id].get('step') == 'name')
def get_name(message: Message):
    state = user_states[message.from_user.id]
    state['name'] = message.text.strip()
    state['step'] = 'phone'
    bot.send_message(message.chat.id, "Введите ваш номер телефона", reply_markup=cancel_keyboard())

@bot.message_handler(func=lambda m: m.from_user.id in user_states and user_states[m.from_user.id].get('step') == 'phone')
def get_phone(message: Message):
    state = user_states[message.from_user.id]
    phone = message.text.strip()
    if not is_valid_phone(phone):
        bot.send_message(message.chat.id, "❌ Неверный формат номера. Введите снова.")
        return

    state['phone'] = phone
    session = SessionLocal()
    app = Application(
        user_id=message.from_user.id,
        type=state.get('type'),
        sub_type=state.get('sub_type'),
        region=state.get('region'),
        rooms=state.get('rooms'),
        material=state.get('material'),
        name=state.get('name'),
        phone=phone
    )
    session.add(app)
    session.commit()
    session.close()

    bot.send_message(message.chat.id, "✅ Ваша заявка принята!")
    user_states.pop(message.from_user.id, None)

@bot.callback_query_handler(func=lambda c: c.data == "cancel")
def cancel(callback: CallbackQuery):
    user_states.pop(callback.from_user.id, None)
    bot.edit_message_text("❌ Заявка отменена.", callback.message.chat.id, callback.message.message_id)

def show_admin_panel(chat_id, page=1):
    session = SessionLocal()
    all_apps = session.query(Application).order_by(Application.timestamp.desc()).all()
    session.close()

    per_page = 5
    total_pages = (len(all_apps) + per_page - 1) // per_page
    start = (page - 1) * per_page
    apps = all_apps[start:start+per_page]
    kb = get_applications_keyboard(apps, page, total_pages)
    bot.send_message(chat_id, "📦 Заявки", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("page_"))
def handle_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[1])
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    show_admin_panel(callback.message.chat.id, page)

@bot.callback_query_handler(func=lambda c: c.data.startswith("view_"))
def view_app(callback: CallbackQuery):
    app_id = int(callback.data.split("_")[1])
    session = SessionLocal()
    app = session.query(Application).get(app_id)
    session.close()
    if not app:
        bot.answer_callback_query(callback.id, "Заявка не найдена")
        return

    text = (
        f"📄 Заявка #{app.id}\n"
        f"Тип: {app.type or '-'}\n"
        f"Подтип: {app.sub_type or '-'}\n"
        f"Район: {app.region or '-'}\n"
        f"Комнаты: {app.rooms or '-'}\n"
        f"Материал: {app.material or '-'}\n"
        f"Имя: {app.name}\n"
        f"Телефон: {app.phone}\n"
        f"Комментарий: {app.comment or '—'}\n"
        f"Статус: {app.status or 'Новая'}\n"
        f"Дата: {app.timestamp.strftime('%Y-%m-%d %H:%M')}"
    )
    bot.send_message(callback.message.chat.id, text, reply_markup=get_application_detail_kb(app.id))

@bot.callback_query_handler(func=lambda c: c.data.startswith("delete_"))
def delete_app(callback: CallbackQuery):
    app_id = int(callback.data.split("_")[1])
    session = SessionLocal()
    app = session.query(Application).get(app_id)
    if app:
        session.delete(app)
        session.commit()
    session.close()
    bot.answer_callback_query(callback.id, "Удалено")
    bot.delete_message(callback.message.chat.id, callback.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("comment_"))
def comment_app(callback: CallbackQuery):
    app_id = int(callback.data.split("_")[1])
    user_states[callback.from_user.id] = {'step': 'comment', 'app_id': app_id}
    bot.send_message(callback.message.chat.id, "Введите комментарий (до 250 символов)")

@bot.message_handler(func=lambda m: m.from_user.id in user_states and user_states[m.from_user.id].get('step') == 'comment')
def save_comment(message: Message):
    state = user_states.pop(message.from_user.id)
    session = SessionLocal()
    app = session.query(Application).get(state['app_id'])
    if app:
        app.comment = message.text[:250]
        session.commit()
        bot.send_message(message.chat.id, "✅ Комментарий сохранён.")
    session.close()

@bot.callback_query_handler(func=lambda c: c.data.startswith("status_"))
def status_app(callback: CallbackQuery):
    app_id = int(callback.data.split("_")[1])
    user_states[callback.from_user.id] = {'step': 'status', 'app_id': app_id}
    bot.send_message(callback.message.chat.id, "Введите статус (до 30 символов)")

@bot.message_handler(func=lambda m: m.from_user.id in user_states and user_states[m.from_user.id].get('step') == 'status')
def save_status(message: Message):
    state = user_states.pop(message.from_user.id)
    session = SessionLocal()
    app = session.query(Application).get(state['app_id'])
    if app:
        app.status = message.text[:30]
        session.commit()
        bot.send_message(message.chat.id, "✅ Статус обновлён.")
    session.close()

@bot.callback_query_handler(func=lambda c: c.data == "export")
def export_excel(callback: CallbackQuery):
    session = SessionLocal()
    apps = session.query(Application).all()
    session.close()
    stream = generate_excel(apps)
    bot.send_document(callback.message.chat.id, InputFile(stream, "заявки.xlsx"))

@bot.callback_query_handler(func=lambda c: c.data == "stats")
def stats(callback: CallbackQuery):
    session = SessionLocal()
    total = session.query(Application).count()
    by_type = session.query(Application.type, func.count()).group_by(Application.type).all()
    session.close()

    text = f"📊 Всего заявок: {total}\n"
    for t, count in by_type:
        text += f"- {t}: {count}\n"
    bot.send_message(callback.message.chat.id, text)

bot.infinity_polling()
