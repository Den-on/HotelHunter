import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены, так как отсутствует файл .env.template")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
DATABASE_NAME = os.getenv("DATABASE_NAME")
API_URL = os.getenv("API_URL")

DEFAULT_COMMANDS = (
    ('city_selection', 'Ввести город'),
    ('date_change', 'Сменить даты'),
    ('sorting', 'Изменить сортировку')
)
