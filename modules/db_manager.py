import sqlite3
import os
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """
    Класс для управления локальной базой данных SQLite.
    Хранит очередь загруженных из бота треков и общие настройки приложения.
    """
    def __init__(self, db_path: str = "app_data.db"):
        self.db_path = os.path.expanduser(db_path)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Позволяет обращаться к полям по имени
        return conn

    def _init_db(self) -> None:
        """Создает таблицы базы данных, если они отсутствуют."""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица очереди треков
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tik_tok_url TEXT NOT NULL,
                    mp3_path TEXT NOT NULL,
                    description TEXT,
                    predicted_category TEXT,
                    confirmed_category TEXT,
                    status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_at TIMESTAMP
                )
            """)
            
            # Таблица настроек (Key-Value)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    # --- РАБОТА С ОЧЕРЕДЬЮ ТРЕКОВ ---

    def add_track_to_queue(self, tik_tok_url: str, mp3_path: str, description: str, predicted_category: str) -> int:
        """Добавляет новый трек в очередь со статусом 'pending'."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tracks (tik_tok_url, mp3_path, description, predicted_category)
                VALUES (?, ?, ?, ?)
            """, (tik_tok_url, mp3_path, description, predicted_category))
            conn.commit()
            return cursor.lastrowid

    def get_pending_tracks(self) -> List[Dict[str, Any]]:
        """Возвращает список всех треков, ожидающих утверждения пользователя."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tracks WHERE status = 'pending' ORDER BY id ASC")
            return [dict(row) for row in cursor.fetchall()]

    def approve_track(self, track_id: int, confirmed_category: str, new_path: Optional[str] = None) -> bool:
        """Утверждает трек, обновляет категорию, итоговый путь и меняет статус на 'approved'."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if new_path:
                cursor.execute("""
                    UPDATE tracks 
                    SET confirmed_category = ?, mp3_path = ?, status = 'approved', approved_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (confirmed_category, new_path, track_id))
            else:
                cursor.execute("""
                    UPDATE tracks 
                    SET confirmed_category = ?, status = 'approved', approved_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (confirmed_category, track_id))
            conn.commit()
            return cursor.rowcount > 0

    def reject_track(self, track_id: int) -> bool:
        """Отклоняет трек (удаляет из активной очереди / ставит статус 'rejected')."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tracks SET status = 'rejected' WHERE id = ?", (track_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_track_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Возвращает историю обработанных (утвержденных/отклоненных) треков."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tracks 
                WHERE status IN ('approved', 'rejected') 
                ORDER BY approved_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # --- РАБОТА С НАСТРОЙКАМИ ---

    def set_setting(self, key: str, value: str) -> None:
        """Сохраняет настройку по ключу."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (key, value) 
                VALUES (?, ?) 
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, value))
            conn.commit()

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Получает значение настройки по ключу."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default
