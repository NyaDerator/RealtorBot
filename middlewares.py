from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database import SessionLocal, User

class UserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        username = None
        first_name = None
        
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
            user_id = user.id
            username = user.username
            first_name = user.first_name
        
        if user_id:
            db = SessionLocal()
            try:
                db_user = db.query(User).filter(User.user_id == user_id).first()
                if not db_user:
                    db_user = User(
                        user_id=user_id,
                        username=username,
                        first_name=first_name
                    )
                    db.add(db_user)
                    db.commit()
                
                data["user"] = db_user
            finally:
                db.close()
        
        return await handler(event, data)