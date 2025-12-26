"""
نظام التسجيل المتقدم
"""

import logging
import sys
from datetime import datetime
from typing import Optional

from src.config.settings import DATA_DIR

class ColorFormatter(logging.Formatter):
    """مُنسق الألوان للتسجيل"""
    
    COLORS = {
        'DEBUG': '\033[94m',     # أزرق
        'INFO': '\033[92m',      # أخضر
        'WARNING': '\033[93m',   # أصفر
        'ERROR': '\033[91m',     # أحمر
        'CRITICAL': '\033[95m',  # بنفسجي
        'RESET': '\033[0m'       إعادة الضبط
    }
    
    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            record.msg = f"{self.COLORS[levelname]}{record.msg}{self.COLORS['RESET']}"
        return super().format(record)

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """إعداد مُسجل"""
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(level)
    logger.propagate = False
    
    # معالج وحدة التحكم
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    console_formatter = ColorFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # معالج الملفات
    try:
        log_file = f"{DATA_DIR}/common_bot.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Failed to setup file handler: {e}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """الحصول على مُسجل"""
    return setup_logger(name)

class BotLogger:
    """مسجل مخصص للبوت"""
    
    def __init__(self, name: str = "CommonBot"):
        self.logger = get_logger(name)
        self.name = name
    
    def info(self, message: str, **kwargs):
        """تسجيل معلومات"""
        self.logger.info(f"{self.name}: {message}", **kwargs)
    
    def error(self, message: str, **kwargs):
        """تسجيل خطأ"""
        self.logger.error(f"{self.name}: {message}", **kwargs)
    
    def warning(self, message: str, **kwargs):
        """تسجيل تحذير"""
        self.logger.warning(f"{self.name}: {message}", **kwargs)
    
    def debug(self, message: str, **kwargs):
        """تسجيل تصحيح"""
        self.logger.debug(f"{self.name}: {message}", **kwargs)
    
    def critical(self, message: str, **kwargs):
        """تسجيل حرج"""
        self.logger.critical(f"{self.name}: {message}", **kwargs)