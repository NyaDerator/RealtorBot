#!/bin/bash

read -p "Введите BOT_TOKEN: " BOT_TOKEN
read -p "Введите ваш Telegram ID (если несколько, через запятую): " ADMIN_IDS

echo "Создание .env файла..."
cat > .env <<EOF
BOT_TOKEN=${BOT_TOKEN}
ADMIN_IDS=${ADMIN_IDS}
EOF

echo "Установка Python и venv..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

echo "Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "Файл requirements.txt не найден!"
    exit 1
fi

deactivate

WORKING_DIR=$(pwd)
SERVICE_NAME="realtorbot"

echo "Создание systemd-сервиса..."

sudo bash -c "cat > /etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=realtorbot
After=network.target

[Service]
Type=simple
WorkingDirectory=${WORKING_DIR}
ExecStart=${WORKING_DIR}/venv/bin/python ${WORKING_DIR}/main.py
EnvironmentFile=${WORKING_DIR}/.env
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Запуск и включение сервиса..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}

echo "Готово! Бот запущен как systemd-сервис: ${SERVICE_NAME}"