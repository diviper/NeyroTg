import requests
from ..utils.config import OPENAI_API_KEY

class ImageService:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

    def generate_image(self, description):
        """Генерация изображения через OpenAI API"""
        payload = {
            "model": "dall-e-3",
            "prompt": f"{description}. Digital art style, clear details, vibrant colors.",
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

    def generate_description(self, user_input):
        """Генерация описания через OpenAI API"""
        payload = {
            "model": "gpt-4",
            "messages": [{
                "role": "user",
                "content": f"Опиши сцену: {user_input}. Описание должно быть точным и соответствовать запрошенному изображению."
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