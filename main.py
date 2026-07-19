import os
import asyncio
import threading
import sys
import datetime

# Класс для перенаправления вывода в файл и в стандартный поток одновременно
class DualStream:
    def __init__(self, stream, file_path):
        self.stream = stream
        self.file_path = file_path

    def write(self, data):
        # В exe, собранном с --windowed (без консоли), sys.__stdout__/__stderr__
        # равны None - писать в них нельзя, но в лог-файл писать всё равно нужно.
        if self.stream is not None:
            try:
                self.stream.write(data)
                self.stream.flush()
            except Exception:
                pass
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(data)
        except Exception:
            pass

    def flush(self):
        if self.stream is not None:
            try:
                self.stream.flush()
            except Exception:
                pass

def setup_logging():
    os.makedirs("data", exist_ok=True)
    log_path = "data/soundpad_sync.log"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- SESSION STARTED AT {datetime.datetime.now().isoformat()} ---\n")
    except Exception:
        pass
    sys.stdout = DualStream(sys.__stdout__, log_path)
    sys.stderr = DualStream(sys.__stderr__, log_path)

# Вызываем настройку логирования до импорта остальных модулей
setup_logging()

from modules.db_manager import DatabaseManager
from modules.spl_manager import SoundpadSPLManager
from modules.bot_manager import TelegramBotManager
from modules.gui_app import SoundpadSyncApp

# Конфигурация путей по умолчанию
DB_PATH = "data/app_database.db"
DEFAULT_SPL = "~/Documents/Soundpad/soundlists/telegram_sync.spl"
DOWNLOADS_DIR = "~/Music/Soundpad_Tracks"

class AppOrchestrator:
    """
    Класс для координации жизненного цикла GUI и асинхронного фонового Telegram-бота.
    """
    def __init__(self):
        # Инициализация БД и парсера SPL
        self.db = DatabaseManager(DB_PATH)
        spl_path = self.db.get_setting("spl_path", DEFAULT_SPL)
        self.spl = SoundpadSPLManager(spl_path)
        
        self.bot_thread = None
        self.bot_loop = None
        self.bot_manager = None

    def start_bot(self, token: str) -> bool:
        """Запускает цикл событий Telegram-бота в отдельном фоновом потоке."""
        if self.bot_thread and self.bot_thread.is_alive():
            return True
            
        try:
            # Создаем поток, который будет крутить event loop для aiogram
            self.bot_thread = threading.Thread(target=self._run_bot_event_loop, args=(token,), daemon=True)
            self.bot_thread.start()
            return True
        except Exception as e:
            print(f"[MAIN] Ошибка старта бота: {e}")
            return False

    def _run_bot_event_loop(self, token: str):
        """Метод, выполняемый внутри фонового потока."""
        self.bot_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.bot_loop)
        
        self.bot_manager = TelegramBotManager(
            token=token,
            db_manager=self.db,
            download_dir=DOWNLOADS_DIR
        )
        
        try:
            self.bot_loop.run_until_complete(self.bot_manager.start())
        except asyncio.CancelledError:
            print("[MAIN] Задачи бота были отменены.")
        except Exception as e:
            print(f"[MAIN] Ошибка в работе бота: {e}")
        finally:
            try:
                # Отменяем все оставшиеся задачи в цикле событий перед закрытием
                pending = asyncio.all_tasks(self.bot_loop)
                for task in pending:
                    task.cancel()
                if pending:
                    self.bot_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
                if not self.bot_loop.is_closed():
                    self.bot_loop.close()
            except Exception as e:
                print(f"[MAIN] Ошибка при очистке loop: {e}")

    async def _async_stop_bot(self):
        if self.bot_manager:
            try:
                print("[BOT] Останавливаем polling...")
                await self.bot_manager.dp.stop_polling()
            except Exception as e:
                print(f"[BOT] Ошибка при остановке polling: {e}")
            try:
                print("[BOT] Закрываем сессию бота...")
                await self.bot_manager.bot.session.close()
            except Exception as e:
                print(f"[BOT] Ошибка при закрытии сессии бота: {e}")

    def stop_bot(self):
        """Безопасно останавливает фоновый Telegram-бот в отдельном потоке без фризов GUI."""
        if not self.bot_loop:
            return

        def _stop_worker():
            print("[MAIN] Запуск фонового процесса остановки бота...")
            if self.bot_loop and self.bot_loop.is_running():
                future = asyncio.run_coroutine_threadsafe(self._async_stop_bot(), self.bot_loop)
                try:
                    future.result(timeout=4.0)
                except Exception as e:
                    print(f"[MAIN] Ошибка при асинхронной остановке бота в потоке: {e}")
                
                try:
                    self.bot_loop.call_soon_threadsafe(self.bot_loop.stop)
                except Exception as e:
                    print(f"[MAIN] Ошибка call_soon_threadsafe: {e}")

            if self.bot_thread:
                self.bot_thread.join(timeout=2.0)
            print("[MAIN] Бот успешно остановлен.")

        # Запускаем остановку в фоновом потоке, чтобы GUI CustomTkinter намертво не фризило!
        stop_thread = threading.Thread(target=_stop_worker, daemon=True)
        stop_thread.start()

    def run(self):
        """Запуск приложения (CustomTkinter GUI запускается в основном потоке)."""
        app = SoundpadSyncApp(
            db_manager=self.db,
            spl_manager=self.spl,
            start_bot_callback=self.start_bot,
            stop_bot_callback=self.stop_bot
        )
        
        # Запускаем GUI (это блокирующий вызов Tkinter mainloop)
        app.mainloop()
        
        # После закрытия окна останавливаем бота, если он запущен
        self.stop_bot()

if __name__ == "__main__":
    # Убедимся, что папки для данных существуют
    os.makedirs("data", exist_ok=True)
    
    orchestrator = AppOrchestrator()
    orchestrator.run()
