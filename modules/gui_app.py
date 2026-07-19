import customtkinter as ctk
import os
import re
import shutil
import sys
import threading
from typing import List, Dict, Any
from tkinter import messagebox, filedialog, Label, PhotoImage


def resource_path(relative_path):
    """Путь к ресурсу (например, иконке), корректно работающий как при
    запуске из исходников, так и из собранного PyInstaller --onefile exe."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    elif getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


ICON_PATH = resource_path("icon.ico")


def apply_window_icon(window):
    """Пытается назначить окну иконку icon.ico. Если файла нет (например,
    иконку ещё не добавили в проект) - тихо ничего не делает."""
    try:
        if os.path.exists(ICON_PATH):
            window.iconbitmap(ICON_PATH)
    except Exception:
        pass

LOCALIZATION = {
    "ru": {
        "title": "Soundpad & Telegram Sync Tool",
        "wizard_title": "Первоначальная настройка Soundpad Sync",
        "step": "Шаг",
        "of": "из",
        "next": "Далее ➡️",
        "back": "⬅️ Назад",
        "finish": "Завершить 🎉",
        "success": "Успешно",
        "warning": "Предупреждение",
        "error": "Ошибка",
        "cancel": "Отмена",
        "save": "Сохранить",
        
        # Step 1: Language selection
        "step_lang_title": "Шаг 1 из 3: Выбор языка / Select Language",
        "step_lang_desc": "Пожалуйста, выберите предпочитаемый язык для интерфейса программы:\nPlease choose your preferred language for the application interface:",
        
        # Step 2: Token
        "step_tok_title": "Шаг 2 из 3: Создание и настройка Telegram-бота",
        "step_tok_desc": (
            "Для работы программы вам нужен собственный Telegram-бот,\n"
            "который будет принимать звуковые файлы из TikTok и YouTube.\n\n"
            "Как его создать (Инструкция):\n"
            "1. Откройте Telegram и в поиске найдите бота @BotFather\n"
            "2. Отправьте ему команду /newbot\n"
            "3. Введите любое имя для бота (например, Мой Саундпад Бот)\n"
            "4. Введите юзернейм бота, оканчивающийся на 'bot' (например, my_soundpad_bot)\n"
            "5. Скопируйте полученный API токен (длинную строку вида 12345:AAAbbB...)\n"
            "6. Вставьте полученный токен в поле ниже:"
        ),
        "token_placeholder": "Вставьте API-токен вашего бота сюда...",
        "paste": "📋 Вставить",
        "token_empty_warn": "Пожалуйста, укажите API-токен Telegram бота.",
        "token_invalid_warn": "Некорректный формат токена. Токен должен содержать двоеточие (например, 12345:AAAbbb...)",
        
        # Step 3: SPL
        "step_spl_title": "Шаг 3 из 3: Указание плейлиста Soundpad (.spl)",
        "step_spl_desc": (
            "Программе необходимо знать, в какой файл плейлиста (.spl) Soundpad\n"
            "добавлять новые звуки.\n\n"
            "💡 Решение для ЛЮБЫХ версий (включая Steam и обычную):\n"
            "1. Откройте Soundpad на вашем компьютере.\n"
            "2. Нажмите меню: Файл ➡️ Сохранить список звуков как... (Save soundlist as...)\n"
            "3. Сохраните плейлист в любое удобное место (например, в 'Документы')\n"
            "   под именем 'soundlist.spl'.\n"
            "4. Укажите этот файл, нажав кнопку «Выбрать файл» ниже!\n"
            "   Либо нажмите «Создать новый», если хотите начать с чистого листа.\n\n"
            "Стандартные места установки:\n"
            "• Обычная версия: C:\\Program Files\\Soundpad\\\n"
            "• Steam-версия: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Soundpad\\\n"
            "• Пользовательские файлы: Documents\\Soundpad\\soundlists\\"
        ),
        "choose_spl_btn": "📁 Выбрать файл .spl",
        "create_spl_btn": "🆕 Создать новый .spl",
        "selected_file": "Выбранный файл:\n{}",
        "created_file_info": "Создан и выбран файл:\n{}",
        "created_file_success": "Новый файл плейлиста успешно создан:\n{}",
        "create_file_error": "Не удалось создать файл: {}",
        "spl_file_empty_warn": "Пожалуйста, выберите или создайте файл плейлиста .spl",
        "wizard_success_info": "Первоначальная настройка завершена! Теперь вы можете запустить бота и принимать треки.",
        
        # Token Dialog
        "token_dialog_title": "Настройка Telegram токена",
        "token_dialog_label": "Введите API Token вашего Telegram бота:\n(Получите его в Telegram у @BotFather)",
        "token_dialog_hint": "Подсказка: Если Ctrl+V не работает, используйте кнопку «Вставить»\nили смените раскладку клавиатуры на английскую.",
        "token_dialog_empty_warn": "Токен не может быть пустым.",
        "token_dialog_success": "API-токен бота успешно сохранен!",
        
        # Main GUI
        "bot_status_off": "● Бот выключен",
        "bot_status_on": "● Бот активен",
        "start_bot": "Запустить бота",
        "stop_bot": "Остановить бота",
        "configure_token_btn": "Настроить токен бота",
        "sync_settings_label": "Настройки синхронизации",
        "codec_label": "Кодек автоконвертации:",
        "autosync_label": "Авто-синхронизация",
        "interval_label": "Интервал проверки:",
        "paths_label_sec": "Настройки путей",
        "select_spl_btn_sec": "Указать файл .spl",
        "language_setting_label": "Язык / Language:",
        "header_queue_title": "Очередь новых треков для утверждения",
        "refresh_btn_text": "🔄 Обновить",
        "queue_scroll_title": "Новые треки из Telegram",
        "no_tracks_text": "Очередь пуста. Новых треков нет.",
        "track_name_label": "Название трека:",
        "category_label": "Категория:",
        "play_btn_play": "▶️ Слушать",
        "play_btn_stop": "⏹️ Стоп",
        "approve_btn_text": "Утвердить",
        "reject_btn_text": "Удалить",
        "file_not_found_error": "Файл не найден на жестком диске!",
        "track_file_not_found_error": "Файл трека не найден на вашем жестком диске!",
        "spl_modify_error": "Не удалось модифицировать плейлист Soundpad по API. Проверьте подключение.",
        "move_file_error": "Не удалось переместить файл или обновить список: {}",
        "start_bot_error_title": "Ошибка старта",
        "start_bot_error_desc": "Не удалось запустить Telegram бота. Проверьте правильность токена и интернет-соединение."
    },
    "en": {
        "title": "Soundpad & Telegram Sync Tool",
        "wizard_title": "Initial Setup of Soundpad Sync",
        "step": "Step",
        "of": "of",
        "next": "Next ➡️",
        "back": "⬅️ Back",
        "finish": "Finish 🎉",
        "success": "Success",
        "warning": "Warning",
        "error": "Error",
        "cancel": "Cancel",
        "save": "Save",
        
        # Step 1: Language selection
        "step_lang_title": "Step 1 of 3: Select Language",
        "step_lang_desc": "Please choose your preferred language for the application interface:\nПожалуйста, выберите предпочитаемый язык для интерфейса программы:",
        
        # Step 2: Token
        "step_tok_title": "Step 2 of 3: Create and Configure Telegram Bot",
        "step_tok_desc": (
            "To use this app, you need your own Telegram Bot,\n"
            "which will receive audio files from TikTok and YouTube.\n\n"
            "How to create it (Instructions):\n"
            "1. Open Telegram and search for the bot @BotFather\n"
            "2. Send the command /newbot\n"
            "3. Enter any name for your bot (e.g., My Soundpad Bot)\n"
            "4. Enter a username for your bot ending in 'bot' (e.g., my_soundpad_bot)\n"
            "5. Copy the received API token (long string like 12345:AAAbbB...)\n"
            "6. Paste the token in the field below:"
        ),
        "token_placeholder": "Paste your bot API token here...",
        "paste": "📋 Paste",
        "token_empty_warn": "Please provide your Telegram Bot API token.",
        "token_invalid_warn": "Invalid token format. The token must contain a colon (e.g., 12345:AAAbbb...)",
        
        # Step 3: SPL
        "step_spl_title": "Step 3 of 3: Select Soundpad Playlist (.spl)",
        "step_spl_desc": (
            "The program needs to know which Soundpad playlist (.spl) file\n"
            "to add new sounds to.\n\n"
            "💡 Solution for ANY version (including Steam and normal ones):\n"
            "1. Open Soundpad on your computer.\n"
            "2. Click menu: File ➡️ Save soundlist as...\n"
            "3. Save the playlist to any convenient place (e.g., 'Documents')\n"
            "   with the name 'soundlist.spl'.\n"
            "4. Specify this file by clicking the \"Select file\" button below!\n"
            "   Or click \"Create new\" if you want to start from scratch.\n\n"
            "Default installation locations:\n"
            "• Standard version: C:\\Program Files\\Soundpad\\\n"
            "• Steam version: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Soundpad\\\n"
            "• User files: Documents\\Soundpad\\soundlists\\"
        ),
        "choose_spl_btn": "📁 Select .spl file",
        "create_spl_btn": "🆕 Create new .spl",
        "selected_file": "Selected file:\n{}",
        "created_file_info": "Created and selected file:\n{}",
        "created_file_success": "New playlist file successfully created:\n{}",
        "create_file_error": "Could not create file: {}",
        "spl_file_empty_warn": "Please select or create a .spl playlist file",
        "wizard_success_info": "Initial setup completed! You can now start the bot and receive tracks.",
        
        # Token Dialog
        "token_dialog_title": "Telegram Token Setup",
        "token_dialog_label": "Enter Telegram Bot API Token:\n(Get it from Telegram @BotFather)",
        "token_dialog_hint": "Hint: If Ctrl+V does not work, use the 'Paste' button\nor switch keyboard layout to English.",
        "token_dialog_empty_warn": "Token cannot be empty.",
        "token_dialog_success": "Bot API token successfully saved!",
        
        # Main GUI
        "bot_status_off": "● Bot is offline",
        "bot_status_on": "● Bot is active",
        "start_bot": "Start Bot",
        "stop_bot": "Stop Bot",
        "configure_token_btn": "Configure Bot Token",
        "sync_settings_label": "Sync Settings",
        "codec_label": "Auto-convert Codec:",
        "autosync_label": "Auto-sync",
        "interval_label": "Check Interval:",
        "paths_label_sec": "Path Settings",
        "select_spl_btn_sec": "Select .spl file",
        "language_setting_label": "Language / Язык:",
        "header_queue_title": "New Tracks Queue for Approval",
        "refresh_btn_text": "🔄 Refresh",
        "queue_scroll_title": "New Tracks from Telegram",
        "no_tracks_text": "Queue is empty. No new tracks.",
        "track_name_label": "Track Name:",
        "category_label": "Category:",
        "play_btn_play": "▶️ Play",
        "play_btn_stop": "⏹️ Stop",
        "approve_btn_text": "Approve",
        "reject_btn_text": "Delete",
        "file_not_found_error": "File not found on hard drive!",
        "track_file_not_found_error": "Track file not found on your hard drive!",
        "spl_modify_error": "Could not add sound to Soundpad via API. Check connection.",
        "move_file_error": "Failed to move file or update playlist: {}",
        "start_bot_error_title": "Start Error",
        "start_bot_error_desc": "Could not start Telegram bot. Check your token and internet connection."
    }
}

class OnboardingWizard(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        apply_window_icon(self)
        self.parent = parent
        
        # Попытка прочесть текущий язык
        self.language = self.parent.db.get_setting("language", "ru")
        self.title(self.t("wizard_title"))
        self.geometry("620x460")
        self.resizable(False, False)
        
        # Модальный режим
        self.transient(parent)
        self.grab_set()
        
        # Установка иконки
        self.set_window_icon()
        
        self.current_step = 1
        self.bot_token = ""
        
        # Контейнер для шагов
        self.step_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.step_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Нижняя панель навигации
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        self.back_btn = ctk.CTkButton(self.nav_frame, text=self.t("back"), width=100, command=self.prev_step, fg_color="gray", hover_color="#555555")
        self.back_btn.pack(side="left")
        self.back_btn.configure(state="disabled")
        
        self.next_btn = ctk.CTkButton(self.nav_frame, text=self.t("next"), width=120, command=self.next_step)
        self.next_btn.pack(side="right")
        
        self.show_step(1)
        
        # Центрирование
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def t(self, key, *args):
        lang = getattr(self, "language", "ru")
        translation_dict = LOCALIZATION.get(lang, LOCALIZATION["ru"])
        val = translation_dict.get(key, key)
        if args:
            return val.format(*args)
        return val

    def set_window_icon(self):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png")
        if not os.path.exists(icon_path):
            icon_path = "icon.png"
        if os.path.exists(icon_path):
            try:
                self.icon_img = PhotoImage(file=icon_path)
                self.iconphoto(False, self.icon_img)
            except Exception:
                pass

    def show_step(self, step):
        # Очищаем фрейм шага
        for widget in self.step_frame.winfo_children():
            widget.destroy()
            
        self.title(self.t("wizard_title"))
        
        if step == 1:
            self.current_step = 1
            self.back_btn.configure(state="disabled")
            self.next_btn.configure(text=self.t("next"))
            self.build_step1()
        elif step == 2:
            self.current_step = 2
            self.back_btn.configure(state="normal")
            self.next_btn.configure(text=self.t("finish"))
            self.build_step2()

    def build_step1(self):
        # Шаг 1: Выбор языка
        title = ctk.CTkLabel(
            self.step_frame, 
            text=self.t("step_lang_title").replace("1 из 3", "1 из 2").replace("1 of 3", "1 of 2"), 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 10))
        
        # Отображение логотипа/значка программы, если он существует!
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png")
        if not os.path.exists(icon_path):
            icon_path = "icon.png"
        if os.path.exists(icon_path):
            try:
                self.logo_img = PhotoImage(file=icon_path)
                scaled_logo = self.logo_img.subsample(8, 8)
                self.logo_display_img = scaled_logo  # предотвращаем сборку мусора
                logo_label = Label(self.step_frame, image=scaled_logo, bg=self.cget("bg"))
                logo_label.pack(pady=(5, 15))
            except Exception:
                pass

        desc = ctk.CTkLabel(
            self.step_frame,
            text=self.t("step_lang_desc"),
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        desc.pack(anchor="w", fill="x", pady=10)
        
        self.lang_var = ctk.StringVar(value="English" if self.language == "en" else "Русский (Russian)")
        self.lang_dropdown = ctk.CTkOptionMenu(
            self.step_frame, 
            values=["Русский (Russian)", "English"],
            command=self.on_lang_change,
            width=220
        )
        self.lang_dropdown.set(self.lang_var.get())
        self.lang_dropdown.pack(pady=15)

    def on_lang_change(self, val):
        if "English" in val:
            self.language = "en"
        else:
            self.language = "ru"
        # Сохраняем язык сразу
        self.parent.db.set_setting("language", self.language)
        # Динамически обновляем кнопки навигации
        self.back_btn.configure(text=self.t("back"))
        self.next_btn.configure(text=self.t("next"))
        # Перерисовываем заголовок
        self.show_step(1)

    def build_step2(self):
        # Шаг 2: Настройка токена
        title = ctk.CTkLabel(
            self.step_frame, 
            text=self.t("step_tok_title").replace("2 из 3", "2 из 2").replace("2 of 3", "2 of 2"), 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 10))
        
        desc = ctk.CTkLabel(
            self.step_frame,
            text=self.t("step_tok_desc"),
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        desc.pack(anchor="w", fill="x", pady=10)
        
        # Поле ввода и кнопка "Вставить"
        input_container = ctk.CTkFrame(self.step_frame, fg_color="transparent")
        input_container.pack(fill="x", pady=15)
        
        self.token_entry = ctk.CTkEntry(input_container, placeholder_text=self.t("token_placeholder"), height=35)
        self.token_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Получаем текущий токен, если он уже был в бд
        curr_tok = self.parent.db.get_setting("bot_token", "")
        if curr_tok:
            self.token_entry.insert(0, curr_tok)
            
        paste_btn = ctk.CTkButton(
            input_container, 
            text=self.t("paste"), 
            width=100, 
            height=35,
            command=self.paste_token,
            fg_color="#10b981", 
            hover_color="#059669"
        )
        paste_btn.pack(side="right")
        
        # Кросс-раскладка биндинги
        self.token_entry.bind("<Control-v>", lambda e: self.paste_token())
        self.token_entry.bind("<Control-V>", lambda e: self.paste_token())
        self.token_entry.bind("<Control-KeyPress-m>", lambda e: self.paste_token())
        self.token_entry.bind("<Control-KeyPress-M>", lambda e: self.paste_token())

    def paste_token(self):
        try:
            clipboard_content = self.clipboard_get()
            if clipboard_content:
                self.token_entry.delete(0, "end")
                self.token_entry.insert(0, clipboard_content.strip())
        except Exception:
            pass
        return "break"

    def prev_step(self):
        if self.current_step == 2:
            self.show_step(1)

    def next_step(self):
        if self.current_step == 1:
            self.show_step(2)
        elif self.current_step == 2:
            token = self.token_entry.get().strip()
            if not token:
                messagebox.showwarning(self.t("warning"), self.t("token_empty_warn"))
                return
            if ":" not in token:
                messagebox.showwarning(self.t("warning"), self.t("token_invalid_warn"))
                return
            self.bot_token = token
            self.parent.db.set_setting("bot_token", token)
            self.parent.bot_token = token
            
            messagebox.showinfo(self.t("success"), self.t("wizard_success_info"))
            self.grab_release()
            self.destroy()

class SoundpadSyncApp(ctk.CTk):
    def __init__(self, db_manager, spl_manager, start_bot_callback, stop_bot_callback):
        super().__init__()
        apply_window_icon(self)
        
        self.db = db_manager
        self.spl = spl_manager
        self.start_bot_callback = start_bot_callback
        self.stop_bot_callback = stop_bot_callback
        
        self.bot_running = False
        self._auto_sync_after_id = None
        self.playing_track_id = None
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.load_settings()
        
        self.title(self.t("title"))
        self.geometry("950x650")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Установка иконки
        self.set_window_icon()
        
        self._init_layout()
        self.refresh_queue()
        self.setup_auto_sync_timer()
        
        # Проверяем, нужна ли первоначальная настройка
        self.after(500, self.check_onboarding)
        # Запускаем отслеживание статуса Soundpad
        self.after(2000, self.update_soundpad_status)

    def t(self, key, *args):
        lang = getattr(self, "language", "ru")
        translation_dict = LOCALIZATION.get(lang, LOCALIZATION["ru"])
        val = translation_dict.get(key, key)
        if args:
            return val.format(*args)
        return val

    def set_window_icon(self):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png")
        if not os.path.exists(icon_path):
            icon_path = "icon.png"
        if os.path.exists(icon_path):
            try:
                self.icon_img = PhotoImage(file=icon_path)
                self.iconphoto(False, self.icon_img)
            except Exception:
                pass

    def check_onboarding(self):
        if not self.bot_token:
            wizard = OnboardingWizard(self)
            self.wait_window(wizard)
            self.load_settings()
            self.reconfigure_ui_texts()

    def load_settings(self):
        self.language = self.db.get_setting("language", "ru")
        self.spl_path = self.db.get_setting("spl_path", "")
        self.bot_token = self.db.get_setting("bot_token", "")
        self.tracks_dir = self.db.get_setting("tracks_dir", "~/Music/Soundpad_Tracks")
        self.preferred_format = self.db.get_setting("preferred_format", "mp3")
        self.auto_sync = int(self.db.get_setting("auto_sync", "0"))
        self.sync_interval = int(self.db.get_setting("sync_interval", "900"))

    def update_soundpad_status(self):
        """Опрашивает статус Soundpad и выводит плашку-индикатор в боковом меню."""
        running = self.spl.is_soundpad_running()
        if running:
            self.sp_status_indicator.configure(
                text="● Soundpad: запущен" if self.language == "ru" else "● Soundpad: running",
                text_color="#55ff55"
            )
        else:
            self.sp_status_indicator.configure(
                text="● Soundpad: закрыт" if self.language == "ru" else "● Soundpad: closed",
                text_color="#ff5555"
            )
        self.after(5000, self.update_soundpad_status)

    def _init_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(12, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Soundpad Sync", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=15)
        
        self.bot_status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.bot_status_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.status_indicator = ctk.CTkLabel(self.bot_status_frame, text=self.t("bot_status_off"), text_color="#ff5555", font=ctk.CTkFont(size=12, weight="bold"))
        self.status_indicator.pack(pady=2)

        # Индикатор статуса Soundpad
        self.sp_status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sp_status_frame.grid(row=2, column=0, padx=10, pady=(2, 8), sticky="ew")
        self.sp_status_indicator = ctk.CTkLabel(
            self.sp_status_frame, 
            text="● Soundpad: опрос..." if self.language == "ru" else "● Soundpad: polling...", 
            text_color="#f59e0b", 
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.sp_status_indicator.pack(pady=2)
        
        self.toggle_bot_btn = ctk.CTkButton(self.sidebar, text=self.t("start_bot"), command=self.toggle_bot)
        self.toggle_bot_btn.grid(row=3, column=0, padx=20, pady=5)
        
        # Кнопка ручной настройки токена бота
        self.setup_token_btn = ctk.CTkButton(
            self.sidebar, 
            text=self.t("configure_token_btn"), 
            fg_color="#374151", 
            hover_color="#4b5563", 
            command=self.configure_token
        )
        self.setup_token_btn.grid(row=4, column=0, padx=20, pady=5)
        
        self.settings_label = ctk.CTkLabel(self.sidebar, text=self.t("sync_settings_label"), font=ctk.CTkFont(size=13, weight="bold"))
        self.settings_label.grid(row=5, column=0, padx=20, pady=(15, 5))
        
        self.format_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.format_frame.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        self.codec_lbl = ctk.CTkLabel(self.format_frame, text=self.t("codec_label"), font=ctk.CTkFont(size=11))
        self.codec_lbl.pack(anchor="w")
        self.format_dropdown = ctk.CTkOptionMenu(
            self.format_frame, 
            values=["MP3", "WAV", "OGG", "FLAC"], 
            command=self.change_format_setting
        )
        self.format_dropdown.set(self.preferred_format.upper())
        self.format_dropdown.pack(fill="x", pady=2)
        
        self.autosync_switch = ctk.CTkSwitch(
            self.sidebar, 
            text=self.t("autosync_label"), 
            command=self.toggle_autosync_setting,
            font=ctk.CTkFont(size=11)
        )
        if self.auto_sync:
            self.autosync_switch.select()
        self.autosync_switch.grid(row=7, column=0, padx=20, pady=5, sticky="w")
        
        self.interval_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.interval_frame.grid(row=8, column=0, padx=20, pady=5, sticky="ew")
        self.interval_lbl = ctk.CTkLabel(self.interval_frame, text=self.t("interval_label"), font=ctk.CTkFont(size=11))
        self.interval_lbl.pack(anchor="w")
        
        self.interval_dropdown = ctk.CTkOptionMenu(
            self.interval_frame, 
            values=["15 секунд (тест)" if self.language == "ru" else "15 seconds (test)", 
                    "1 минута" if self.language == "ru" else "1 minute", 
                    "15 минут" if self.language == "ru" else "15 minutes", 
                    "1 час" if self.language == "ru" else "1 hour", 
                    "12 часов" if self.language == "ru" else "12 hours"], 
            command=self.change_interval_setting
        )
        interval_map = {15: "15 секунд (тест)" if self.language == "ru" else "15 seconds (test)", 
                        60: "1 минута" if self.language == "ru" else "1 minute", 
                        900: "15 минут" if self.language == "ru" else "15 minutes", 
                        3600: "1 час" if self.language == "ru" else "1 hour", 
                        43200: "12 часов" if self.language == "ru" else "12 hours"}
        self.interval_dropdown.set(interval_map.get(self.sync_interval, "15 минут" if self.language == "ru" else "15 minutes"))
        self.interval_dropdown.pack(fill="x", pady=2)
        
        # Выбор языка / Language selection dropdown
        self.lang_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.lang_frame.grid(row=9, column=0, padx=20, pady=5, sticky="ew")
        self.lang_label = ctk.CTkLabel(self.lang_frame, text=self.t("language_setting_label"), font=ctk.CTkFont(size=11))
        self.lang_label.pack(anchor="w")
        self.lang_dropdown = ctk.CTkOptionMenu(
            self.lang_frame, 
            values=["Русский (Russian)", "English"], 
            command=self.change_language_setting
        )
        self.lang_dropdown.set("English" if self.language == "en" else "Русский (Russian)")
        self.lang_dropdown.pack(fill="x", pady=2)
        
        # Кнопка открытия логов и диагностики
        self.logs_btn = ctk.CTkButton(
            self.sidebar,
            text="📋 Логи и диагностика" if self.language == "ru" else "📋 Logs & Diagnostics",
            fg_color="#0f766e",
            hover_color="#0d9488",
            command=self.open_logs_window
        )
        self.logs_btn.grid(row=10, column=0, padx=20, pady=5)
        
        self.version_label = ctk.CTkLabel(self.sidebar, text="v1.2.0 (Soundpad API)", font=ctk.CTkFont(size=10))
        self.version_label.grid(row=11, column=0, pady=10)

        self.main_container = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        self.header_title = ctk.CTkLabel(self.header_frame, text=self.t("header_queue_title"), font=ctk.CTkFont(size=18, weight="bold"))
        self.header_title.pack(side="left")
        
        self.refresh_btn = ctk.CTkButton(self.header_frame, text=self.t("refresh_btn_text"), width=100, command=self.refresh_queue)
        self.refresh_btn.pack(side="right")
        
        self.queue_scroll = ctk.CTkScrollableFrame(self.main_container, label_text=self.t("queue_scroll_title"))
        self.queue_scroll.grid(row=1, column=0, sticky="nsew")

    def reconfigure_ui_texts(self):
        self.title(self.t("title"))
        
        if self.bot_running:
            self.status_indicator.configure(text=self.t("bot_status_on"), text_color="#55ff55")
            self.toggle_bot_btn.configure(text=self.t("stop_bot"))
        else:
            self.status_indicator.configure(text=self.t("bot_status_off"), text_color="#ff5555")
            self.toggle_bot_btn.configure(text=self.t("start_bot"))
            
        self.setup_token_btn.configure(text=self.t("configure_token_btn"))
        self.settings_label.configure(text=self.t("sync_settings_label"))
        self.codec_lbl.configure(text=self.t("codec_label"))
        self.autosync_switch.configure(text=self.t("autosync_label"))
        self.interval_lbl.configure(text=self.t("interval_label"))
        
        self.interval_dropdown.configure(
            values=["15 секунд (тест)" if self.language == "ru" else "15 seconds (test)", 
                    "1 минута" if self.language == "ru" else "1 minute", 
                    "15 минут" if self.language == "ru" else "15 minutes", 
                    "1 час" if self.language == "ru" else "1 hour", 
                    "12 часов" if self.language == "ru" else "12 hours"]
        )
        interval_map = {15: "15 секунд (тест)" if self.language == "ru" else "15 seconds (test)", 
                        60: "1 минута" if self.language == "ru" else "1 minute", 
                        900: "15 минут" if self.language == "ru" else "15 minutes", 
                        3600: "1 час" if self.language == "ru" else "1 hour", 
                        43200: "12 часов" if self.language == "ru" else "12 hours"}
        self.interval_dropdown.set(interval_map.get(self.sync_interval, "15 минут" if self.language == "ru" else "15 minutes"))
        
        self.lang_label.configure(text=self.t("language_setting_label"))
        self.header_title.configure(text=self.t("header_queue_title"))
        self.refresh_btn.configure(text=self.t("refresh_btn_text"))
        self.logs_btn.configure(text="📋 Логи и диагностика" if self.language == "ru" else "📋 Logs & Diagnostics")
        
        self.refresh_queue()

    def change_language_setting(self, value: str):
        if "English" in value or value == "en":
            self.language = "en"
        else:
            self.language = "ru"
        self.db.set_setting("language", self.language)
        self.reconfigure_ui_texts()

    def change_format_setting(self, value: str):
        self.preferred_format = value.lower()
        self.db.set_setting("preferred_format", self.preferred_format)
        print(f"[GUI] Format changed to: {value}")

    def toggle_autosync_setting(self):
        self.auto_sync = 1 if self.autosync_switch.get() else 0
        self.db.set_setting("auto_sync", str(self.auto_sync))
        print(f"[GUI] Auto-sync: {self.auto_sync}")
        self.setup_auto_sync_timer()

    def change_interval_setting(self, value: str):
        interval_map = {
            "15 секунд (тест)": 15, "15 seconds (test)": 15,
            "1 минута": 60, "1 minute": 60,
            "15 минут": 900, "15 minutes": 900,
            "1 час": 3600, "1 hour": 3600,
            "12 часов": 43200, "12 hours": 43200
        }
        self.sync_interval = interval_map.get(value, 900)
        self.db.set_setting("sync_interval", str(self.sync_interval))
        print(f"[GUI] Auto-sync check interval set to {self.sync_interval} seconds")
        self.setup_auto_sync_timer()

    def setup_auto_sync_timer(self):
        if self._auto_sync_after_id:
            self.after_cancel(self._auto_sync_after_id)
            self._auto_sync_after_id = None
            
        if self.auto_sync:
            self.run_auto_sync_check()

    def run_auto_sync_check(self):
        print("[GUI/Auto-Sync] Timer triggered! Scanning new tracks...")
        self.refresh_queue()
        pending = self.db.get_pending_tracks()
        if pending:
            track = pending[0]
            cat = track['predicted_category'] or ("Разное" if self.language == "ru" else "Miscellaneous")
            print(f"[GUI/Auto-Sync] Automatically approving track ID={track['id']} into category '{cat}'")
            self.approve_item(track['id'], track['mp3_path'], cat, os.path.splitext(os.path.basename(track['mp3_path']))[0])
        self._auto_sync_after_id = self.after(self.sync_interval * 1000, self.run_auto_sync_check)

    def on_closing(self):
        self.stop_audio()
        self.destroy()

    def play_audio(self, track_id: int, path: str):
        if self.playing_track_id == track_id:
            self.stop_audio()
            return

        if self.playing_track_id is not None:
            self.stop_audio()

        if not os.path.exists(path):
            messagebox.showerror(self.t("error"), self.t("file_not_found_error"))
            return

        if os.name == 'nt':
            try:
                import ctypes
                buf = ctypes.create_unicode_buffer(260)
                ctypes.windll.kernel32.GetShortPathNameW(path, buf, 260)
                short_path = buf.value if buf.value else path
                
                ctypes.windll.winmm.mciSendStringW("close temp_track", None, 0, None)
                cmd_open = f'open "{short_path}" type mpegvideo alias temp_track'
                res_open = ctypes.windll.winmm.mciSendStringW(cmd_open, None, 0, None)
                if res_open == 0:
                    ctypes.windll.winmm.mciSendStringW("play temp_track", None, 0, None)
                    self.playing_track_id = track_id
                    self.refresh_queue()
                else:
                    os.startfile(path)
            except Exception as e:
                print(f"[Audio] MCI Error: {e}")
                try:
                    os.startfile(path)
                except Exception:
                    pass
        else:
            try:
                import subprocess
                import sys
                if sys.platform == 'darwin':
                    subprocess.Popen(['open', path])
                else:
                    subprocess.Popen(['xdg-open', path])
            except Exception as e:
                print(f"[Audio] Playback Error: {e}")

    def stop_audio(self):
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.winmm.mciSendStringW("stop temp_track", None, 0, None)
                ctypes.windll.winmm.mciSendStringW("close temp_track", None, 0, None)
            except Exception as e:
                print(f"[Audio] MCI Stop Error: {e}")
        self.playing_track_id = None
        self.refresh_queue()

    def configure_token(self):
        """Открывает диалоговое окно настройки токена."""
        dialog = TokenDialog(self, current_token=self.bot_token, language=self.language)
        self.wait_window(dialog)
        if dialog.result is not None:
            token = dialog.result
            self.db.set_setting("bot_token", token)
            self.bot_token = token
            messagebox.showinfo(self.t("success"), self.t("token_dialog_success"))
            return token
        return None

    def toggle_bot(self):
        if not self.bot_running:
            # Проверяем, запущен ли Soundpad (именованный пайп)
            if not self.spl.is_soundpad_running():
                msg = (
                    "Soundpad не запущен!\n\n"
                    "Для работы программы и синхронизации звуков необходимо, чтобы Soundpad был запущен.\n"
                    "Пожалуйста, откройте Soundpad и попробуйте снова."
                    if self.language == "ru" else
                    "Soundpad is not running!\n\n"
                    "For the program and sound synchronization to work, Soundpad must be running.\n"
                    "Please open Soundpad and try again."
                )
                messagebox.showwarning(self.t("warning"), msg)
                return

            token = self.bot_token
            if not token:
                token = self.configure_token()
                if not token:
                    return
                
            success = self.start_bot_callback(token)
            if success:
                self.bot_running = True
                self.status_indicator.configure(text=self.t("bot_status_on"), text_color="#55ff55")
                self.toggle_bot_btn.configure(text=self.t("stop_bot"), fg_color="#ff4444", hover_color="#cc3333")
            else:
                messagebox.showerror(self.t("start_bot_error_title"), self.t("start_bot_error_desc"))
        else:
            self.stop_bot_callback()
            self.bot_running = False
            self.status_indicator.configure(text=self.t("bot_status_off"), text_color="#ff5555")
            self.toggle_bot_btn.configure(text=self.t("start_bot"), fg_color=["#3b82f6", "#1d4ed8"])

    def choose_spl_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите плейлист Soundpad (.spl)" if self.language == "ru" else "Select Soundpad Playlist (.spl)",
            filetypes=[("Soundpad Playlist", "*.spl")]
        )
        if file_path:
            self.db.set_setting("spl_path", file_path)
            self.spl_path = file_path
            self.spl.spl_path = file_path
            messagebox.showinfo(self.t("success"), self.t("spl_saved_success", file_path))

    def refresh_queue(self):
        if not hasattr(self, "queue_scroll"):
            return
            
        for widget in self.queue_scroll.winfo_children():
            widget.destroy()
            
        tracks = self.db.get_pending_tracks()
        
        if not tracks:
            no_tracks_label = ctk.CTkLabel(self.queue_scroll, text=self.t("no_tracks_text"), font=ctk.CTkFont(slant="italic"))
            no_tracks_label.pack(pady=40)
            return

        categories = self.spl.get_categories()
        default_cat = "Разное" if self.language == "ru" else "Miscellaneous"
        if default_cat not in categories:
            categories.insert(0, default_cat)

        for i, track in enumerate(tracks):
            track_id = track['id']
            item_frame = ctk.CTkFrame(self.queue_scroll, corner_radius=8)
            item_frame.pack(fill="x", padx=10, pady=5)
            
            item_frame.columnconfigure(0, weight=1)
            
            orig_filename = os.path.basename(track['mp3_path'])
            base_name, ext = os.path.splitext(orig_filename)
            desc_text = track['description'][:100] + "..." if len(track['description'] or "") > 100 else track['description']
            
            name_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            name_frame.grid(row=0, column=0, padx=15, pady=10, sticky="w")
            
            name_label = ctk.CTkLabel(name_frame, text=self.t("track_name_label"), font=ctk.CTkFont(size=11, weight="bold"))
            name_label.pack(anchor="w")
            
            name_input_frame = ctk.CTkFrame(name_frame, fg_color="transparent")
            name_input_frame.pack(fill="x", pady=2)
            
            is_playing = (self.playing_track_id == track_id)
            play_text = self.t("play_btn_stop") if is_playing else self.t("play_btn_play")
            play_color = "#f59e0b" if is_playing else "#10b981"
            play_hover = "#d97706" if is_playing else "#059669"
            
            play_cmd = lambda t_id=track_id, path=track['mp3_path']: self.play_audio(t_id, path)
            play_btn = ctk.CTkButton(name_input_frame, text=play_text, width=85, height=28, fg_color=play_color, hover_color=play_hover, command=play_cmd)
            play_btn.pack(side="left", padx=(0, 5))
            
            name_input = ctk.CTkEntry(name_input_frame, width=220)
            name_input.insert(0, base_name)
            name_input.pack(side="left", fill="x", expand=True)
            
            if desc_text:
                desc_label = ctk.CTkLabel(name_frame, text=f"📝 {desc_text}", font=ctk.CTkFont(size=10, slant="italic"), text_color="gray")
                desc_label.pack(anchor="w", pady=(2, 0))
            
            cat_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            cat_frame.grid(row=0, column=1, padx=10, pady=10)
            
            cat_label = ctk.CTkLabel(cat_frame, text=self.t("category_label"), font=ctk.CTkFont(size=11))
            cat_label.pack()
            
            cat_input = ctk.CTkComboBox(cat_frame, width=140, values=categories)
            cat_input.set(track['predicted_category'] or default_cat)
            cat_input.pack()
            
            btn_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=2, padx=15, pady=10)
            
            approve_cmd = lambda t_id=track_id, path=track['mp3_path'], inp_cat=cat_input, inp_name=name_input: self.approve_item(t_id, path, inp_cat.get(), inp_name.get())
            reject_cmd = lambda t_id=track_id: self.reject_item(t_id)
            
            app_btn = ctk.CTkButton(btn_frame, text=self.t("approve_btn_text"), width=80, height=28, fg_color="#22c55e", hover_color="#16a34a", command=approve_cmd)
            app_btn.pack(side="left", padx=5)
            
            rej_btn = ctk.CTkButton(btn_frame, text=self.t("reject_btn_text"), width=80, height=28, fg_color="#ef4444", hover_color="#dc2626", command=reject_cmd)
            rej_btn.pack(side="left", padx=5)

    def approve_item(self, track_id: int, temp_path: str, confirmed_category: str, new_filename_base: str):
        # Останавливаем воспроизведение, чтобы разблокировать доступ к файлу на Windows
        if self.playing_track_id == track_id:
            self.stop_audio()

        # Проверка: если Soundpad не запущен — выводим пользователю предупреждение и не даем сломать процесс
        if not self.spl.is_soundpad_running():
            msg = (
                "Soundpad не запущен!\n\n"
                "Для работы API и добавления звуков программа Soundpad должна быть открыта на вашем компьютере.\n"
                "Запустите Soundpad и попробуйте снова."
                if self.language == "ru" else
                "Soundpad is not running!\n\n"
                "For the API to function and add sounds, the Soundpad application must be open on your computer.\n"
                "Please run Soundpad and try again."
            )
            messagebox.showwarning(self.t("warning"), msg)
            return

        if not os.path.exists(temp_path):
            messagebox.showerror(self.t("error"), self.t("track_file_not_found_error"))
            self.db.reject_track(track_id)
            self.refresh_queue()
            return
            
        base_dest_dir = os.path.expanduser(self.tracks_dir)
        category_dir = os.path.join(base_dest_dir, confirmed_category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Санитизация названия файла от запрещенных символов Windows (двойное экранирование слэша исправлено)
        for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            new_filename_base = new_filename_base.replace(char, '_')
        # Пробелы (в т.ч. несколько подряд) заменяем на один "_", чтобы имя файла
        # было предсказуемым и не создавало проблем при передаче его дальше.
        new_filename_base = re.sub(r'\s+', '_', new_filename_base)
        # Windows не допускает точки/пробелы/подчёркивания в конце имени файла
        # (они молча обрезаются самой ОС), поэтому убираем их сами, чтобы имя
        # на диске совпадало с тем, что мы дальше передаём в Soundpad.
        new_filename_base = new_filename_base.strip('._ ')
        if not new_filename_base:
            new_filename_base = "track"
            
        _, ext = os.path.splitext(temp_path)
        filename = f"{new_filename_base}{ext}"
        final_path = os.path.join(category_dir, filename)
        
        try:
            if temp_path != final_path:
                shutil.move(temp_path, final_path)
            
            sound_title, _ = os.path.splitext(filename)
            spl_success = self.spl.add_sound(
                file_path=final_path,
                title=sound_title,
                category_name=confirmed_category
            )
            
            if spl_success:
                self.db.approve_track(track_id, confirmed_category, final_path)
                self.refresh_queue()
            else:
                messagebox.showerror(self.t("error"), self.t("spl_modify_error"))
                
        except Exception as e:
            messagebox.showerror(self.t("error"), self.t("move_file_error", e))

    def reject_item(self, track_id: int):
        self.db.reject_track(track_id)
        self.refresh_queue()

    def open_logs_window(self):
        """Открывает окно просмотра логов и запуска диагностики."""
        # Закрываем предыдущее окно, если оно уже открыто
        if hasattr(self, "_logs_window") and self._logs_window.winfo_exists():
            self._logs_window.focus()
            return
            
        self._logs_window = LogsWindow(self, language=self.language)


class LogsWindow(ctk.CTkToplevel):
    """
    Окно просмотра логов сессии и запуска живой диагностики Soundpad API и окружения.
    """
    def __init__(self, parent, language="ru"):
        super().__init__(parent)
        apply_window_icon(self)
        self.parent = parent
        self.language = language
        
        self.title("Логи и Диагностика" if self.language == "ru" else "Logs & Diagnostics")
        self.geometry("750x550")
        self.minsize(600, 400)
        
        # Размещаем окно поверх родительского
        self.after(250, self.lift)
        self.focus_force()
        
        self._init_ui()
        self.refresh_logs()

    def _init_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Верхняя панель с кнопками управления
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        
        self.diag_btn = ctk.CTkButton(
            self.top_bar, 
            text="🔍 Запустить диагностику" if self.language == "ru" else "🔍 Run Diagnostics",
            fg_color="#0284c7",
            hover_color="#0369a1",
            command=self.run_diagnostics
        )
        self.diag_btn.pack(side="left", padx=(0, 10))
        
        self.refresh_btn = ctk.CTkButton(
            self.top_bar,
            text="🔄 Обновить" if self.language == "ru" else "🔄 Refresh",
            width=100,
            command=self.refresh_logs
        )
        self.refresh_btn.pack(side="left", padx=5)
        
        self.copy_btn = ctk.CTkButton(
            self.top_bar,
            text="📋 Скопировать всё" if self.language == "ru" else "📋 Copy All",
            width=120,
            fg_color="#16a34a",
            hover_color="#15803d",
            command=self.copy_logs
        )
        self.copy_btn.pack(side="left", padx=5)

        self.clear_btn = ctk.CTkButton(
            self.top_bar,
            text="🗑️ Очистить" if self.language == "ru" else "🗑️ Clear",
            width=100,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=self.clear_logs
        )
        self.clear_btn.pack(side="left", padx=5)
        
        # Текстовое поле логов
        self.textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=11))
        self.textbox.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        
        # Нижняя панель
        self.bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_bar.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="ew")
        
        self.open_file_btn = ctk.CTkButton(
            self.bottom_bar,
            text="📂 Открыть файл логов" if self.language == "ru" else "📂 Open Log File",
            fg_color="#4b5563",
            hover_color="#374151",
            command=self.open_log_file
        )
        self.open_file_btn.pack(side="left")
        
        self.close_btn = ctk.CTkButton(
            self.bottom_bar,
            text="Закрыть" if self.language == "ru" else "Close",
            width=100,
            command=self.destroy
        )
        self.close_btn.pack(side="right")

    def get_log_path(self):
        return "data/soundpad_sync.log"

    def refresh_logs(self):
        log_path = self.get_log_path()
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    # Защита от зависаний UI при огромном логе
                    if len(content) > 150000:
                        content = "... [Логи урезаны для оптимизации отображения] ...\n" + content[-150000:]
                    self.textbox.insert("1.0", content)
            except Exception as e:
                self.textbox.insert("1.0", f"Ошибка чтения логов: {e}" if self.language == "ru" else f"Error reading logs: {e}")
        else:
            self.textbox.insert("1.0", "Лог-файл пуст или ещё не создан." if self.language == "ru" else "Log file is empty or not created yet.")
            
        self.textbox.configure(state="disabled")
        self.textbox.see("end")

    def copy_logs(self):
        self.clipboard_clear()
        self.clipboard_append(self.textbox.get("1.0", "end-1c"))
        messagebox.showinfo(
            "Успешно" if self.language == "ru" else "Success",
            "Логи успешно скопированы в буфер обмена!" if self.language == "ru" else "Logs successfully copied to clipboard!"
        )

    def clear_logs(self):
        confirm = messagebox.askyesno(
            "Подтверждение" if self.language == "ru" else "Confirmation",
            "Очистить всю историю логов в файле?" if self.language == "ru" else "Are you sure you want to clear all log history?"
        )
        if confirm:
            log_path = self.get_log_path()
            try:
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write("")
                self.refresh_logs()
            except Exception as e:
                messagebox.showerror("Ошибка" if self.language == "ru" else "Error", f"Не удалось очистить файл: {e}")

    def open_log_file(self):
        log_path = self.get_log_path()
        if os.path.exists(log_path):
            try:
                import platform
                import subprocess
                if platform.system() == "Windows":
                    os.startfile(log_path)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", log_path])
                else:
                    subprocess.Popen(["xdg-open", log_path])
            except Exception as e:
                messagebox.showerror("Ошибка" if self.language == "ru" else "Error", f"Не удалось запустить файл: {e}")
        else:
            messagebox.showwarning(
                "Предупреждение" if self.language == "ru" else "Warning",
                "Файл логов ещё не создан." if self.language == "ru" else "Log file not found."
            )

    def run_diagnostics(self):
        self.diag_btn.configure(state="disabled")
        threading.Thread(target=self._diagnostics_worker, daemon=True).start()

    def _diagnostics_worker(self):
        import platform
        import socket
        import datetime
        import sys
        
        self.textbox.configure(state="normal")
        self.textbox.insert("end", f"\n\n=================================\n")
        self.textbox.insert("end", f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ЗАПУСК ДИАГНОСТИКИ...\n")
        self.textbox.insert("end", f"=================================\n")
        
        # 1. Информация о системе
        self.textbox.insert("end", f"[SYS] Операционная система: {platform.system()} {platform.release()} ({platform.architecture()[0]})\n")
        self.textbox.insert("end", f"[SYS] Версия Python: {platform.python_version()}\n")
        
        # 2. Проверка прав Администратора
        is_admin = False
        if platform.system() == "Windows":
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception as e:
                self.textbox.insert("end", f"[SYS] Ошибка проверки прав администратора: {e}\n")
        self.textbox.insert("end", f"[SYS] Программа запущена с правами Администратора: {'ДА' if is_admin else 'НЕТ'}\n")
        
        # 3. Процесс Soundpad
        self.textbox.insert("end", "[SP_API] Поиск процесса Soundpad.exe...\n")
        sp_running = self.parent.spl.is_soundpad_running()
        self.textbox.insert("end", f"[SP_API] Soundpad запущен: {'ДА' if sp_running else 'НЕТ'}\n")
        
        # 4. Проверка Named Pipe (только на Windows)
        if platform.system() == "Windows":
            self.textbox.insert("end", "[SP_API] Проверка доступности Named Pipe \\.\\pipe\\sp_remote_control...\n")
            pipe_exists = os.path.exists(r"\\.\\pipe\\sp_remote_control")
            self.textbox.insert("end", f"[SP_API] Канал Soundpad (sp_remote_control) обнаружен в ОС: {'ДА' if pipe_exists else 'НЕТ'}\n")
            
            # Тестовое подключение
            try:
                handle, err_desc = self.parent.spl._connect_to_pipe()
                if handle:
                    self.textbox.insert("end", "[SP_API] Успешное прямое подключение к каналу Soundpad!\n")
                    try:
                        import ctypes
                        ctypes.windll.kernel32.CloseHandle(handle)
                    except Exception:
                        pass
                else:
                    self.textbox.insert("end", f"[SP_API] НЕ удалось подключиться к каналу: {err_desc}\n")
                    self.textbox.insert("end", "[RECOM] СОВЕТ: Откройте Soundpad -> Настройки -> Разработчикам -> Включить API разработчика.\n")
                    if is_admin:
                        self.textbox.insert("end", "[RECOM] СОВЕТ: Убедитесь, что Soundpad ТОЖЕ запущен от имени Администратора.\n")
                    else:
                        self.textbox.insert("end", "[RECOM] СОВЕТ: Если Soundpad запущен от имени Администратора, запустите эту утилиту ТОЖЕ от имени Администратора.\n")
            except Exception as e:
                self.textbox.insert("end", f"[SP_API] Исключение при тесте канала: {e}\n")
        else:
            self.textbox.insert("end", "[SP_API] Named Pipes не поддерживаются на этой операционной системе.\n")
            
        # 5. Тестирование команд Soundpad API
        if sp_running and platform.system() == "Windows":
            self.textbox.insert("end", "[SP_API] Тестирование запросов к Soundpad по API...\n")
            try:
                trial_res = self.parent.spl.is_trial()
                self.textbox.insert("end", f"[SP_API] IsTrial() (Триальная версия): {'ДА' if trial_res else 'НЕТ / Не удалось получить'}\n")
                
                raw_trial = self.parent.spl.send_command("IsTrial()")
                self.textbox.insert("end", f"[SP_API] Ответ на IsTrial(): {raw_trial}\n")
                
                ver_res = self.parent.spl.send_command("GetVersion()")
                self.textbox.insert("end", f"[SP_API] Ответ на GetVersion(): {ver_res}\n")
            except Exception as e:
                self.textbox.insert("end", f"[SP_API] Исключение при отправке команд: {e}\n")
                
        # 6. Сеть и Telegram API
        self.textbox.insert("end", "[NET] Проверка доступности Telegram API...\n")
        try:
            socket.gethostbyname("api.telegram.org")
            self.textbox.insert("end", "[NET] Домен api.telegram.org успешно разрешен в IP.\n")
        except Exception as e:
            self.textbox.insert("end", f"[NET] Ошибка DNS-запроса к Telegram (возможно нет интернета): {e}\n")
            
        # 7. Бот статус
        bot_run = getattr(self.parent, "bot_running", False)
        self.textbox.insert("end", f"[BOT] Статус бота в программе: {'АКТИВЕН' if bot_run else 'ВЫКЛЮЧЕН'}\n")
        if self.parent.bot_token:
            masked = self.parent.bot_token[:8] + "..." + self.parent.bot_token[-4:] if len(self.parent.bot_token) > 12 else "неверный формат"
            self.textbox.insert("end", f"[BOT] Токен настроен: {masked}\n")
        else:
            self.textbox.insert("end", "[BOT] Токен не настроен. Бот не сможет запуститься.\n")
            
        self.textbox.insert("end", f"=================================\n")
        self.textbox.insert("end", f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ДИАГНОСТИКА ЗАВЕРШЕНА!\n")
        self.textbox.insert("end", f"=================================\n\n")
        
        self.textbox.configure(state="disabled")
        self.textbox.see("end")
        self.diag_btn.configure(state="normal")


class TokenDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_token="", language="ru"):
        super().__init__(parent)
        apply_window_icon(self)
        self.parent = parent
        self.language = language
        self.result = None
        
        self.title(self.t("token_dialog_title"))
        self.geometry("500x250")
        self.resizable(False, False)
        
        # Модальный режим
        self.transient(parent)
        self.grab_set()
        
        self._init_ui(current_token)
        
        # Центрирование
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
    def t(self, key):
        return self.parent.t(key)
        
    def _init_ui(self, current_token):
        self.grid_columnconfigure(0, weight=1)
        
        # Метка с описанием
        self.label = ctk.CTkLabel(
            self,
            text=self.t("token_dialog_label"),
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        self.label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Поле ввода и кнопка "Вставить"
        self.input_container = ctk.CTkFrame(self, fg_color="transparent")
        self.input_container.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        self.entry = ctk.CTkEntry(
            self.input_container,
            placeholder_text=self.t("token_placeholder") or "12345:AAAbbb...",
            height=32
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        if current_token:
            self.entry.insert(0, current_token)
            
        self.paste_btn = ctk.CTkButton(
            self.input_container,
            text=self.t("paste"),
            width=80,
            height=32,
            fg_color="#10b981",
            hover_color="#059669",
            command=self.paste_token
        )
        self.paste_btn.pack(side="right")
        
        # Подсказка
        self.hint = ctk.CTkLabel(
            self,
            text=self.t("token_dialog_hint"),
            font=ctk.CTkFont(size=10, slant="italic"),
            text_color="gray",
            justify="left"
        )
        self.hint.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        # Кнопки управления (Сохранить, Отмена)
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=3, column=0, padx=20, pady=(20, 15), sticky="e")
        
        self.save_btn = ctk.CTkButton(
            self.btn_frame,
            text=self.t("save"),
            width=100,
            command=self.save_token
        )
        self.save_btn.pack(side="left", padx=5)
        
        self.cancel_btn = ctk.CTkButton(
            self.btn_frame,
            text=self.t("cancel"),
            width=100,
            fg_color="gray",
            hover_color="#555555",
            command=self.destroy
        )
        self.cancel_btn.pack(side="left", padx=5)
        
        # Биндинги
        self.entry.bind("<Control-v>", lambda e: self.paste_token())
        self.entry.bind("<Control-V>", lambda e: self.paste_token())
        self.entry.bind("<Control-KeyPress-m>", lambda e: self.paste_token())
        self.entry.bind("<Control-KeyPress-M>", lambda e: self.paste_token())
        self.entry.bind("<Return>", lambda e: self.save_token())
        
    def paste_token(self):
        try:
            clipboard_content = self.clipboard_get()
            if clipboard_content:
                self.entry.delete(0, "end")
                self.entry.insert(0, clipboard_content.strip())
        except Exception:
            pass
        return "break"
        
    def save_token(self):
        token = self.entry.get().strip()
        if not token:
            messagebox.showwarning(self.t("warning"), self.t("token_dialog_empty_warn"))
            return
        if ":" not in token:
            messagebox.showwarning(self.t("warning"), self.t("token_invalid_warn"))
            return
        self.result = token
        self.destroy()
