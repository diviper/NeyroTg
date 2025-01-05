import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
from ..services.image_service import ImageService
from ..utils.image_storage import ImageStorage
from ..utils.config import UI_CONFIG

class ImageGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title(UI_CONFIG['window_title'])
        self.root.geometry(UI_CONFIG['window_size'])
        self.root.configure(bg=UI_CONFIG['bg_color'])

        # Инициализация сервисов
        self.image_service = ImageService()
        self.image_storage = ImageStorage()

        # История генераций
        self.current_history_index = -1
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Стили
        self.setup_styles()
        
        # Основной контейнер
        self.main_frame = ttk.Frame(self.root, padding="20", style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        self.title_label = ttk.Label(self.main_frame, 
                                   text="Генератор Изображений",
                                   font=('Helvetica', 24, 'bold'))
        self.title_label.pack(pady=(0, 30))

        # Контент
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Область изображения
        self.setup_image_area()
        
        # Правая панель
        self.setup_right_panel()

        # Нижняя панель
        self.setup_bottom_panel()

    def setup_styles(self):
        """Настройка стилей"""
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TFrame', background=UI_CONFIG['bg_color'])
        self.style.configure('TButton', padding=10, font=('Helvetica', 12))
        self.style.configure('TLabel', font=('Helvetica', 14),
                           background=UI_CONFIG['bg_color'],
                           foreground=UI_CONFIG['text_color'])

    def setup_image_area(self):
        """Настройка области изображения"""
        self.image_frame = ttk.Frame(self.content_frame)
        self.image_frame.pack(side=tk.LEFT, padx=20)

        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack()

        self.loading_placeholder = ttk.Label(self.image_frame,
                                           text="Загрузка...",
                                           font=('Helvetica', 16))

    def setup_right_panel(self):
        """Настройка правой панели"""
        self.right_frame = ttk.Frame(self.content_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)

        # Текстовое поле описания
        self.setup_text_area()
        
        # Кнопки
        self.setup_buttons()

    def setup_text_area(self):
        """Настройка текстового поля"""
        # Текстовое поле описания
        self.description_text = tk.Text(self.right_frame,
                                      height=8,
                                      width=40,
                                      wrap=tk.WORD,
                                      bg="#2E2E2E",
                                      fg="white",
                                      font=('Helvetica', 12),
                                      insertbackground="white",
                                      selectbackground="#4a4a4a",
                                      selectforeground="white",
                                      relief=tk.SUNKEN,
                                      padx=10,
                                      pady=10)
        self.description_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Скроллбар
        scrollbar = tk.Scrollbar(self.right_frame, command=self.description_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.description_text.config(yscrollcommand=scrollbar.set)

    def setup_buttons(self):
        """Настройка кнопок"""
        self.buttons_frame = ttk.Frame(self.right_frame)
        self.buttons_frame.pack(fill=tk.X)

        # Кнопка генерации
        self.generate_button = ttk.Button(self.buttons_frame,
                                        text="✨ Создать изображение",
                                        command=self.start_generation_thread)
        self.generate_button.pack(fill=tk.X, pady=5)

        # Кнопки навигации
        self.nav_frame = ttk.Frame(self.buttons_frame)
        self.nav_frame.pack(fill=tk.X, pady=5)

        self.prev_button = ttk.Button(self.nav_frame,
                                    text="⬅️ Предыдущее",
                                    command=self.show_previous)
        self.prev_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.next_button = ttk.Button(self.nav_frame,
                                    text="Следующее ➡️",
                                    command=self.show_next)
        self.next_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Кнопка истории
        self.history_button = ttk.Button(self.buttons_frame,
                                       text="📜 История",
                                       command=self.show_history)
        self.history_button.pack(fill=tk.X, pady=5)

    def setup_bottom_panel(self):
        """Настройка нижней панели"""
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill=tk.X, pady=(20, 0))

        self.status_label = ttk.Label(self.bottom_frame,
                                    text="",
                                    font=('Helvetica', 10))
        self.status_label.pack(side=tk.LEFT)

    def start_generation_thread(self):
        """Запуск генерации в отдельном потоке"""
        self.generate_button.config(state='disabled')
        self.loading_placeholder.pack()
        self.status_label.config(text="Генерация изображения...")
        
        thread = threading.Thread(target=self.generate_new)
        thread.daemon = True
        thread.start()

    def generate_new(self):
        """Генерация нового изображения"""
        description = self.description_text.get(1.0, tk.END).strip()
        
        # Генерация описания если пользователь не ввел его
        if not description:
            description = self.image_service.generate_description("Случайная сцена")
            self.root.after(0, lambda: self.description_text.insert(1.0, description))

        # Генерация изображения
        image_url = self.image_service.generate_image(description)
        
        if image_url:
            # Сохранение изображения
            image_path = self.image_storage.save_image(image_url, description)
            if image_path:
                image = Image.open(image_path)
                image = image.resize((500, 500), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                def update_ui():
                    self.current_history_index = len(self.image_storage.get_history()) - 1
                    self.image_label.configure(image=photo)
                    self.image_label.image = photo
                    self.loading_placeholder.pack_forget()
                    self.generate_button.config(state='normal')
                    self.status_label.config(text="Готово!")
                    self.update_navigation_buttons()
                
                self.root.after(0, update_ui)
        else:
            self.root.after(0, lambda: self.status_label.config(
                text="Ошибка при генерации изображения"))
            self.root.after(0, lambda: self.generate_button.config(state='normal'))
            self.root.after(0, self.loading_placeholder.pack_forget)

    def show_previous(self):
        """Показать предыдущее изображение"""
        if self.current_history_index > 0:
            self.current_history_index -= 1
            self.show_history_item(self.current_history_index)

    def show_next(self):
        """Показать следующее изображение"""
        if self.current_history_index < len(self.image_storage.get_history()) - 1:
            self.current_history_index += 1
            self.show_history_item(self.current_history_index)

    def show_history_item(self, index):
        """Показать элемент истории по индексу"""
        history = self.image_storage.get_history()
        if 0 <= index < len(history):
            item = history[index]
            image = self.image_storage.load_image(item['image_path'])
            if image:
                image = image.resize((500, 500), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_label.configure(image=photo)
                self.image_label.image = photo
                self.description_text.delete(1.0, tk.END)
                self.description_text.insert(1.0, item['description'])
                self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Обновление состояния кнопок навигации"""
        history = self.image_storage.get_history()
        self.prev_button.config(state='normal' if self.current_history_index > 0 else 'disabled')
        self.next_button.config(
            state='normal' if self.current_history_index < len(history) - 1 else 'disabled')

    def show_history(self):
        """Показать окно истории"""
        history_window = tk.Toplevel(self.root)
        history_window.title("История генераций")
        history_window.geometry("600x400")
        history_window.configure(bg=UI_CONFIG['bg_color'])

        history_list = tk.Listbox(history_window,
                                 font=('Helvetica', 12),
                                 bg="#2E2E2E",
                                 fg="white")
        history_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for i, item in enumerate(self.image_storage.get_history()):
            history_list.insert(tk.END,
                              f"{i+1}. {item['timestamp']} - {item['description'][:50]}...")

        def on_select(event):
            if history_list.curselection():
                index = history_list.curselection()[0]
                self.current_history_index = index
                self.show_history_item(index)
                history_window.destroy()

        history_list.bind('<<ListboxSelect>>', on_select)

    def load_history(self):
        """Загрузка истории при старте"""
        history = self.image_storage.get_history()
        if history:
            self.current_history_index = len(history) - 1
            self.show_history_item(self.current_history_index) 