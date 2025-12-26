"""
دوال مساعدة عامة
"""

import os
import json
import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

def load_json_file(file_path: str) -> Dict:
    """تحميل ملف JSON"""
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_json_file(file_path: str, data: Dict):
    """حفظ ملف JSON"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"Failed to save JSON file: {e}")

def generate_random_string(length: int = 8) -> str:
    """إنشاء سلسلة عشوائية"""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

def format_time_delta(delta: timedelta) -> str:
    """تنسيق الفارق الزمني"""
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days} يوم {hours} ساعة"
    elif hours > 0:
        return f"{hours} ساعة {minutes} دقيقة"
    elif minutes > 0:
        return f"{minutes} دقيقة {seconds} ثانية"
    else:
        return f"{seconds} ثانية"

def format_currency(amount: float) -> str:
    """تنسيق المبالغ المالية"""
    return f"${amount:,.2f}"

def safe_int(value: Any, default: int = 0) -> int:
    """تحويل آمن إلى عدد صحيح"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """تحويل آمن إلى عدد عشري"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def truncate_text(text: str, max_length: int = 100) -> str:
    """تقليم النص إذا كان طويلاً"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def get_current_date() -> str:
    """الحصول على التاريخ الحالي"""
    return datetime.now().strftime("%Y-%m-%d")

def get_current_time() -> str:
    """الحصول على الوقت الحالي"""
    return datetime.now().strftime("%H:%M:%S")

def is_valid_phone_number(phone: str) -> bool:
    """التحقق من رقم الهاتف"""
    # إزالة المسافات والإشارات
    phone = phone.replace(" ", "").replace("+", "").replace("-", "")
    
    # يجب أن يحتوي على أرقام فقط
    if not phone.isdigit():
        return False
    
    # يجب أن يكون الطول معقولاً
    return 8 <= len(phone) <= 15

def create_progress_bar(percentage: float, length: int = 10) -> str:
    """إنشاء شريط تقدم"""
    filled = int(percentage / 100 * length)
    empty = length - filled
    bar = "🟩" * filled + "⬜" * empty
    return f"{bar} {percentage:.1f}%"