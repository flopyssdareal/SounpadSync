import os
import ctypes
import subprocess
from typing import List, Dict, Optional

class SoundpadAPIManager:
    r"""
    Класс для управления Soundpad через Named Pipes (Windows Named Pipe Developer API)
    по адресу \\.\pipe\sp_remote_control.
    """
    def __init__(self, spl_path: str = ""):
        # Для обратной совместимости сохраняем spl_path, хотя он больше не используется
        self.spl_path = spl_path

    def _connect_to_pipe(self):
        """Пытается подключиться к именованному каналу Soundpad с поддержкой ожидания и ретраев."""
        if os.name != 'nt':
            return None, "Error: Soundpad API works only on Windows."
            
        pipe_name = r"\\.\pipe\sp_remote_control"
        
        # Настройка ctypes типов для корректной работы на 64-битных и 32-битных системах
        try:
            # Настраиваем CreateFileW
            ctypes.windll.kernel32.CreateFileW.argtypes = [
                ctypes.c_wchar_p,     # lpFileName
                ctypes.c_ulong,       # dwDesiredAccess
                ctypes.c_ulong,       # dwShareMode
                ctypes.c_void_p,      # lpSecurityAttributes
                ctypes.c_ulong,       # dwCreationDisposition
                ctypes.c_ulong,       # dwFlagsAndAttributes
                ctypes.c_void_p       # hTemplateFile
            ]
            ctypes.windll.kernel32.CreateFileW.restype = ctypes.c_void_p # HANDLE (64-bit safe)
            
            # Настраиваем CloseHandle
            ctypes.windll.kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
            ctypes.windll.kernel32.CloseHandle.restype = ctypes.c_long
            
            # Настраиваем WaitNamedPipeW
            ctypes.windll.kernel32.WaitNamedPipeW.argtypes = [ctypes.c_wchar_p, ctypes.c_ulong]
            ctypes.windll.kernel32.WaitNamedPipeW.restype = ctypes.c_long
        except Exception:
            pass

        GENERIC_READ = 0x80000000
        GENERIC_WRITE = 0x40000000
        OPEN_EXISTING = 3
        FILE_ATTRIBUTE_NORMAL = 0x80
        
        for attempt in range(5):
            handle = ctypes.windll.kernel32.CreateFileW(
                pipe_name,
                GENERIC_READ | GENERIC_WRITE,
                0, None,
                OPEN_EXISTING,
                FILE_ATTRIBUTE_NORMAL,
                None
            )
            
            # В ctypes.c_void_p INVALID_HANDLE_VALUE может быть 0xFFFFFFFFFFFFFFFF (на 64-bit) или 0xFFFFFFFF (на 32-bit), или -1
            if handle is not None and handle != 0 and handle != 0xFFFFFFFFFFFFFFFF and handle != 0xFFFFFFFF and handle != -1:
                return handle, None
                
            err = ctypes.windll.kernel32.GetLastError()
            if err == 231: # ERROR_PIPE_BUSY
                # Ждем освобождения канала до 1 секунды
                if ctypes.windll.kernel32.WaitNamedPipeW(pipe_name, 1000):
                    continue
            
            # Если это не занятость канала, возвращаем ошибку
            err_desc = ""
            if err == 2:
                err_desc = (
                    "Soundpad не запущен или API отключен (Pipe not found / Error 2).\n\n"
                    "Пожалуйста, проверьте следующие настройки:\n"
                    "1. Убедитесь, что программа Soundpad ЗАПУЩЕНА.\n"
                    "2. Откройте в Soundpad меню: Файл -> Настройки -> вкладка «Разработчикам» (File -> Preferences -> Developer) "
                    "и убедитесь, что включена галочка «Включить API разработчика» (Enable developer API).\n"
                    "3. Если вы запускаете Soundpad от имени Администратора (чтобы клавиши работали в играх), "
                    "то эту программу синхронизации ТОЖЕ ОБЯЗАТЕЛЬНО нужно запускать от имени Администратора.\n"
                    "4. В Soundpad также рекомендуется зайти в меню: Файл -> Настройки -> вкладка «Удаленное управление» (Remote Control) и "
                    "включить его."
                )
            elif err == 5:
                err_desc = (
                    "Доступ ограничен (Access denied / Error 5).\n\n"
                    "Пожалуйста, запустите обе программы на ОДНОМ уровне прав:\n"
                    "либо ОБЕ от имени Администратора (и Soundpad, и эту утилиту),\n"
                    "либо ОБЕ от имени обычного пользователя."
                )
            elif err == 231:
                err_desc = "Soundpad pipe is busy."
            else:
                err_desc = f"Failed to open pipe (Windows Error Code {err})."
                
            return None, err_desc
            
        return None, "Error: Soundpad pipe is busy after retries."

    def is_soundpad_running(self) -> bool:
        """Проверяет, запущен ли Soundpad на Windows (включая Steam-версию)."""
        if os.name != 'nt':
            return False
        
        # 1. Сначала проверяем наличие процесса Soundpad.exe через tasklist
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.check_output(
                ['tasklist', '/FI', 'IMAGENAME eq Soundpad.exe', '/NH'],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW,
                text=True,
                errors='ignore'
            )
            if "soundpad.exe" in output.lower():
                return True
        except Exception:
            pass
            
        # 2. Если процесс не найден (или нет доступа к tasklist), пробуем подключиться к каналу
        # Но чтобы не занимать канал надолго, просто пытаемся открыть его и тут же закрываем.
        try:
            handle, err_desc = self._connect_to_pipe()
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                return True
            # Если вернулась ошибка Access Denied или Pipe Busy, значит канал существует, но мы не смогли подключиться прямо сейчас
            if err_desc and ("Access denied" in err_desc or "busy" in err_desc):
                return True
        except Exception:
            pass
            
        return False

    def send_command(self, command_str: str) -> str:
        """Отправляет текстовую команду напрямую в Soundpad через Named Pipe sp_remote_control."""
        if os.name != 'nt':
            return "Error: Soundpad API works only on Windows."
            
        handle, err_desc = self._connect_to_pipe()
        if not handle:
            return f"Error: {err_desc}"
            
        try:
            # Настраиваем WriteFile и ReadFile для надежности
            try:
                ctypes.windll.kernel32.WriteFile.argtypes = [
                    ctypes.c_void_p,      # hFile
                    ctypes.c_void_p,      # lpBuffer
                    ctypes.c_ulong,       # nNumberOfBytesToWrite
                    ctypes.POINTER(ctypes.c_ulong), # lpNumberOfBytesWritten
                    ctypes.c_void_p       # lpOverlapped
                ]
                ctypes.windll.kernel32.WriteFile.restype = ctypes.c_long
                
                ctypes.windll.kernel32.ReadFile.argtypes = [
                    ctypes.c_void_p,      # hFile
                    ctypes.c_void_p,      # lpBuffer
                    ctypes.c_ulong,       # nNumberOfBytesToRead
                    ctypes.POINTER(ctypes.c_ulong), # lpNumberOfBytesRead
                    ctypes.c_void_p       # lpOverlapped
                ]
                ctypes.windll.kernel32.ReadFile.restype = ctypes.c_long
            except Exception:
                pass

            # ВАЖНО: Soundpad - нативное Windows-приложение (Delphi), оно читает команды
            # из пайпа в системной ANSI-кодировке (на русской Windows это cp1251),
            # а НЕ в UTF-8. Если отправлять путь с кириллицей как UTF-8, Soundpad
            # декодирует байты неправильно и получает "мусорный" путь, которого не
            # существует на диске -> "R-204: File does not exist", хотя файл на месте.
            try:
                cmd_bytes = command_str.encode('mbcs')
            except (UnicodeEncodeError, LookupError):
                # 'mbcs' существует только на Windows; на случай, если какой-то
                # символ не влезает в текущую ANSI-кодовую страницу, подстраховываемся.
                cmd_bytes = command_str.encode('utf-8', errors='ignore')
            written = ctypes.c_ulong(0)
            ctypes.windll.kernel32.WriteFile(
                handle,
                cmd_bytes,
                len(cmd_bytes),
                ctypes.byref(written),
                None
            )

            # Читаем ответ от Soundpad (буфер увеличен до 1 МБ для корректного чтения XML со списком звуков)
            buf_size = 1024 * 1024
            buf = ctypes.create_string_buffer(buf_size)
            read_bytes = ctypes.c_ulong(0)
            ctypes.windll.kernel32.ReadFile(
                handle,
                buf,
                buf_size,
                ctypes.byref(read_bytes),
                None
            )

            ctypes.windll.kernel32.CloseHandle(handle)
            try:
                return buf.value.decode('mbcs', errors='ignore').strip()
            except LookupError:
                return buf.value.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            try:
                ctypes.windll.kernel32.CloseHandle(handle)
            except Exception:
                pass
            return f"Error during I/O: {e}"

    def is_trial(self) -> bool:
        """Проверяет, является ли запущенная версия Soundpad триальной (IsTrial())."""
        if not self.is_soundpad_running():
            return False
            
        response = self.send_command("IsTrial()")
        print(f"[Soundpad API] Response for IsTrial(): {response}")
        
        if "Error" in response:
            return False
            
        # Если ответ содержит "true" или "1" (после R-200)
        resp_lower = response.lower()
        if "true" in resp_lower or "1" in resp_lower:
            return True
            
        return False

    def get_categories_from_api(self) -> List[str]:
        """Получает список категорий напрямую из Soundpad по API с помощью GetSoundList()."""
        if not self.is_soundpad_running():
            return ["Разное", "Мемы", "Музыка", "Аниме", "Игры", "Фильмы"]
            
        xml_str = self.send_command("GetSoundList()")
        if not xml_str or "Error" in xml_str:
            return ["Разное", "Мемы", "Музыка", "Аниме", "Игры", "Фильмы"]
            
        # Убираем R-200, если он есть в начале
        if xml_str.startswith("R-200"):
            parts = xml_str.split("\n", 1)
            if len(parts) > 1:
                xml_str = parts[1].strip()
            else:
                xml_str = ""
                
        if not xml_str.startswith("<"):
            # Попробуем найти начало XML тега
            idx = xml_str.find("<")
            if idx != -1:
                xml_str = xml_str[idx:]
            else:
                return ["Разное", "Мемы", "Музыка", "Аниме", "Игры", "Фильмы"]
                
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_str)
            categories = []
            for cat in root.iter("Category"):
                name = cat.get("name") or cat.get("title")
                if name:
                    categories.append(name)
            if categories:
                # Добавим "Разное" (Miscellaneous), если его нет
                default_cat = "Разное"
                if default_cat not in categories:
                    categories.insert(0, default_cat)
                return categories
        except Exception as e:
            print(f"[Soundpad API] Ошибка парсинга категорий из XML: {e}")
            
        return ["Разное", "Мемы", "Музыка", "Аниме", "Игры", "Фильмы"]

    def _get_category_index(self, category_name: str) -> Optional[int]:
        """Находит числовой индекс категории по её названию через GetSoundList()."""
        if not category_name:
            return None
            
        xml_str = self.send_command("GetSoundList()")
        if not xml_str or "Error" in xml_str:
            return None
            
        # Очищаем XML
        if xml_str.startswith("R-200"):
            parts = xml_str.split("\n", 1)
            if len(parts) > 1:
                xml_str = parts[1].strip()
            else:
                xml_str = ""
                
        if not xml_str.startswith("<"):
            idx = xml_str.find("<")
            if idx != -1:
                xml_str = xml_str[idx:]
            else:
                return None
                
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_str)
            for cat in root.iter("Category"):
                name = cat.get("name") or cat.get("title")
                if name and name.lower() == category_name.lower():
                    # Индекс категории может быть в "index" или "id"
                    cat_index = cat.get("index") or cat.get("id")
                    if cat_index is not None:
                        return int(cat_index)
        except Exception as e:
            print(f"[Soundpad API] Ошибка получения индекса категории: {e}")
            
        return None

    def get_categories(self) -> List[str]:
        """Возвращает список категорий для GUI (динамически запрашивая Soundpad)."""
        return self.get_categories_from_api()

    def get_all_tracks(self) -> List[Dict[str, str]]:
        """Больше не считываем файлы .spl вручную."""
        return []

    def create_backup(self) -> str:
        return ""

    def add_sound(self, file_path: str, title: str = "", category_name: Optional[str] = None) -> bool:
        r"""
        Добавляет звуковой файл в плейлист Soundpad по API.
        Пытается получить числовой индекс категории по имени через GetSoundList().
        Если индекс найден, использует: DoAddSound("filePath", categoryIndex)
        Иначе использует: DoAddSound("filePath")
        """
        if not self.is_soundpad_running():
            print("[Soundpad API] Ошибка: Soundpad не запущен.")
            return False

        normalized_path = os.path.abspath(file_path)
        
        # Сначала проверим IsTrial() для предотвращения случайных ошибок
        try:
            trial_status = self.is_trial()
            print(f"[Soundpad API] Trial status: {trial_status}")
        except Exception as e:
            print(f"[Soundpad API] Error checking IsTrial: {e}")
            
        category_index = None
        if category_name:
            try:
                category_index = self._get_category_index(category_name)
                print(f"[Soundpad API] Found category '{category_name}' index: {category_index}")
            except Exception as e:
                print(f"[Soundpad API] Error getting category index: {e}")
                
        # Формируем команду DoAddSound
        # ВАЖНО: у DoAddSound(url, index) второй параметр — это позиция вставки
        # в общем списке, а НЕ индекс категории. Чтобы добавить звук именно
        # в нужную категорию, нужна трёхаргументная форма:
        # DoAddSound(url, categoryIndex, insertAtPosition), где -1 = в конец категории.
        if category_index is not None:
            cmd = f'DoAddSound("{normalized_path}", {category_index}, -1)'
        else:
            cmd = f'DoAddSound("{normalized_path}")'
            
        print(f"[Soundpad API] Sending command: {cmd}")
        response = self.send_command(cmd)
        print(f"[Soundpad API] Response for DoAddSound: {response}")
        
        # Проверяем успешность ответа (должен начинаться на R-200)
        if "Error" in response or (response and not response.startswith("R-200")):
            # Попробуем резервный вариант do add sound
            fallback_cmd = f'do add sound("{normalized_path}")'
            print(f"[Soundpad API] Fallback: Sending legacy command: {fallback_cmd}")
            fb_response = self.send_command(fallback_cmd)
            print(f"[Soundpad API] Response for legacy command: {fb_response}")
            if "Error" in fb_response or (fb_response and not fb_response.startswith("R-200")):
                return False
                
        return True

# Алиас для обратной совместимости
SoundpadSPLManager = SoundpadAPIManager
