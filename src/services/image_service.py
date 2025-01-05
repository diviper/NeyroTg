import requests
from ..utils.config import OPENAI_API_KEY, IMAGES_DIR
import os

class ImageService:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        # Стили для изображений
        self.style_prompts = {
            "default": "Digital art style, clear details, vibrant colors.",
            "rick_and_morty": "In the style of Rick and Morty animation, with bold lines and vibrant colors.",
            "simpsons": "In the style of The Simpsons animation, with yellow skin tones and characteristic features.",
            "oil_painting": "In the style of an oil painting, with visible brush strokes and rich textures.",
            "black_and_white": "Black and white artistic photography style, with strong contrast and dramatic lighting.",
            "custom": None  # Для кастомного стиля
        }
        
        # Загружаем кастомный стиль, если он есть
        self.load_custom_style()
    
    def load_custom_style(self):
        """Загрузка кастомного стиля из файла"""
        config_path = os.path.join(os.path.dirname(IMAGES_DIR), 'custom_style.txt')
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.style_prompts["custom"] = f.read().strip()
        except Exception as e:
            print(f"Ошибка при загрузке кастомного стиля: {e}")
    
    def save_custom_style(self, style_prompt):
        """Сохранение кастомного стиля в файл"""
        config_path = os.path.join(os.path.dirname(IMAGES_DIR), 'custom_style.txt')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(style_prompt)
            self.style_prompts["custom"] = style_prompt
            return True
        except Exception as e:
            print(f"Ошибка при сохранении кастомного стиля: {e}")
            return False

    def generate_image(self, description, style="default"):
        """Генерация изображения через OpenAI API"""
        # Получаем стиль
        style_prompt = self.style_prompts.get(style)
        if style == "custom" and not style_prompt:
            style_prompt = self.style_prompts["default"]
        
        full_prompt = f"{description}. {style_prompt}"
        
        payload = {
            "model": "dall-e-3",
            "prompt": full_prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "standard"
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()['data'][0]['url']
            else:
                print(f"Ошибка API: {response.status_code}")
                return None
        except Exception as e:
            print(f"Ошибка при генерации изображения: {str(e)}")
            return None

    def generate_description(self, prompt):
        """Генерация улучшенного описания через OpenAI API"""
        if not prompt or prompt.isspace():
            # Если текст пустой, генерируем случайное описание
            base_prompt = "Создай интересное описание для случайной сцены. Описание должно быть детальным, но не длиннее 2-3 предложений."
        else:
            # Если есть текст, улучшаем его
            base_prompt = f"""Улучши следующее описание для генерации изображения, сделав его более детальным и точным: "{prompt}"
            
            Требования к улучшению:
            1. Сохрани основную идею и стиль
            2. Добавь важные детали (цвета, формы, освещение)
            3. Используй художественные термины
            4. Сделай описание более конкретным
            5. Оставь длину в пределах 2-3 предложений
            
            Улучшенное описание:"""

        payload = {
            "model": "gpt-4",
            "messages": [{
                "role": "user",
                "content": base_prompt
            }]
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"Ошибка API: {response.status_code}"
        except Exception as e:
            return f"Произошла ошибка: {str(e)}"

    def translate_text(self, text, target_lang):
        """Перевод текста через OpenAI API"""
        language_names = {
            "en": "английский",
            "ru": "русский",
            "es": "испанский",
            "fr": "французский",
            "de": "немецкий",
            "ja": "японский",
            "zh": "китайский"
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [{
                "role": "user",
                "content": f"Переведи следующий текст на {language_names.get(target_lang, target_lang)} язык: {text}"
            }]
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"Ошибка перевода: {response.status_code}"
        except Exception as e:
            return f"Ошибка при переводе: {str(e)}" 