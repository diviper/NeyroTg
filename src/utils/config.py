import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Конфигурация API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Проверка API ключа
if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith('sk-'):
    raise ValueError("Ошибка: Неверный формат API ключа")

# Конфигурация путей
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

# Конфигурация UI
UI_CONFIG = {
    'window_title': "Генератор Изображений",
    'window_size': "900x700",
    'bg_color': "#1E1E1E",
    'text_color': "white",
    'button_color': "#4CAF50"
} 