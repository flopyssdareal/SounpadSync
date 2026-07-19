import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
import yt_dlp

class TelegramBotManager:
    """
    Класс для управления Telegram-ботом на aiogram v3.
    """
    def __init__(self, token: str, db_manager, download_dir: str):
        self.token = token
        self.db = db_manager
        self.download_dir = os.path.expanduser(download_dir)
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.loop = None
        self._setup_handlers()

    def _setup_handlers(self):
        @self.dp.message(CommandStart())
        async def cmd_start(message: Message):
            await message.reply(
                "Привет! Отправь мне ссылку на TikTok/YouTube Short, "
                "и я автоматически скачаю звук и подготовлю его для добавления в твой Soundpad!"
            )

        @self.dp.message()
        async def handle_message(message: Message):
            text = message.text or ""
            urls = re.findall(r'https?://[^\s]+', text)
            
            if not urls:
                await message.reply("Пожалуйста, отправь валидную ссылку на видео (TikTok, Shorts, и др.).")
                return

            url = urls[0].split()[0]
            status_msg = await message.reply("⏳ Начинаю парсинг и загрузку трека...")
            
            loop = asyncio.get_running_loop()
            try:
                track_info = await loop.run_in_executor(
                    None, self._download_and_extract, url
                )
                
                if track_info:
                    predicted_cat = self._predict_category(track_info['description'])
                    
                    track_id = self.db.add_track_to_queue(
                        tik_tok_url=url,
                        mp3_path=track_info['filepath'],
                        description=track_info['description'],
                        predicted_category=predicted_cat
                    )
                    
                    preferred_format = self.db.get_setting("preferred_format", "mp3").upper()
                    
                    notice = ""
                    if track_info.get('used_fallback'):
                        actual_ext = track_info.get('actual_ext', 'm4a').upper()
                        notice = (
                            f"\n\n⚠️ *Внимание:* Звук скачан в исходном формате (*{actual_ext}*), "
                            f"так как на вашем ПК не удалось запустить конвертер (ffmpeg/ffprobe).\n"
                            f"Для автоконвертации в *{preferred_format}* положите `ffmpeg.exe` и `ffprobe.exe` рядом с `main.py`."
                        )
                    
                    await status_msg.edit_text(
                        f"✅ Трек успешно скачан и добавлен в очередь на ПК!\n"
                        f"🎵 *Название:* {track_info['title']}\n"
                        f"🏷️ *Предложенная категория:* {predicted_cat}"
                        f"{notice}\n\n"
                        f"Утвердите трек в приложении на компьютере.",
                        parse_mode="Markdown"
                    )
                else:
                    await status_msg.edit_text("❌ Не удалось извлечь аудио из ссылки.")
            except Exception as e:
                await status_msg.edit_text(f"❌ Ошибка при загрузке: {str(e)}")

    def _predict_category(self, description: str) -> str:
        if not description:
            return "Разное"
            
        desc_lower = description.lower()
        rules = {
            "Мемы": ["мем", "прикол", "смех", "lol", "joke", "funny", "haha"],
            "Музыка": ["песня", "music", "трек", "song", "remix", "кавер", "cover"],
            "Аниме": ["аниме", "anime", "naruto", "наруто", "тян", "kun"],
            "Игры": ["игра", "csgo", "dota", "minecraft", "игры", "gaming", "steam"],
            "Фильмы": ["фильм", "кино", "сериал", "cinema", "movie", "clip"]
        }
        
        for cat, keywords in rules.items():
            if any(keyword in desc_lower for keyword in keywords):
                return cat
                
        return "Разное"

    def _sanitize_filename(self, filename: str) -> str:
        # Удаляем управляющие символы (0-31) и запрещенные в Windows символы: \ / : * ? " < > |
        forbidden = set(chr(i) for i in range(32)) | set('\\/*?:"<>|')
        cleaned = "".join(c for c in filename if c not in forbidden)
        
        # Оставляем только латиницу (ASCII 32-127), кириллицу (0x0400-0x04FF), пробелы, дефисы и подчеркивания
        cleaned = "".join(
            c for c in cleaned
            if (32 <= ord(c) <= 127) or (0x0400 <= ord(c) <= 0x04FF) or c in " _-"
        )
        
        # Срезаем пробелы по краям
        cleaned = cleaned.strip()
        # Ограничиваем длину имени файла до 100 символов, чтобы избежать превышения лимитов путей на Windows
        if len(cleaned) > 100:
            cleaned = cleaned[:100].strip()
        return cleaned if cleaned else "track"

    def _download_and_extract(self, url: str) -> dict:
        os.makedirs(self.download_dir, exist_ok=True)
        
        preferred_format = self.db.get_setting("preferred_format", "mp3").lower()
        if preferred_format not in ["mp3", "wav", "ogg", "flac"]:
            preferred_format = "mp3"
            
        postprocessors = []
        pp = {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': preferred_format,
        }
        if preferred_format in ['mp3', 'ogg']:
            pp['preferredquality'] = '192'
        postprocessors.append(pp)
        
        # Автоматическое определение папки проекта для поиска ffmpeg/ffprobe
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Получаем короткий 8.3 путь для Windows, чтобы избежать проблем с кириллицей (например, "Проекты")
        download_dir_for_ytdl = self.download_dir
        if os.name == 'nt':
            try:
                import ctypes
                buf = ctypes.create_unicode_buffer(260)
                ctypes.windll.kernel32.GetShortPathNameW(project_root, buf, 260)
                if buf.value:
                    project_root = buf.value
                
                buf_dl = ctypes.create_unicode_buffer(260)
                ctypes.windll.kernel32.GetShortPathNameW(self.download_dir, buf_dl, 260)
                if buf_dl.value:
                    download_dir_for_ytdl = buf_dl.value
            except Exception:
                pass
        
        # Добавляем в PATH для надежного вызова ffprobe/ffmpeg дочерними процессами на Windows
        if project_root not in os.environ.get("PATH", ""):
            os.environ["PATH"] = project_root + os.pathsep + os.environ.get("PATH", "")
        
        # Настройки yt-dlp: добавляем cookiesfrombrowser и user-agent заголовки для обхода возрастных ограничений TikTok
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_dir_for_ytdl, '%(id)s.%(ext)s'),
            'postprocessors': postprocessors,
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': project_root,
            'cookies_from_browser': 'chrome',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
        
        info = None
        used_fallback = False
        
        # Попытка 1: С полной конвертацией (требует ffmpeg/ffprobe)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
        except Exception as e:
            print(f"[BOT] Ошибка постобработки: {e}. Переходим в режим скачивания без конвертации...")
            used_fallback = True
            
            # Попытка 2: Скачивание без постпроцессоров (не требует ffprobe для конвертации)
            ydl_opts_fallback = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(download_dir_for_ytdl, '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'ffmpeg_location': project_root,
                'cookies_from_browser': 'chrome',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                }
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts_fallback) as ydl:
                    info = ydl.extract_info(url, download=True)
            except Exception as ex:
                raise Exception(f"Не удалось скачать трек даже без конвертации: {ex}")

        if not info:
            raise Exception("Не удалось получить информацию о треке.")

        title = info.get('title', 'Unknown Track')
        description = info.get('description', '') or info.get('title', '')
        video_id = info.get('id', 'temp_id')
        
        # Нам нужно найти скачанный файл
        actual_ext = preferred_format
        temp_filepath = os.path.join(download_dir_for_ytdl, f"{video_id}.{preferred_format}")
        
        if not os.path.exists(temp_filepath):
            # Проверяем другие возможные расширения
            for ext in ['m4a', 'webm', 'mp3', 'wav', 'ogg', 'aac', 'mp4']:
                possible_path = os.path.join(download_dir_for_ytdl, f"{video_id}.{ext}")
                if os.path.exists(possible_path):
                    temp_filepath = possible_path
                    actual_ext = ext
                    break
        
        # Санитизируем название для итогового файла
        sanitized_title = self._sanitize_filename(title)
        final_filename = f"{sanitized_title}.{actual_ext}"
        final_filepath = os.path.join(self.download_dir, final_filename)
        
        # Разрешаем коллизии имен файлов
        counter = 1
        while os.path.exists(final_filepath):
            final_filename = f"{sanitized_title}_{counter}.{actual_ext}"
            final_filepath = os.path.join(self.download_dir, final_filename)
            counter += 1
            
        # Переименовываем
        if os.path.exists(temp_filepath):
            try:
                os.rename(temp_filepath, final_filepath)
                print(f"[BOT] Файл переименован: {temp_filepath} -> {final_filepath}")
            except Exception as e:
                print(f"[BOT] Ошибка переименования: {e}")
                final_filepath = temp_filepath
        else:
            # Резервный поиск файла, если yt-dlp сохранил его под оригинальным именем
            expected_filename = ydl.prepare_filename(info)
            base_path, _ = os.path.splitext(expected_filename)
            base_name_only = os.path.basename(base_path)
            found = False
            for f in os.listdir(download_dir_for_ytdl):
                if f.startswith(base_name_only) or f.startswith(video_id):
                    possible_path = os.path.join(download_dir_for_ytdl, f)
                    _, f_ext = os.path.splitext(f)
                    actual_ext = f_ext.replace('.', '')
                    try:
                        final_filename = f"{sanitized_title}.{actual_ext}"
                        final_filepath = os.path.join(self.download_dir, final_filename)
                        os.rename(possible_path, final_filepath)
                        found = True
                        break
                    except Exception:
                        pass
            if not found:
                final_filepath = temp_filepath
        
        return {
            'title': title,
            'description': description,
            'filepath': final_filepath,
            'used_fallback': used_fallback,
            'actual_ext': actual_ext
        }

    async def start(self):
        print("[BOT] Запуск бота...")
        await self.dp.start_polling(self.bot)
