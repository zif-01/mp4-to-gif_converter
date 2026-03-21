import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import tkinterdnd2 as tkdnd  # Для drag & drop
from pathlib import Path
import threading
import queue
import time
import os
import sys

# Импорт нашего конвертера
from discord_gif_converter import DiscordGIFConverter

class DiscordGIFConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord GIF Converter")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Настройка иконки
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Переменные
        self.input_files = []
        self.output_folder = tk.StringVar(value=os.getcwd())
        self.fps = tk.IntVar(value=10)
        self.optimize_level = tk.IntVar(value=2)
        self.trim_start = tk.StringVar(value="0:00")
        self.trim_end = tk.StringVar()
        
        # Очередь для сообщений из фоновых потоков
        self.message_queue = queue.Queue()
        
        # Статус конвертации
        self.converting = False
        self.converter = None
        
        # Стили
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Запуск обработки очереди сообщений
        self.process_queue()
        
        # Настройка drag & drop
        self.setup_drag_drop()
    
    def setup_styles(self):
        """Настройка стилей для интерфейса"""
        style = ttk.Style()
        
        # Современная тема
        style.theme_use('clam')
        
        # Цвета - улучшенная гармоничная палитра
        self.bg_color = "#1e1e1e"        # Более темный фон
        self.fg_color = "#e0e0e0"        # Светлый текст
        self.text_muted = "#a0a0a0"      # Приглушенный текст
        self.accent_color = "#5e8cff"    # Современный синий акцент
        self.success_color = "#4caf50"   # Современный зеленый
        self.error_color = "#f44336"     # Современный красный
        self.warning_color = "#ff9800"   # Современный оранжевый
        self.border_color = "#333333"    # Цвет границ
        
        # Настройка цветов
        self.root.configure(bg=self.bg_color)

        # Стили для виджетов
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        style.configure("TButton", padding=6)
        style.configure("Accent.TButton", background=self.accent_color, foreground="white")
        style.configure("Success.TButton", background=self.success_color, foreground="white")
        style.configure("Warning.TButton", background=self.warning_color, foreground="white")

        # Стиль для прогресс-бара
        style.configure("Custom.Horizontal.TProgressbar",
                       background=self.accent_color,
                       troughcolor=self.border_color)

        # Стиль для фреймов
        style.configure("TLabelframe", background=self.bg_color, foreground=self.fg_color)
        style.configure("TLabelframe.Label", background=self.bg_color, foreground=self.fg_color)
    
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame,
                              text="🎮 Discord GIF Converter",
                              font=("Segoe UI", 24, "bold"),
                              bg=self.bg_color,
                              fg=self.accent_color)
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(header_frame,
                                 text="Конвертируйте MP4 в GIF для Discord",
                                 font=("Segoe UI", 10),
                                 bg=self.bg_color,
                                 fg="#aaaaaa")
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0), pady=5)
        
        # Основная область с двумя колонками
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая колонка - файлы
        left_frame = ttk.LabelFrame(content_frame, text="📁 Файлы", padding="15")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Правая колонка - настройки
        right_frame = ttk.LabelFrame(content_frame, text="⚙️ Настройки", padding="15")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Левая колонка: управление файлами
        self.create_file_management_widgets(left_frame)
        
        # Правая колонка: настройки
        self.create_settings_widgets(right_frame)
        
        # Нижняя панель: прогресс и кнопки
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.create_bottom_widgets(bottom_frame)
        
        # Область логов
        self.create_log_widgets(main_frame)
    
    def create_file_management_widgets(self, parent):
        """Создание виджетов для управления файлами"""
        # Кнопки добавления файлов
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame,
                  text="📁 Добавить файлы",
                  command=self.add_files,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(btn_frame,
                  text="📂 Добавить папку",
                  command=self.add_folder).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame,
                  text="🗑️ Очистить список",
                  command=self.clear_files,
                  style="Warning.TButton").pack(side=tk.LEFT, padx=(5, 0))
        
        # Drag & drop зона
        drop_frame = tk.Frame(parent, bg="#404040", relief=tk.RAISED, bd=1)
        drop_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        drop_label = tk.Label(drop_frame,
                             text="📤 Перетащите файлы сюда\nили нажмите кнопки выше",
                             font=("Segoe UI", 12),
                             bg="#404040",
                             fg="#aaaaaa",
                             pady=50)
        drop_label.pack(expand=True)
        
        # Список файлов
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Заголовки списка
        header_frame = ttk.Frame(list_frame)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame,
                text="Файл",
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Прокручиваемый список
        canvas = tk.Canvas(list_frame, bg="#404040", highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.file_list_frame = ttk.Frame(canvas)
        
        self.file_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.file_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_settings_widgets(self, parent):
        """Создание виджетов настроек"""
        # Настройки конвертации
        settings_grid = ttk.Frame(parent)
        settings_grid.pack(fill=tk.BOTH, expand=True)
        
        # Уровень оптимизации
        row = 0
        ttk.Label(settings_grid,
                 text="Уровень оптимизации:").grid(row=row, column=0, sticky=tk.W, pady=10)
        
        optimize_frame = ttk.Frame(settings_grid)
        optimize_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        
        levels = [
            ("Макс. качество", 0),
            ("Сбалансировано", 1),
            ("Discord (реком.)", 2)
        ]
        
        for text, value in levels:
            rb = tk.Radiobutton(optimize_frame,
                               text=text,
                               variable=self.optimize_level,
                               value=value,
                               bg=self.bg_color,
                               fg=self.fg_color,
                               selectcolor=self.accent_color,
                               activebackground=self.bg_color,
                               activeforeground=self.fg_color)
            rb.pack(anchor=tk.W)
        
        # Разрешение (автоматически определяется)
        row += 1
        ttk.Label(settings_grid,
                 text="Ширина GIF:").grid(row=row, column=0, sticky=tk.W, pady=10)

        width_info_frame = ttk.Frame(settings_grid)
        width_info_frame.grid(row=row, column=1, sticky=tk.W, pady=10)

        width_info_label = tk.Label(width_info_frame,
                                   text="Автоматически определяется по входному файлу",
                                   bg=self.bg_color,
                                   fg=self.text_muted,
                                   font=("Segoe UI", 9))
        width_info_label.pack(side=tk.LEFT)
        
        # FPS
        row += 1
        ttk.Label(settings_grid,
                 text="Кадров в секунду:").grid(row=row, column=0, sticky=tk.W, pady=10)
        
        fps_frame = ttk.Frame(settings_grid)
        fps_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        
        fps_slider = tk.Scale(fps_frame,
                             from_=5,
                             to=30,
                             variable=self.fps,
                             orient=tk.HORIZONTAL,
                             length=200,
                             bg=self.bg_color,
                             fg=self.fg_color,
                             troughcolor="#404040",
                             highlightthickness=0)
        fps_slider.pack(side=tk.LEFT)
        
        fps_label = tk.Label(fps_frame,
                            textvariable=self.fps,
                            bg=self.bg_color,
                            fg=self.fg_color,
                            width=3)
        fps_label.pack(side=tk.LEFT, padx=5)
        tk.Label(fps_frame,
                text="FPS",
                bg=self.bg_color,
                fg=self.fg_color).pack(side=tk.LEFT)
        
        # Обрезка по времени
        row += 1
        ttk.Label(settings_grid,
                 text="Обрезка видео:").grid(row=row, column=0, sticky=tk.W, pady=10)
        
        trim_frame = ttk.Frame(settings_grid)
        trim_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        
        # Начало
        ttk.Label(trim_frame,
                 text="Начало:").pack(side=tk.LEFT)
        ttk.Entry(trim_frame,
                 textvariable=self.trim_start,
                 width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(trim_frame,
                 text="Конец:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Entry(trim_frame,
                 textvariable=self.trim_end,
                 width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(trim_frame,
                 text="(формат: MM:SS или секунды)",
                 font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=10)
        
        # Папка сохранения
        row += 1
        ttk.Label(settings_grid,
                 text="Папка сохранения:").grid(row=row, column=0, sticky=tk.W, pady=10)
        
        save_frame = ttk.Frame(settings_grid)
        save_frame.grid(row=row, column=1, sticky=tk.W + tk.E, pady=10)
        
        ttk.Entry(save_frame,
                 textvariable=self.output_folder,
                 width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(save_frame,
                  text="📂",
                  command=self.browse_output_folder,
                  width=3).pack(side=tk.RIGHT)
        
        # Информация о Discord
        info_frame = ttk.LabelFrame(parent, text="ℹ️ Ограничения Discord", padding="10")
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        info_text = """
        • Максимальный размер файла: 10 MB
        • Максимальная длительность: 10 секунд
        • Рекомендуемая ширина: 400-480px
        • Рекомендуемый FPS: 8-10
        
        Конвертер автоматически оптимизирует GIF
        под эти ограничения.
        """
        
        info_label = tk.Label(info_frame,
                             text=info_text,
                             justify=tk.LEFT,
                             bg="#404040",
                             fg="#aaaaaa",
                             padx=10,
                             pady=10)
        info_label.pack(fill=tk.X)
    
    def create_bottom_widgets(self, parent):
        """Создание нижней панели с кнопками и прогрессом"""
        # Прогресс-бар
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame,
                                           variable=self.progress_var,
                                           maximum=100,
                                           style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, expand=True)
        
        # Статус
        self.status_label = tk.Label(progress_frame,
                                    text="Готов к работе",
                                    bg=self.bg_color,
                                    fg=self.fg_color)
        self.status_label.pack(pady=(5, 0))
        
        # Кнопки
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        # Кнопка предпросмотра (если выбран 1 файл)
        self.preview_btn = ttk.Button(button_frame,
                                     text="👁️ Предпросмотр",
                                     command=self.preview_gif,
                                     state=tk.DISABLED)
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Кнопка конвертации
        self.convert_btn = ttk.Button(button_frame,
                                     text="🚀 Начать конвертацию",
                                     command=self.start_conversion,
                                     style="Success.TButton")
        self.convert_btn.pack(side=tk.LEFT, padx=10)
        
        # Кнопка остановки
        self.stop_btn = ttk.Button(button_frame,
                                  text="⏹️ Остановить",
                                  command=self.stop_conversion,
                                  style="Warning.TButton",
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Кнопка открытия папки
        ttk.Button(button_frame,
                  text="📂 Открыть папку",
                  command=self.open_output_folder).pack(side=tk.RIGHT)
    
    def create_log_widgets(self, parent):
        """Создание области логов"""
        log_frame = ttk.LabelFrame(parent, text="📝 Лог конвертации", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                 height=8,
                                                 bg="#1e1e1e",
                                                 fg="#ffffff",
                                                 insertbackground="white",
                                                 font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки управления логом
        log_buttons = ttk.Frame(log_frame)
        log_buttons.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(log_buttons,
                  text="Очистить лог",
                  command=self.clear_log).pack(side=tk.LEFT)
        
        ttk.Button(log_buttons,
                  text="Копировать лог",
                  command=self.copy_log).pack(side=tk.LEFT, padx=5)
    
    def setup_drag_drop(self):
        """Настройка drag & drop функциональности"""
        try:
            self.root.drop_target_register(tkdnd.DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.handle_drop)
        except:
            self.log_message("⚠️ Drag & drop не поддерживается в этой системе")
    
    def handle_drop(self, event):
        """Обработка перетаскивания файлов"""
        files = event.data.strip('{}').split('} {')
        mp4_files = [f for f in files if f.lower().endswith('.mp4')]
        
        if mp4_files:
            self.add_files_from_list(mp4_files)
        else:
            messagebox.showwarning("Неверные файлы", "Пожалуйста, перетащите MP4 файлы")
    
    def add_files(self):
        """Добавление файлов через диалог"""
        files = filedialog.askopenfilenames(
            title="Выберите MP4 файлы",
            filetypes=[
                ("MP4 файлы", "*.mp4"),
                ("Видео файлы", "*.mp4;*.mov;*.avi"),
                ("Все файлы", "*.*")
            ]
        )
        
        if files:
            self.add_files_from_list(files)
    
    def add_folder(self):
        """Добавление всех MP4 файлов из папки"""
        folder = filedialog.askdirectory(title="Выберите папку с MP4 файлами")
        
        if folder:
            mp4_files = list(Path(folder).glob("**/*.mp4"))
            if mp4_files:
                self.add_files_from_list([str(f) for f in mp4_files])
            else:
                messagebox.showinfo("Файлы не найдены", "В выбранной папке нет MP4 файлов")
    
    def add_files_from_list(self, file_list):
        """Добавление файлов из списка"""
        for file_path in file_list:
            if file_path not in self.input_files:
                self.input_files.append(file_path)
                self.add_file_to_list(file_path)
        
        self.update_file_count()
        self.update_preview_button()
    
    def add_file_to_list(self, file_path):
        """Добавление файла в список интерфейса"""
        file_frame = ttk.Frame(self.file_list_frame)
        file_frame.pack(fill=tk.X, pady=2)
        
        # Иконка и имя файла
        file_label = tk.Label(file_frame,
                             text=f"🎬 {Path(file_path).name}",
                             bg="#404040",
                             fg=self.fg_color,
                             anchor=tk.W)
        file_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Размер файла
        size_mb = os.path.getsize(file_path) / 1024 / 1024
        size_label = tk.Label(file_frame,
                             text=f"{size_mb:.1f} MB",
                             bg="#404040",
                             fg="#aaaaaa")
        size_label.pack(side=tk.RIGHT, padx=5)
        
        # Кнопка удаления
        remove_btn = tk.Button(file_frame,
                              text="×",
                              command=lambda f=file_path, fr=file_frame: self.remove_file(f, fr),
                              bg="#f04747",
                              fg="white",
                              width=2,
                              relief=tk.FLAT)
        remove_btn.pack(side=tk.RIGHT)
    
    def remove_file(self, file_path, frame):
        """Удаление файла из списка"""
        if file_path in self.input_files:
            self.input_files.remove(file_path)
            frame.destroy()
            self.update_file_count()
            self.update_preview_button()
    
    def clear_files(self):
        """Очистка списка файлов"""
        if self.input_files:
            if messagebox.askyesno("Очистка", "Удалить все файлы из списка?"):
                self.input_files.clear()
                for widget in self.file_list_frame.winfo_children():
                    widget.destroy()
                self.update_file_count()
                self.update_preview_button()
    
    def update_file_count(self):
        """Обновление информации о количестве файлов"""
        count = len(self.input_files)
        self.status_label.config(text=f"Выбрано файлов: {count}")
    
    def update_preview_button(self):
        """Обновление состояния кнопки предпросмотра"""
        if len(self.input_files) == 1:
            self.preview_btn.config(state=tk.NORMAL)
        else:
            self.preview_btn.config(state=tk.DISABLED)
    
    def browse_output_folder(self):
        """Выбор папки сохранения"""
        folder = filedialog.askdirectory(title="Выберите папку для сохранения GIF")
        if folder:
            self.output_folder.set(folder)
    
    def parse_time(self, time_str):
        """Парсинг времени из строки (MM:SS или секунды)"""
        if not time_str:
            return None
        
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 2:
                    minutes, seconds = map(int, parts)
                    return minutes * 60 + seconds
                elif len(parts) == 3:
                    hours, minutes, seconds = map(int, parts)
                    return hours * 3600 + minutes * 60 + seconds
            else:
                return float(time_str)
        except:
            return None
    
    def start_conversion(self):
        """Запуск конвертации"""
        if not self.input_files:
            messagebox.showwarning("Нет файлов", "Добавьте хотя бы один MP4 файл")
            return
        
        if self.converting:
            messagebox.showinfo("Уже запущено", "Конвертация уже выполняется")
            return
        
        # Подтверждение
        if len(self.input_files) > 1:
            if not messagebox.askyesno("Подтверждение", 
                                      f"Начать конвертацию {len(self.input_files)} файлов?"):
                return
        
        # Настройка интерфейса
        self.converting = True
        self.convert_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        
        # Парсинг времени обрезки
        start_time = self.parse_time(self.trim_start.get())
        end_time = self.parse_time(self.trim_end.get())
        
        # Запуск в отдельном потоке
        thread = threading.Thread(
            target=self.convert_files_thread,
            args=(self.input_files, start_time, end_time),
            daemon=True
        )
        thread.start()
    
    def convert_files_thread(self, files, start_time, end_time):
        """Поток для конвертации файлов"""
        total_files = len(files)
        
        for i, file_path in enumerate(files, 1):
            if not self.converting:
                break
            
            # Обновление прогресса
            progress = (i - 1) / total_files * 100
            self.message_queue.put(("progress", progress))
            self.message_queue.put(("log", f"\n[{i}/{total_files}] Конвертация: {Path(file_path).name}"))
            
            try:
                # Создание конвертера
                self.converter = DiscordGIFConverter(
                    optimize_level=self.optimize_level.get()
                )
                
                # Генерация имени выходного файла
                output_name = f"{Path(file_path).stem}_discord.gif"
                output_path = Path(self.output_folder.get()) / output_name
                
                # Конвертация
                success, result = self.converter.convert_mp4_to_gif(
                    input_path=file_path,
                    output_path=str(output_path),
                    start_time=start_time,
                    end_time=end_time,
                    custom_fps=self.fps.get()
                    # custom_width автоматически определяется по входному файлу
                )
                
                if success:
                    self.message_queue.put(("log", f"✅ Успешно: {output_name}"))
                else:
                    self.message_queue.put(("log", f"❌ Ошибка: {result}"))
                
            except Exception as e:
                self.message_queue.put(("log", f"⚠️ Исключение: {str(e)}"))
            
            # Обновление прогресса
            final_progress = i / total_files * 100
            self.message_queue.put(("progress", final_progress))
        
        # Завершение
        self.message_queue.put(("complete", None))
    
    def stop_conversion(self):
        """Остановка конвертации"""
        if self.converting:
            self.converting = False
            self.message_queue.put(("log", "\n⏹️ Конвертация остановлена пользователем"))
            self.finish_conversion()
    
    def finish_conversion(self):
        """Завершение конвертации"""
        self.converting = False
        self.convert_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Конвертация завершена")
    
    def process_queue(self):
        """Обработка сообщений из очереди"""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                
                if msg_type == "progress":
                    self.progress_var.set(data)
                elif msg_type == "log":
                    self.log_message(data)
                elif msg_type == "complete":
                    self.finish_conversion()
                    self.log_message("\n" + "="*50)
                    self.log_message("🎉 Конвертация завершена!")
                    
                    if self.converting:  # Если не было остановки
                        messagebox.showinfo("Готово", "Конвертация успешно завершена!")
        
        except queue.Empty:
            pass
        
        finally:
            # Планируем следующую проверку
            self.root.after(100, self.process_queue)
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Очистка лога"""
        self.log_text.delete(1.0, tk.END)
    
    def copy_log(self):
        """Копирование лога в буфер обмена"""
        log_content = self.log_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(log_content)
        messagebox.showinfo("Скопировано", "Лог скопирован в буфер обмена")
    
    def preview_gif(self):
        """Предпросмотр GIF (если выбран 1 файл)"""
        if len(self.input_files) != 1:
            return
        
        # В реальном приложении здесь можно добавить окно предпросмотра
        # или открытие созданного GIF в системном просмотрщике
        messagebox.showinfo("Предпросмотр", 
                          "Предпросмотр будет доступен после конвертации.\n"
                          "Откройте созданный GIF в папке сохранения.")
    
    def open_output_folder(self):
        """Открытие папки сохранения"""
        folder = self.output_folder.get()
        if os.path.exists(folder):
            try:
                if sys.platform == "win32":
                    os.startfile(folder)
                elif sys.platform == "darwin":
                    os.system(f'open "{folder}"')
                else:
                    os.system(f'xdg-open "{folder}"')
            except:
                messagebox.showerror("Ошибка", "Не удалось открыть папку")
        else:
            messagebox.showwarning("Папка не найдена", "Указанная папка не существует")


def main():
    """Основная функция запуска GUI"""
    try:
        # Создание основного окна с поддержкой drag & drop
        root = tkdnd.TkinterDnD.Tk()
        
        # Настройка темы
        root.tk_setPalette(background='#2b2b2b', foreground='#ffffff')
        
        # Создание приложения
        app = DiscordGIFConverterGUI(root)
        
        # Центрирование окна
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Запуск основного цикла
        root.mainloop()
        
    except Exception as e:
        print(f"Ошибка запуска GUI: {e}")
        
        # Запуск в обычном режиме без drag & drop
        root = tk.Tk()
        app = DiscordGIFConverterGUI(root)
        root.mainloop()


if __name__ == "__main__":
    main()