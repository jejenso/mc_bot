import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота, полученный от @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Telegram ID администратора (узнать у @userinfobot)
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Юзернейм администратора без @ (для упоминаний в чате)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")

# Токен доступа ЮMoney (получить на https://yoomoney.ru/oauth/authorize)
YOOMONEY_TOKEN = os.getenv("YOOMONEY_TOKEN", "")

# Номер кошелька ЮMoney (просто для отображения реквизитов игрокам)
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET", "")

# Номер банковской карты для ручных переводов (отображается в реквизитах)
CARD_NUMBER = os.getenv("CARD_NUMBER", "0000 0000 0000 0000")

# Стоимость сервера в сутки, руб.
SERVER_DAILY_COST = float(os.getenv("SERVER_DAILY_COST", "46.35"))

# Путь к файлу базы данных SQLite
DB_PATH = os.getenv("DB_PATH", "bot.db")

# IP и порт сервера Minecraft
SERVER_IP = os.getenv("SERVER_IP", "your.server.ip")
SERVER_PORT = os.getenv("SERVER_PORT", "25565")
SERVER_VERSION = os.getenv("SERVER_VERSION", "1.21.1 Fabric")

# Ссылка на моды (архив/папка, куда вы выложили модпак — Google Drive, Yandex Disk и т.п.)
MODS_LINK = os.getenv("MODS_LINK", "https://example.com/mods.zip")
