set -e

APP_DIR="/opt/RealtorBot"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="RealtorBot"
USER_NAME=$(whoami)

echo "Установка Python3 и venv..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

echo "Создание директории приложения..."
sudo mkdir -p "$APP_DIR"
sudo chown "$USER_NAME":"$USER_NAME" "$APP_DIR"

echo "Копирование файлов в $APP_DIR (предположим, requirements.txt и main.py уже в текущей директории)..."
cp requirements.txt "$APP_DIR/"
cp main.py "$APP_DIR/"

echo "Создание виртуального окружения..."
python3 -m venv "$VENV_DIR"

echo "Установка зависимостей..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

echo "Создание systemd-сервиса..."

SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Realtor Bot Service
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/python $APP_DIR/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Перезагрузка systemd и запуск сервиса..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "Готово! Статус сервиса:"
sudo systemctl status "$SERVICE_NAME" --no-pager
