import os

# --- Обязательные переменные окружения (задаются на Railway, НЕ в коде) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")          # токен от @BotFather
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # твой личный telegram id (узнать у @userinfobot)

# --- Тарифы ---
TRIAL_DAYS = 3
TARIFFS = {
    "week": {"label": "50₽ / неделя", "price": 50, "days": 7},
    "month": {"label": "100₽ / месяц", "price": 100, "days": 30},
}

# --- Реквизиты для оплаты ---
CARD_NUMBER = "2202 2081 1624 5920"   # ЗАМЕНИ на свой номер карты Сбербанк

# --- Файл базы данных ---
DB_PATH = "jensocraft.db"

# --- Название сервера/канала для текстов ---
SERVER_NAME = "Jensocraft"
