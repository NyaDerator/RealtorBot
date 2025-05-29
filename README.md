# 🏡 RealtorBot: Простой бот для подачи заявок на недвижимость

![aiogram](https://img.shields.io/badge/aiogram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-c71e00?style=for-the-badge&logo=sqlite&logoColor=white)
![dotenv](https://img.shields.io/badge/dotenv-2fb6f5?style=for-the-badge&logo=dotenv&logoColor=white)
![openpyxl](https://img.shields.io/badge/openpyxl-1D6F42?style=for-the-badge&logo=microsoft-excel&logoColor=white)
![requests](https://img.shields.io/badge/requests-3776AB?style=for-the-badge&logo=python&logoColor=white)


RealtorBot — лёгкий и практичный Telegram-бот для сбора заявок на недвижимость с удобной админкой и хранением данных.

---

## 📊 Функционал
1. 📂 Сохранение всех заявок в SQLite базу данных
2. 📨 Простая подача и удаление заявок пользователем
3. 📅 Админ-панель:
   - Удаление/обработка заявок
   - Комментарии от администратора
   - Статус заявки
   - Статистика
   - Управление админами
   - Экспорт в Excel (.xlsx)

---

## ✨ Быстрый старт

### 1. Установка
Сделайте скрипт установки исполняемым и запустите его:
```bash
chmod +x install.sh
./install.sh
```
Следуйте инструкциям на экране.

---

### 2. Управление ботом
#### ✅ Статус:
```bash
sudo systemctl status realtorbot.service
```

#### ↻ Перезапуск:
```bash
sudo systemctl restart realtorbot.service
```

#### ❌ Остановка:
```bash
sudo systemctl stop realtorbot.service
```

---

### 🔎 Telegram ID
Узнайте свой Telegram ID через бота [@userinfobot](https://t.me/userinfobot)
