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

# Версия приложения
VERSION = "1.2.0"

# Темная тема
DARK_THEME = {
    'bg_color': "#1E1E1E",
    'secondary_bg': "#2E2E2E",
    'text_color': "#FFFFFF",
    'accent_color': "#4CAF50",
    'button_bg': "#3E3E3E",
    'button_fg': "#FFFFFF",
    'highlight_bg': "#4a4a4a",
    'border_color': "#3E3E3E",
    'error_color': "#FF5252",
    'success_color': "#4CAF50",
    'scrollbar_bg': "#3E3E3E",
    'scrollbar_fg': "#4a4a4a",
    'selection_bg': "#4a4a4a",
    'selection_fg': "#FFFFFF"
}

# Конфигурация UI
UI_CONFIG = {
    'window_title': f"NeyroTg v{VERSION} - Генератор Изображений",
    'window_size': "1200x800",
    'min_width': 1000,
    'min_height': 800,
    'font_family': 'Helvetica',
    'font_sizes': {
        'title': 24,
        'subtitle': 16,
        'normal': 12,
        'small': 10
    },
    'padding': {
        'small': 5,
        'normal': 10,
        'large': 20
    },
    **DARK_THEME
} 