import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
from ..services.image_service import ImageService
from ..utils.image_storage import ImageStorage
from ..utils.config import UI_CONFIG

class LoadingIndicator:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.withdraw()
        
        # Настройка окна загрузки
        self.window.configure(bg=UI_CONFIG['bg_color'])
        self.window.geometry("200x100")
        
        # Индикатор прогресса
        self.progress = ttk.Progressbar(
            self.window, 
            mode='indeterminate',
            length=180
        )
        self.progress.pack(pady=20)
        
        # Текст загрузки
        self.label = ttk.Label(
            self.window,
            text="Генерация изображения...",
            background=UI_CONFIG['bg_color'],
            foreground=UI_CONFIG['text_color']
        )
        self.label.pack(pady=5)
        
    def start(self, parent_window):
        # Центрируем относительно главного окна
        x = parent_window.winfo_x() + parent_window.winfo_width()//2 - 100
        y = parent_window.winfo_y() + parent_window.winfo_height()//2 - 50
        self.window.geometry(f"+{x}+{y}")
        
        self.window.deiconify()
        self.progress.start(10)
        
    def stop(self):
        self.progress.stop()
        self.window.withdraw()

class ImageGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title(UI_CONFIG['window_title'])
        self.root.geometry(UI_CONFIG['window_size'])
        self.root.configure(bg=UI_CONFIG['bg_color'])
        
        # Устанавливаем минимальные размеры окна
        self.root.minsize(UI_CONFIG['min_width'], UI_CONFIG['min_height'])
        
        # Настраиваем стили
        self.setup_styles()
        
        # Инициализация сервисов
        self.image_service = ImageService()
        self.image_storage = ImageStorage()
        self.loading_indicator = LoadingIndicator(self.root)

        # История генераций
        self.current_history_index = -1
        
        # Настраиваем UI
        self.setup_ui()
        
        # Ждем полной инициализации окна перед загрузкой истории
        self.root.after(500, self.delayed_load_history)

    def delayed_load_history(self):
        """Отложенная загрузка истории после инициализации окна"""
        history = self.image_storage.get_history()
        if history:
            self.current_history_index = len(history) - 1
            self.show_history_item(self.current_history_index)
        else:
            # Если истории нет, просто показываем заглушку
            self.no_image_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.update_navigation_buttons()

    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создаем главный контейнер с отступами
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Создаем канвас и скроллбар
        canvas = tk.Canvas(self.main_container, bg=UI_CONFIG['bg_color'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Конфигурируем скроллинг
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Размещаем элементы
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Добавляем скроллинг мышью
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Верхняя панель с заголовком
        self.setup_header()
        
        # Основной контент
        self.content_container = ttk.Frame(self.scrollable_frame)
        self.content_container.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Левая панель (изображение)
        self.setup_image_panel()
        
        # Правая панель (описание и кнопки)
        self.setup_right_panel()
        
        # Нижняя панель
        self.setup_bottom_panel()

    def setup_header(self):
        """Настройка заголовка"""
        header = ttk.Frame(self.main_container)
        header.pack(fill=tk.X, pady=(0, 20))
        
        self.title_label = ttk.Label(
            header,
            text="Генератор Изображений",
            font=('Helvetica', 24, 'bold'),
            style='Header.TLabel'
        )
        self.title_label.pack()

    def setup_image_panel(self):
        """Настройка панели изображения"""
        # Создаем фрейм для изображения
        self.image_frame = ttk.LabelFrame(
            self.content_container,
            text="Изображение",
            padding="10"
        )
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Метка для изображения
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(expand=True, fill=tk.BOTH)
        
        # Заглушка "Нет изображения"
        self.no_image_label = ttk.Label(
            self.image_frame,
            text="Нет изображения\nНажмите 'Создать изображение'",
            justify=tk.CENTER,
            font=('Helvetica', 12)
        )
        self.no_image_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Добавляем обработчик клика для увеличения
        self.image_label.bind('<Button-1>', self.show_enlarged_image)

    def show_enlarged_image(self, event=None):
        """Показать увеличенное изображение"""
        if hasattr(self, 'current_image'):
            top = tk.Toplevel(self.root)
            top.title("Увеличенное изображение")
            
            # Получаем размеры экрана
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Максимальные размеры окна (80% от экрана)
            max_width = int(screen_width * 0.8)
            max_height = int(screen_height * 0.8)
            
            # Изменяем размер изображения, сохраняя пропорции
            img_width, img_height = self.current_image.size
            ratio = min(max_width/img_width, max_height/img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            resized_image = self.current_image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )
            photo = ImageTk.PhotoImage(resized_image)
            
            label = ttk.Label(top, image=photo)
            label.image = photo
            label.pack()
            
            # Центрируем окно
            x = (screen_width - new_width) // 2
            y = (screen_height - new_height) // 2
            top.geometry(f"{new_width}x{new_height}+{x}+{y}")
            
            # Добавляем кнопку закрытия
            close_btn = ttk.Button(
                top,
                text="Закрыть",
                command=top.destroy
            )
            close_btn.pack(pady=10)

    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use('default')
        
        # Основные цвета
        style.configure('.',
            background=UI_CONFIG['bg_color'],
            foreground=UI_CONFIG['text_color'],
            fieldbackground=UI_CONFIG['secondary_bg'])
            
        # Фреймы
        style.configure('TFrame', background=UI_CONFIG['bg_color'])
        style.configure('TLabelframe', 
            background=UI_CONFIG['bg_color'],
            foreground=UI_CONFIG['text_color'])
        style.configure('TLabelframe.Label', 
            background=UI_CONFIG['bg_color'],
            foreground=UI_CONFIG['text_color'],
            font=('Helvetica', 12))
            
        # Кнопки
        style.configure('TButton',
            background=UI_CONFIG['button_bg'],
            foreground=UI_CONFIG['button_fg'],
            padding=10,
            font=('Helvetica', 12))
        style.map('TButton',
            background=[('active', UI_CONFIG['highlight_bg'])])
            
        # Метки
        style.configure('TLabel',
            background=UI_CONFIG['bg_color'],
            foreground=UI_CONFIG['text_color'],
            font=('Helvetica', 12))
            
        # Заголовок
        style.configure('Header.TLabel',
            background=UI_CONFIG['bg_color'],
            foreground=UI_CONFIG['text_color'],
            font=('Helvetica', 24, 'bold'))
            
        # Радиокнопки
        style.configure('TRadiobutton',
            background=UI_CONFIG['bg_color'],
            foreground=UI_CONFIG['text_color'],
            font=('Helvetica', 12))
            
        # Прогрессбар
        style.configure('TProgressbar',
            background=UI_CONFIG['accent_color'],
            troughcolor=UI_CONFIG['secondary_bg'])

    def setup_right_panel(self):
        """Настройка правой панели"""
        self.right_frame = ttk.Frame(self.content_container)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)

        # Фрейм для стилей
        self.styles_frame = ttk.LabelFrame(self.right_frame, text="Стиль изображения")
        self.styles_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Стандартные стили
        self.style_var = tk.StringVar(value="default")
        styles = [
            ("Обычный", "default"),
            ("Рик и Морти", "rick_and_morty"),
            ("Симпсоны", "simpsons"),
            ("Масляная живопись", "oil_painting"),
            ("Черно-белое", "black_and_white")
        ]
        
        for text, value in styles:
            ttk.Radiobutton(
                self.styles_frame,
                text=text,
                value=value,
                variable=self.style_var
            ).pack(anchor=tk.W, padx=10, pady=2)
            
        # Кастомный стиль
        ttk.Label(
            self.styles_frame,
            text="Кастомный стиль:",
            font=('Helvetica', 10)
        ).pack(anchor=tk.W, padx=10, pady=(10, 2))
        
        self.custom_style_text = tk.Text(
            self.styles_frame,
            height=3,
            wrap=tk.WORD,
            bg=UI_CONFIG['secondary_bg'],
            fg=UI_CONFIG['text_color'],
            insertbackground=UI_CONFIG['text_color'],
            font=('Helvetica', 10)
        )
        self.custom_style_text.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Загружаем сохраненный кастомный стиль
        current_style = self.image_service.style_prompts.get("custom")
        if current_style:
            self.custom_style_text.insert(1.0, current_style)
            
        # Кнопка сохранения стиля
        ttk.Button(
            self.styles_frame,
            text="💾 Сохранить стиль",
            command=self.save_custom_style
        ).pack(anchor=tk.W, padx=10, pady=5)

        # Фрейм для формата сохранения
        self.format_frame = ttk.LabelFrame(self.right_frame, text="Формат сохранения")
        self.format_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.format_var = tk.StringVar(value="png")
        ttk.Radiobutton(
            self.format_frame,
            text="PNG",
            value="png",
            variable=self.format_var
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            self.format_frame,
            text="JPEG",
            value="jpeg",
            variable=self.format_var
        ).pack(side=tk.LEFT, padx=10)

        # Текстовое поле описания
        self.description_frame = ttk.LabelFrame(self.right_frame, text="Описание изображения")
        self.description_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.description_text = tk.Text(
            self.description_frame,
            height=8,
            wrap=tk.WORD,
            bg="#2E2E2E",
            fg="white",
            font=('Helvetica', 12),
            insertbackground="white",
            selectbackground="#4a4a4a",
            selectforeground="white",
            relief=tk.SUNKEN,
            padx=10,
            pady=10
        )
        self.description_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Кнопки для работы с текстом
        self.text_buttons_frame = ttk.Frame(self.right_frame)
        self.text_buttons_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            self.text_buttons_frame,
            text="🎲 Сгенерировать описание",
            command=self.generate_description
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        ttk.Button(
            self.text_buttons_frame,
            text="🌍 Перевести",
            command=self.show_translation_dialog
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Кнопки управления
        self.control_buttons_frame = ttk.Frame(self.right_frame)
        self.control_buttons_frame.pack(fill=tk.X, pady=(0, 10))

        self.generate_button = ttk.Button(
            self.control_buttons_frame,
            text="✨ Создать изображение",
            command=self.start_generation_thread
        )
        self.generate_button.pack(fill=tk.X, pady=5)

        # Кнопки навигации
        self.nav_frame = ttk.Frame(self.control_buttons_frame)
        self.nav_frame.pack(fill=tk.X, pady=5)

        self.prev_button = ttk.Button(
            self.nav_frame,
            text="⬅️ Предыдущее",
            command=self.show_previous
        )
        self.prev_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.next_button = ttk.Button(
            self.nav_frame,
            text="Следующее ➡️",
            command=self.show_next
        )
        self.next_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Кнопка истории
        self.history_button = ttk.Button(
            self.control_buttons_frame,
            text="📜 История",
            command=self.show_history
        )
        self.history_button.pack(fill=tk.X, pady=5)

    def generate_description(self):
        """Улучшение текущего описания"""
        current_text = self.description_text.get(1.0, tk.END).strip()
        
        # Показываем индикатор загрузки
        self.loading_indicator.start(self.root)
        self.status_label.config(text="Улучшаем описание...")
        
        def process_description():
            improved_description = self.image_service.generate_description(current_text)
            
            def update_ui():
                self.description_text.delete(1.0, tk.END)
                self.description_text.insert(1.0, improved_description)
                self.loading_indicator.stop()
                self.status_label.config(text="Описание улучшено!")
                self.root.after(2000, lambda: self.status_label.config(text=""))
            
            self.root.after(0, update_ui)
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=process_description)
        thread.daemon = True
        thread.start()

    def show_translation_dialog(self):
        """Показать диалог выбора языка для перевода"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Выберите язык")
        dialog.geometry("200x250")
        dialog.transient(self.root)
        dialog.grab_set()

        languages = [
            ("English", "en"),
            ("Русский", "ru"),
            ("Español", "es"),
            ("Français", "fr"),
            ("Deutsch", "de"),
            ("日本語", "ja"),
            ("中文", "zh")
        ]

        def translate(lang_code):
            text = self.description_text.get(1.0, tk.END).strip()
            if text:
                translated = self.image_service.translate_text(text, lang_code)
                self.description_text.delete(1.0, tk.END)
                self.description_text.insert(1.0, translated)
            dialog.destroy()

        for lang_name, lang_code in languages:
            ttk.Button(
                dialog,
                text=lang_name,
                command=lambda code=lang_code: translate(code)
            ).pack(fill=tk.X, padx=10, pady=2)

        ttk.Button(
            dialog,
            text="Отмена",
            command=dialog.destroy
        ).pack(fill=tk.X, padx=10, pady=10)

    def setup_bottom_panel(self):
        """Настройка нижней панели"""
        self.bottom_frame = ttk.Frame(self.main_container)
        self.bottom_frame.pack(fill=tk.X, pady=(20, 0))

        self.status_label = ttk.Label(self.bottom_frame,
                                    text="",
                                    font=('Helvetica', 10))
        self.status_label.pack(side=tk.LEFT)

    def start_generation_thread(self):
        """Запуск генерации в отдельном потоке"""
        self.generate_button.config(state='disabled')
        self.loading_indicator.start(self.root)
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

        # Получаем выбранный стиль и формат
        style = self.style_var.get()
        format = self.format_var.get()

        # Генерация изображения
        image_url = self.image_service.generate_image(description, style)
        
        if image_url:
            # Сохранение изображения
            image_path = self.image_storage.save_image(image_url, description, format)
            if image_path:
                self.current_image = Image.open(image_path)  # Сохраняем оригинал для увеличения
                image = self.current_image.copy()
                
                # Подгоняем размер изображения под размер фрейма
                frame_width = self.image_frame.winfo_width() - 20  # Учитываем отступы
                frame_height = self.image_frame.winfo_height() - 20
                
                # Сохраняем пропорции
                img_width, img_height = image.size
                ratio = min(frame_width/img_width, frame_height/img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                def update_ui():
                    self.current_history_index = len(self.image_storage.get_history()) - 1
                    self.no_image_label.place_forget()  # Скрываем заглушку
                    self.image_label.configure(image=photo)
                    self.image_label.image = photo
                    self.loading_indicator.stop()
                    self.generate_button.config(state='normal')
                    self.status_label.config(text="Готово!")
                    self.update_navigation_buttons()
                
                self.root.after(0, update_ui)
        else:
            def show_error():
                self.status_label.config(text="Ошибка при генерации изображения")
                self.generate_button.config(state='normal')
                self.loading_indicator.stop()
                messagebox.showerror("Ошибка", "Не удалось сгенерировать изображение")
            
            self.root.after(0, show_error)

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
        if not history or not (0 <= index < len(history)):
            self.no_image_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.update_navigation_buttons()
            return
            
        item = history[index]
        image = self.image_storage.load_image(item['image_path'])
        if not image:
            messagebox.showerror("Ошибка", "Не удалось загрузить изображение")
            return
            
        try:
            self.current_image = image  # Сохраняем оригинал для увеличения
            
            # Получаем размеры фрейма
            self.image_frame.update_idletasks()
            frame_width = self.image_frame.winfo_width() - 20
            frame_height = self.image_frame.winfo_height() - 20
            
            if frame_width <= 1 or frame_height <= 1:
                frame_width = 500
                frame_height = 500
            
            # Сохраняем пропорции
            img_width, img_height = image.size
            ratio = min(frame_width/img_width, frame_height/img_height)
            new_width = max(int(img_width * ratio), 1)
            new_height = max(int(img_height * ratio), 1)
            
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)
            
            self.no_image_label.place_forget()
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # Сохраняем ссылку!
            
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(1.0, item['description'])
            
            self.update_navigation_buttons()
            
        except Exception as e:
            print(f"Ошибка при отображении изображения: {e}")
            messagebox.showerror("Ошибка", "Не удалось отобразить изображение")

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
            # Даем окну время на инициализацию
            self.root.after(100, lambda: self.show_history_item(self.current_history_index)) 

    def save_custom_style(self):
        """Сохранение кастомного стиля"""
        style_prompt = self.custom_style_text.get(1.0, tk.END).strip()
        if style_prompt:
            if self.image_service.save_custom_style(style_prompt):
                messagebox.showinfo("Успех", "Кастомный стиль сохранен")
                self.style_var.set("custom")  # Автоматически выбираем кастомный стиль
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить стиль")
        else:
            messagebox.showwarning("Внимание", "Введите описание стиля")