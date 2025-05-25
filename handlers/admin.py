from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards import *
from states import AdminStates
from database import SessionLocal, Application, User, Config
from utils import is_admin, get_statistics, export_to_excel, get_config_value, set_config_value
from datetime import datetime, timedelta

router = Router()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав администратора.")
        return
    
    await message.answer("🔧 Панель администратора:", reply_markup=get_admin_keyboard())

@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    await callback.message.edit_text("🔧 Панель администратора:", reply_markup=get_admin_keyboard())

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    stats = get_statistics()
    
    text = f"📊 Статистика:\n\n"
    text += f"👥 Всего пользователей: {stats['total_users']}\n"
    text += f"📋 Всего заявок: {stats['total_applications']}\n"
    text += f"🏠 Заявки на квартиры: {stats['apartment_applications']}\n"
    text += f"🏡 Заявки на дома: {stats['house_applications']}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "admin_applications")
async def admin_applications(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📋 Список заявок:",
        reply_markup=get_applications_keyboard()
    )

@router.callback_query(F.data.startswith("apps_page_"))
async def applications_page(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    page = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        "📋 Список заявок:",
        reply_markup=get_applications_keyboard(page)
    )

@router.callback_query(F.data.startswith("app_"))
async def view_application(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    app_id = int(callback.data.split("_")[1])
    
    db = SessionLocal()
    try:
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            await callback.answer("Заявка не найдена", show_alert=True)
            return
        
        user = db.query(User).filter(User.user_id == app.user_id).first()
        
        status_text = {
            "new": "🆕 Новая",
            "in_progress": "⏳ В работе", 
            "completed": "✅ Завершена",
            "cancelled": "❌ Отменена"
        }.get(app.status, "❓ Неизвестно")
        
        text = f"📋 Заявка #{app.id}\n\n"
        text += f"👤 Пользователь: {user.first_name if user else 'Неизвестно'}\n"
        text += f"📱 Телефон: {app.phone}\n"
        text += f"👨‍💼 Имя: {app.name}\n"
        text += f"🏠 Тип: {'Квартира' if app.property_type == 'apartment' else 'Дом'}\n"
        text += f"📍 Статус: {status_text}\n"
        
        if app.building_status:
            building_text = "Строящаяся" if app.building_status == "new" else "Сданная"
            text += f"🏗 Строительство: {building_text}\n"
        
        if app.district:
            text += f"📍 Район: {app.district}\n"
        
        if app.rooms:
            text += f"🚪 Комнат: {app.rooms}\n"
        
        if app.has_plot:
            text += f"🌳 Участок: {app.has_plot}\n"
        
        if app.house_type:
            text += f"🏠 Тип дома: {app.house_type}\n"
        
        if app.admin_comment:
            text += f"\n💬 Комментарий админа:\n{app.admin_comment}\n"
        
        text += f"\n📅 Создана: {app.created_at.strftime('%d.%m.%Y %H:%M')}"
        text += f"\n🔄 Обновлена: {app.updated_at.strftime('%d.%m.%Y %H:%M')}"
        
        await callback.message.edit_text(text, reply_markup=get_application_manage_keyboard(app_id))
        
    finally:
        db.close()

@router.callback_query(F.data.startswith("change_status_"))
async def change_status(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    app_id = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        f"Выберите новый статус для заявки #{app_id}:",
        reply_markup=get_status_keyboard(app_id)
    )

@router.callback_query(F.data.startswith("set_status_"))
async def set_status(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    parts = callback.data.split("_")
    app_id = int(parts[2])
    new_status = parts[3]
    
    db = SessionLocal()
    try:
        app = db.query(Application).filter(Application.id == app_id).first()
        if app:
            app.status = new_status
            app.updated_at = datetime.utcnow()
            db.commit()
            
            status_text = {
                "new": "🆕 Новая",
                "in_progress": "⏳ В работе",
                "completed": "✅ Завершена", 
                "cancelled": "❌ Отменена"
            }.get(new_status, "❓ Неизвестно")
            
            await callback.answer(f"Статус изменен на: {status_text}")
            
            # Возвращаемся к просмотру заявки
            await view_application(CallbackQuery(
                id=callback.id,
                from_user=callback.from_user,
                chat_instance=callback.chat_instance,
                message=callback.message,
                data=f"app_{app_id}"
            ))
        else:
            await callback.answer("Заявка не найдена", show_alert=True)
    finally:
        db.close()

@router.callback_query(F.data.startswith("add_comment_"))
async def add_comment_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    app_id = int(callback.data.split("_")[2])
    await state.update_data(app_id=app_id)
    
    await callback.message.edit_text(
        f"Введите комментарий для заявки #{app_id}:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить", callback_data=f"app_{app_id}")]
        ])
    )
    await state.set_state(AdminStates.waiting_for_comment)

@router.message(AdminStates.waiting_for_comment)
async def add_comment_handler(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    
    user_data = await state.get_data()
    app_id = user_data.get("app_id")
    
    db = SessionLocal()
    try:
        app = db.query(Application).filter(Application.id == app_id).first()
        if app:
            app.admin_comment = message.text
            app.updated_at = datetime.utcnow()
            db.commit()
            
            await message.answer(
                "✅ Комментарий добавлен!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="👀 Посмотреть заявку", callback_data=f"app_{app_id}")],
                    [InlineKeyboardButton(text="📋 К списку заявок", callback_data="admin_applications")]
                ])
            )
        else:
            await message.answer("❌ Заявка не найдена")
    finally:
        db.close()
    
    await state.clear()

