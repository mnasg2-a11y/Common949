"""
اتصال قاعدة البيانات
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional

from src.config.settings import REFERRAL_DB
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseConnection:
    """مدير اتصال قاعدة البيانات"""
    
    def __init__(self, db_path: str = REFERRAL_DB):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """إنشاء اتصال جديد"""
        try:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
            logger.info(f"✅ تم الاتصال بقاعدة البيانات: {self.db_path}")
            return self._connection
        except sqlite3.Error as e:
            logger.error(f"❌ فشل الاتصال بقاعدة البيانات: {e}")
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """الحصول على الاتصال الحالي"""
        if self._connection is None:
            return self.connect()
        return self._connection
    
    def close(self):
        """إغلاق الاتصال"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("✅ تم إغلاق اتصال قاعدة البيانات")
    
    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """الحصول على مؤشر مع إدارة السياق"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ خطأ في قاعدة البيانات: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """تنفيذ استعلام والحصول على النتائج"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """تنفيذ تحديث والحصول على عدد الصفوف المتأثرة"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def create_tables(self):
        """إنشاء الجداول الأساسية"""
        queries = [
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subscription_type TEXT NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'active',
                payment_amount REAL,
                payment_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER NOT NULL,
                referred_id INTEGER NOT NULL,
                referral_code TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                commission_amount REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users (id),
                FOREIGN KEY (referred_id) REFERENCES users (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                source TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_string TEXT NOT NULL,
                device_info TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            '''
        ]
        
        try:
            with self.get_cursor() as cursor:
                for query in queries:
                    cursor.execute(query)
            logger.info("✅ تم إنشاء جداول قاعدة البيانات")
        except sqlite3.Error as e:
            logger.error(f"❌ فشل إنشاء الجداول: {e}")
            raise
    
    def backup_database(self, backup_path: str):
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"✅ تم إنشاء نسخة احتياطية في: {backup_path}")
        except Exception as e:
            logger.error(f"❌ فشل إنشاء نسخة احتياطية: {e}")

# إنشاء اتصال افتراضي
db_connection = DatabaseConnection()