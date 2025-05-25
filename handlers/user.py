from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from keyboards import *
from states import ApplicationStates
from database import SessionLocal, Application, User
from utils import validate_phone, validate_name

router = Router()

@router.message(CommandStart())
async def start_command(message: Message, user: User):
    text = f"Добро пожаловать, {user.first_name}!\n\nВыберите действие:"
    await message.answer(text, reply_markup=get_main_keyboard())

@router.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery, user: User):
    db = SessionLocal()
    try:
        app = db.query(Application).filter(Application.user_id == user.user_id).first()
        
        if app:
            status_text = {
                "new": "🆕 Новая",
                "in_progress": "⏳ В работе",
                "completed": "✅ Завершена",
                "cancelled": "❌ Отменена"
            }.get(app.status, "❓ Неизвестно")
            
            text = f"👤 Ваш профиль:\n\n"
            text += f"Имя: {app.name}\n"
            text += f"Телефон: {app.phone}\n"
            text += f"Тип недвижимости: {'Квартира' if app.property_type == 'apartment' else 'Дом'}\n"
            text += f"Статус заявки: {status_text}\n"
            
            if app.building_status:
                text += f"Статус строительства: {app.building_status}\n"
            if app.district:
                text += f"Район: {app.district}\n"
            if app.rooms:
                text += f"Комнаты: {app.rooms}\n"
            if app.has_plot:
                text += f"Участок: {app.has_plot}\n"
            if app.house_type:
                text += f"Тип дома: {app.house_type}\n"
            if app.admin_comment:
                text += f"\n💬 Комментарий: {app.admin_comment}\n"
            
            text += f"\nДата подачи: {app.created_at.strftime('%d.%m.%Y %H:%M')}"
            
            # Кнопка для удаления заявки пользователем
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🗑 Удалить заявку", callback_data="delete_my_app")],
                [InlineKeyboardButton(text="⬅️ Главное меню", callback_data="main_menu")]
            ])
        else:
            text = "У вас пока нет поданных заявок."
            keyboard = get_main_keyboard()
    finally:
        db.close()
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "delete_my_app")
async def delete_my_app(callback: CallbackQuery, user: User):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_delete_my_app")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="profile")]
    ])
    
    await callback.message.edit_text(
        "⚠️ Вы уверены, что хотите удалить свою заявку?\n\nПосле удаления вы сможете подать новую заявку.",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "confirm_delete_my_app")
async def confirm_delete_my_app(callback: CallbackQuery, user: User):
    db = SessionLocal()
    try:
        app = db.query(Application).filter(Application.user_id == user.user_id).first()
        if app:
            db.delete(app)
            user.has_application = False
            db.commit()
            
            await callback.message.edit_text(
                "✅ Ваша заявка удалена. Теперь вы можете подать новую заявку.",
                reply_markup=get_main_keyboard()
            )
        else:
            await callback.message.edit_text(
                "Заявка не найдена.",
                reply_markup=get_main_keyboard()
            )
    finally:
        db.close()

@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, user: User):
    text = f"Главное меню"
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())

@router.callback_query(F.data == "start_application")
async def start_application(callback: CallbackQuery, user: User):
    if user.has_application:
        await callback.answer("У вас уже есть активная заявка! Удалите текущую заявку в профиле, чтобы подать новую.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "Что вы хотите купить?",
        reply_markup=get_property_type_keyboard()
    )

# Остальные обработчики остаются такими же...
@router.callback_query(F.data.startswith("property_"))
async def property_type_handler(callback: CallbackQuery, state: FSMContext):
    property_type = callback.data.split("_")[1]
    await state.update_data(property_type=property_type)
    
    if property_type == "apartment":
        await callback.message.edit_text(
            "Квартира строящаяся или сданная?",
            reply_markup=get_building_status_keyboard()
        )
    else:
        await callback.message.edit_text(
            "Участок уже есть?",
            reply_markup=get_has_plot_keyboard()
        )

@router.callback_query(F.data.startswith("building_"))
async def building_status_handler(callback: CallbackQuery, state: FSMContext):
    status = callback.data.split("_")[1]
    await state.update_data(building_status=status)
    
    if status == "new":
        await callback.message.edit_text(
            "Выберите количество комнат:",
            reply_markup=get_config_keyboard("rooms")
        )
    else:
        await callback.message.edit_text(
            "Выберите район:",
            reply_markup=get_config_keyboard("districts")
        )

@router.callback_query(F.data.startswith("plot_"))
async def plot_handler(callback: CallbackQuery, state: FSMContext):
    has_plot = "Да" if callback.data.split("_")[1] == "yes" else "Нет"
    await state.update_data(has_plot=has_plot)
    
    if has_plot == "Да":
        await callback.message.edit_text(
            "Выберите тип дома:",
            reply_markup=get_config_keyboard("house_types")
        )
    else:
        await callback.message.edit_text(
            "Выберите район для покупки участка:",
            reply_markup=get_config_keyboard("districts")
        )

@router.callback_query(F.data.startswith("districts_"))
async def district_handler(callback: CallbackQuery, state: FSMContext):
    district = callback.data.split("_", 1)[1]
    await state.update_data(district=district)
    
    user_data = await state.get_data()
    
    if user_data.get("property_type") == "apartment" and user_data.get("building_status") == "ready":
        await callback.message.edit_text(
            "Выберите количество комнат:",
            reply_markup=get_config_keyboard("rooms")
        )
    else:
        await callback.message.edit_text(
            "Введите ваше имя:",
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(ApplicationStates.waiting_for_name)

@router.callback_query(F.data.startswith("rooms_"))
async def rooms_handler(callback: CallbackQuery, state: FSMContext):
    rooms = callback.data.split("_", 1)[1]
    await state.update_data(rooms=rooms)
    
    await callback.message.edit_text(
        "Введите ваше имя:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ApplicationStates.waiting_for_name)

@router.callback_query(F.data.startswith("house_types_"))
async def house_type_handler(callback: CallbackQuery, state: FSMContext):
    house_type = callback.data.split("_", 1)[1]
    await state.update_data(house_type=house_type.replace('types_ ', ''))
    
    await callback.message.edit_text(
        "Введите ваше имя:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ApplicationStates.waiting_for_name)

@router.message(ApplicationStates.waiting_for_name)
async def name_handler(message: Message, state: FSMContext):
    if not validate_name(message.text):
        await message.answer(
            "Пожалуйста, введите корректное имя (только буквы):",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    await state.update_data(name=message.text)
    await message.answer(
        "Введите ваш номер телефона:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ApplicationStates.waiting_for_phone)

@router.message(ApplicationStates.waiting_for_phone)
async def phone_handler(message: Message, state: FSMContext, user: User):
    if not validate_phone(message.text):
        await message.answer(
            "Пожалуйста, введите корректный номер телефона:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    user_data = await state.get_data()
    
    db = SessionLocal()
    try:
        application = Application(
            user_id=user.user_id,
            property_type=user_data.get("property_type"),
            building_status=user_data.get("building_status"),
            district=user_data.get("district"),
            rooms=user_data.get("rooms"),
            has_plot=user_data.get("has_plot"),
            house_type=user_data.get("house_type"),
            name=user_data.get("name"),
            phone=message.text,
            status="new"
        )
        
        db.add(application)
        user.has_application = True
        db.commit()
        
    finally:
        db.close()
    
    await message.answer(
        "✅ Ваша заявка успешно подана!\n\nНаш менеджер свяжется с вами в ближайшее время.",
        reply_markup=get_main_keyboard()
    )
    await state.clear()

@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Операция отменена.",
        reply_markup=get_main_keyboard()
    )