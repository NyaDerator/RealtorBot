from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def start_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📋 Подать заявку", callback_data="start_form"))
    return kb

def cancel_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return kb

def property_type_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Квартира", callback_data="apt"))
    kb.add(InlineKeyboardButton("Дом", callback_data="house"))
    kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return kb

def apt_stage_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Строящаяся", callback_data="apt_new"))
    kb.add(InlineKeyboardButton("Сданная", callback_data="apt_ready"))
    kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return kb

def house_land_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Да", callback_data="land_yes"))
    kb.add(InlineKeyboardButton("Нет", callback_data="land_no"))
    kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return kb

def rooms_keyboard():
    kb = InlineKeyboardMarkup()
    for i in range(1, 5):
        kb.add(InlineKeyboardButton(f"{i} комн.", callback_data=f"{i}_rooms"))
    kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return kb

def region_keyboard():
    kb = InlineKeyboardMarkup()
    for region in ["Центр", "Север", "Юг", "Запад", "Восток"]:
        kb.add(InlineKeyboardButton(region, callback_data=f"region_{region}"))
    kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return kb

def material_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Камень", callback_data="mat_stone"))
    kb.add(InlineKeyboardButton("Дерево", callback_data="mat_wood"))
    kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return kb