@router.callback_query(F.data.startswith("delete_app_"))
async def delete_application_confirm(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    app_id = int(callback.data.split("_")[2])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_app_{app_id}")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data=f"app_{app_id}")]
    ])
    
    await callback.message.edit_text(
        f"⚠️ Вы уверены, что хотите удалить заявку #{app_id}?\n\nЭто действие нельзя отменить!",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("confirm_delete_app_"))
async def delete_application_execute(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    app_id = int(callback.data.split("_")[3])
    
    db = SessionLocal()
    try:
        app = db.query(Application).filter(Application.id == app_id).first()
        if app:
            user = db.query(User).filter(User.user_id == app.user_id).first()
            if user:
                user.has_application = False
            
            db.delete(app)
            db.commit()
            
            await callback.answer("✅ Заявка удалена!")
            await callback.message.edit_text(
                "📋 Список заявок:",
                reply_markup=get_applications_keyboard()
            )
        else:
            await callback.answer("❌ Заявка не найдена", show_alert=True)
    finally:
        db.close()


@router.callback_query(F.data == "admin_export")
async def admin_export(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    try:
        buffer = export_to_excel()
        
        file = BufferedInputFile(
            buffer.getvalue(),
            filename=f"applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        await callback.message.answer_document(file, caption="📊 Экспорт заявок")
        await callback.answer("Файл экспортирован!")
        
    except Exception as e:
        await callback.answer("Ошибка при экспорте файла.", show_alert=True)

@router.callback_query(F.data == "admin_settings")
async def admin_settings(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "⚙️ Настройки конфигурации:",
        reply_markup=get_settings_keyboard()
    )

@router.callback_query(F.data.startswith("settings_"))
async def settings_handler(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    setting_type = callback.data.replace('settings_', '')
    current_value = get_config_value(setting_type)
    
    await state.update_data(config_key=setting_type)
    
    text = f"⚙️ Настройка {setting_type}\n\n"
    text += f"Текущие значения:\n{current_value.replace(',', ', ')}\n\n"
    text += "Введите новые значения через запятую:"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="admin_settings")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_config_value)

@router.message(AdminStates.waiting_for_config_value)
async def config_value_handler(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    
    user_data = await state.get_data()
    config_key = user_data.get("config_key")
    
    set_config_value(config_key, message.text)
    
    await message.answer(
        f"✅ Настройки {config_key} обновлены!",
        reply_markup=get_settings_keyboard()
    )
    await state.clear()

@router.callback_query(F.data == "admin_admins")
async def admin_admins(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    db = SessionLocal()
    try:
        admins = db.query(User).filter(User.is_admin == True).all()
        
        text = "👥 Администраторы:\n\n"
        for admin in admins:
            text += f"• {admin.first_name} (@{admin.username or 'нет'}) - ID: {admin.user_id}\n"
        
        text += "\nДля управления администраторами используйте кнопки ниже:"
        
    finally:
        db.close()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Добавить админа", callback_data="add_admin"),
            InlineKeyboardButton(text="➖ Удалить админа", callback_data="remove_admin")
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "add_admin")
async def add_admin_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👥 Введите ID пользователя для добавления в администраторы:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить", callback_data="admin_admins")]
        ])
    )
    await state.set_state(AdminStates.waiting_for_admin_id)

@router.message(AdminStates.waiting_for_admin_id)
async def add_admin_handler(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    
    try:
        admin_id = int(message.text)
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == admin_id).first()
            if user:
                if user.is_admin:
                    await message.answer(
                        "❌ Пользователь уже является администратором!",
                        reply_markup=get_admin_keyboard()
                    )
                else:
                    user.is_admin = True
                    db.commit()
                    await message.answer(
                        f"✅ Пользователь {user.first_name} добавлен в администраторы!",
                        reply_markup=get_admin_keyboard()
                    )
            else:
                await message.answer(
                    "❌ Пользователь не найден в базе данных.",
                    reply_markup=get_admin_keyboard()
                )
        finally:
            db.close()
            
    except ValueError:
        await message.answer(
            "❌ Введите корректный числовой ID.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отменить", callback_data="admin_admins")]
            ])
        )
        return
    
    await state.clear()

@router.callback_query(F.data == "remove_admin")
async def remove_admin_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👥 Введите ID администратора для удаления из списка администраторов:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить", callback_data="admin_admins")]
        ])
    )
    await state.set_state(AdminStates.waiting_for_remove_admin_id)

@router.message(AdminStates.waiting_for_remove_admin_id)
async def remove_admin_handler(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    
    try:
        admin_id = int(message.text)
        
        # Проверяем, что пользователь не пытается удалить сам себя
        if admin_id == message.from_user.id:
            await message.answer(
                "❌ Вы не можете удалить себя из администраторов!",
                reply_markup=get_admin_keyboard()
            )
            await state.clear()
            return
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == admin_id).first()
            if user:
                if user.is_admin:
                    user.is_admin = False
                    db.commit()
                    await message.answer(
                        f"✅ Пользователь {user.first_name} удален из администраторов!",
                        reply_markup=get_admin_keyboard()
                    )
                else:
                    await message.answer(
                        "❌ Пользователь не является администратором!",
                        reply_markup=get_admin_keyboard()
                    )
            else:
                await message.answer(
                    "❌ Пользователь не найден в базе данных.",
                    reply_markup=get_admin_keyboard()
                )
        finally:
            db.close()
            
    except ValueError:
        await message.answer(
            "❌ Введите корректный числовой ID.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отменить", callback_data="admin_admins")]
            ])
        )
        return
    
    await state.clear()