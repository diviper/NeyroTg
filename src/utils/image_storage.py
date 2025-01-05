import os
import json
from datetime import datetime
from PIL import Image
from io import BytesIO
import requests
from .config import IMAGES_DIR

class ImageStorage:
    def __init__(self):
        self.history_file = os.path.join(IMAGES_DIR, 'history.json')
        self._load_history()

    def _load_history(self):
        """Загрузка истории из файла"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_image(self, image_url, description):
        """Сохранение изображения и информации о нем"""
        try:
            # Загрузка изображения
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Генерация имени файла
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_filename = f'image_{timestamp}.png'
            image_path = os.path.join(IMAGES_DIR, image_filename)
            
            # Сохранение изображения
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            # Добавление в историю
            history_entry = {
                'timestamp': timestamp,
                'description': description,
                'image_path': image_filename
            }
            self.history.append(history_entry)
            
            # Сохранение истории
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            
            return image_path
            
        except Exception as e:
            print(f"Ошибка при сохранении изображения: {str(e)}")
            return None

    def get_history(self):
        """Получение истории генераций"""
        return self.history

    def load_image(self, image_path):
        """Загрузка изображения из файла"""
        try:
            full_path = os.path.join(IMAGES_DIR, image_path)
            if os.path.exists(full_path):
                return Image.open(full_path)
            return None
        except Exception as e:
            print(f"Ошибка при загрузке изображения: {str(e)}")
            return None 