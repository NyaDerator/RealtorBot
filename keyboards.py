from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import SessionLocal, Config, Application, User

def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="📝 Подать заявку", callback_data="start_application")]
    ])

def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")]
    ])

def get_property_type_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Квартира", callback_data="property_apartment")],
        [InlineKeyboardButton(text="🏡 Дом", callback_data="property_house")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")]
    ])
    return keyboard

def get_building_status_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏗 Строящаяся", callback_data="building_new")],
        [InlineKeyboardButton(text="✅ Сданная", callback_data="building_ready")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")]
    ])

def get_has_plot_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="plot_yes")],
        [InlineKeyboardButton(text="❌ Нет", callback_data="plot_no")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")]
    ])

def get_config_keyboard(config_key):
    db = SessionLocal()
    try:
        config = db.query(Config).filter(Config.key == config_key).first()
        if not config:
            return get_cancel_keyboard()
        
        values = config.value.split(",")
        keyboard = []
        
        for value in values:
            keyboard.append([InlineKeyboardButton(text=value, callback_data=f"{config_key}_{value}")])
        
        keyboard.append([InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    finally:
        db.close()

def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📋 Заявки", callback_data="admin_applications")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings")],
        [InlineKeyboardButton(text="👥 Администраторы", callback_data="admin_admins")],
        [InlineKeyboardButton(text="📤 Экспорт", callback_data="admin_export")]
    ])

def get_applications_keyboard(page=0, per_page=5):
    db = SessionLocal()
    try:
        total = db.query(Application).count()
        applications = db.query(Application).order_by(Application.created_at.desc()).offset(page * per_page).limit(per_page).all()
        
        keyboard = []
        
        # Кнопки с заявками
        for app in applications:
            user = db.query(User).filter(User.user_id == app.user_id).first()
            status_emoji = {
                "new": "🆕",
                "in_progress": "⏳",
                "completed": "✅",
                "cancelled": "❌"
            }.get(app.status, "❓")
            
            button_text = f"{status_emoji} {app.name} ({app.id})"
            keyboard.append([InlineKeyboardButton(text=button_text, callback_data=f"app_{app.id}")])
        
        # Пагинация
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"apps_page_{page-1}"))
        if (page + 1) * per_page < total:
            nav_buttons.append(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"apps_page_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_applications")])
        keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    finally:
        db.close()

def get_application_manage_keyboard(app_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Изменить статус", callback_data=f"change_status_{app_id}")],
        [InlineKeyboardButton(text="💬 Добавить комментарий", callback_data=f"add_comment_{app_id}")],
        [InlineKeyboardButton(text="🗑 Удалить заявку", callback_data=f"delete_app_{app_id}")],
        [InlineKeyboardButton(text="⬅️ К списку заявок", callback_data="admin_applications")]
    ])

def get_status_keyboard(app_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Новая", callback_data=f"set_status_{app_id}_new")],
        [InlineKeyboardButton(text="⏳ В работе", callback_data=f"set_status_{app_id}_in_progress")],
        [InlineKeyboardButton(text="✅ Завершена", callback_data=f"set_status_{app_id}_completed")],
        [InlineKeyboardButton(text="❌ Отменена", callback_data=f"set_status_{app_id}_cancelled")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"app_{app_id}")]
    ])

def get_applications_filter_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Квартиры", callback_data="filter_apartment")],
        [InlineKeyboardButton(text="🏡 Дома", callback_data="filter_house")],
        [InlineKeyboardButton(text="🆕 Новые", callback_data="filter_new")],
        [InlineKeyboardButton(text="⏳ В работе", callback_data="filter_in_progress")],
        [InlineKeyboardButton(text="✅ Завершенные", callback_data="filter_completed")],
        [InlineKeyboardButton(text="🔄 Все", callback_data="filter_all")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")]
    ])

def get_settings_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏘 Районы", callback_data="settings_districts")],
        [InlineKeyboardButton(text="🏠 Комнаты", callback_data="settings_rooms")],
        [InlineKeyboardButton(text="🏗 Типы домов", callback_data="settings_house_types")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")]
    ])