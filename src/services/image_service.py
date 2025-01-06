import requests
import logging
from ..utils.config import OPENAI_API_KEY, IMAGES_DIR
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ImageService:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        # Стили для изображений с экспертными промптами
        self.style_prompts = {
            "default": {
                "prefix": "Create a highly detailed digital art masterpiece:",
                "suffix": "Render in professional digital art style with ultra-high detail, perfect lighting, volumetric atmosphere, dynamic composition, and cinematic color grading. Include subtle ambient occlusion, realistic textures, and careful attention to reflections and shadows."
            },
            "rick_and_morty": {
                "prefix": "Create an authentic Rick and Morty universe scene:",
                "suffix": """Replicate the exact Rick and Morty animation style with these key elements:
                1. Bold, thick black outlines (2-3 pixels) around all elements
                2. Signature color palette: vibrant greens for portals, toxic waste colors, saturated backgrounds
                3. Characteristic eye style: large white oval eyes with tiny black pupils, often dilated or constricted for expression
                4. Distinctive drool or spittle on character mouths
                5. Signature sci-fi elements: glowing technology, interdimensional portals, alien textures
                6. Exaggerated expressions with wrinkles around eyes and mouths
                7. Slightly wobbly, imperfect lines for that hand-drawn feel
                8. Flat color fills with minimal gradients
                9. Sharp angular shadows under characters
                10. Background elements in slightly muted colors compared to characters
                Make it look exactly like it was animated by the original Rick and Morty studio team."""
            },
            "simpsons": {
                "prefix": "Create an authentic Simpsons universe scene:",
                "suffix": """Replicate the exact Simpsons animation style with these essential elements:
                1. Signature yellow skin tone for human characters
                2. Distinctive overbite with round upper lip
                3. Large oval eyes with black pupils touching the top
                4. No visible neck lines
                5. Four fingers instead of five
                6. Bold black outlines around all elements
                7. Flat color fills with minimal shading
                8. Bright, saturated color palette
                9. Simple but expressive facial features
                10. Characteristic hair lines and spikes
                Make it look exactly like it was animated by the original Simpsons animation team."""
            },
            "oil_painting": {
                "prefix": "Create a masterful classical oil painting:",
                "suffix": """Paint in the grand tradition of classical oil painting with these techniques:
                1. Rich, layered impasto technique for texture
                2. Visible, confident brushstrokes showing movement
                3. Glazing technique for depth and luminosity
                4. Chiaroscuro lighting with dramatic shadows
                5. Traditional color palette with earth tones
                6. Careful attention to composition using the golden ratio
                7. Multiple layers of paint creating depth
                8. Subtle color transitions and blending
                9. Textural variations between different materials
                10. Classical atmospheric perspective
                Make it look like it was painted by a master artist from the Renaissance or Baroque period."""
            },
            "black_and_white": {
                "prefix": "Create a dramatic black and white artistic photograph:",
                "suffix": """Capture in classic black and white photography style with these elements:
                1. Full range of tones from pure black to bright white
                2. Sharp contrast with deep shadows
                3. Dramatic lighting reminiscent of film noir
                4. Zone system exposure for perfect tonal balance
                5. Careful attention to texture and form
                6. Crisp focus with selective depth of field
                7. Strong compositional elements
                8. Rich silver gelatin print quality
                9. Subtle grain texture
                10. Masterful use of negative space
                Make it look like it was shot by a master photographer using professional medium format film."""
            },
            "custom": None
        }
        
        # Загружаем кастомный стиль
        self.load_custom_style()
    
    def load_custom_style(self):
        """Загрузка кастомного стиля"""
        config_path = os.path.join(os.path.dirname(IMAGES_DIR), 'custom_style.txt')
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        self.style_prompts["custom"] = {
                            "prefix": lines[0].strip(),
                            "suffix": lines[1].strip()
                        }
        except Exception as e:
            logger.error(f"Ошибка при загрузке кастомного стиля: {e}")
    
    def save_custom_style(self, style_prompt):
        """Сохранение кастомного стиля"""
        try:
            # Разделяем стиль на prefix и suffix
            style_data = {
                "prefix": "Create an image in custom style:",
                "suffix": style_prompt
            }
            
            # Сохраняем в файл
            config_path = os.path.join(os.path.dirname(IMAGES_DIR), 'custom_style.txt')
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(f"{style_data['prefix']}\n{style_data['suffix']}")
            
            self.style_prompts["custom"] = style_data
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении кастомного стиля: {e}")
            return False

    def generate_image(self, description, style="default"):
        """Генерация изображения с учетом стиля"""
        try:
            # Получаем стиль
            style_data = self.style_prompts.get(style)
            if not style_data:
                style_data = self.style_prompts["default"]
            
            # Формируем промпт
            prefix = style_data["prefix"]
            suffix = style_data["suffix"]
            
            # Собираем полный промпт
            full_prompt = f"{prefix} {description}. {suffix}"
            
            logger.info(f"Генерация изображения. Промпт: {full_prompt}")
            
            payload = {
                "model": "dall-e-3",
                "prompt": full_prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "standard"
            }
            
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()['data'][0]['url']
            else:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Неизвестная ошибка')
                logger.error(f"Ошибка API при генерации изображения: {response.status_code}, {error_message}")
                return None
        except Exception as e:
            logger.error(f"Ошибка при генерации изображения: {str(e)}")
            return None

    def generate_description(self, text: str, style: str = "default") -> str:
        """Генерирует улучшенное описание для изображения с учетом стиля"""
        try:
            # Получаем данные стиля
            style_data = self.style_prompts.get(style, self.style_prompts["default"])
            if not style_data:
                style_data = self.style_prompts["default"]

            # Формируем запрос для GPT с учетом стиля
            prompt = f"""Как эксперт по стилю {style}, создай краткое но ёмкое описание для генерации изображения на основе: "{text}"

Требования:
1. Сохрани основную идею, сделав её более яркой

2. Добавь ключевые детали (10-15 элементов):
   - Основные объекты и их характеристики
   - Цвета и освещение
   - Композиция и настроение
   - Характерные элементы стиля
   - Важные детали окружения

3. Учти особенности стиля: {style_data['suffix']}

4. Сделай описание креативным:
   - Добавь 2-3 неожиданных, но уместных детали
   - Используй интересные художественные приёмы
   - Создай запоминающуюся композицию

Создай лаконичное но эффектное описание:"""
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                improved_text = response.json()['choices'][0]['message']['content'].strip()
                return improved_text
            else:
                logger.error(f"Ошибка API при генерации описания: {response.status_code}")
                return text
        except Exception as e:
            logger.error(f"Ошибка при генерации описания: {e}")
            return text

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