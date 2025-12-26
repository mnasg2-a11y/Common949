"""
مدققو المدخلات
"""

import re
from typing import Optional, Union

def validate_phone(phone: str) -> bool:
    """التحقق من صحة رقم الهاتف"""
    # إزالة المسافات والإشارات
    phone = re.sub(r'[\s+\-()]', '', phone)
    
    # يجب أن يحتوي على أرقام فقط
    if not phone.isdigit():
        return False
    
    # يجب أن يكون الطول بين 8 و 15 رقم
    return 8 <= len(phone) <= 15

def validate_email(email: str) -> bool:
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_url(url: str) -> bool:
    """التحقق من صحة الرابط"""
    pattern = r'^(https?://)?(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(/\S*)?$'
    return bool(re.match(pattern, url))

def validate_username(username: str) -> bool:
    """التحقق من صحة اسم المستخدم"""
    # يجب أن يكون بين 3 و 30 حرف
    if not 3 <= len(username) <= 30:
        return False
    
    # يجب أن يحتوي على أحرف إنجليزية وأرقام وشرطة سفلية فقط
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, username))

def validate_password(password: str) -> tuple[bool, str]:
    """التحقق من قوة كلمة المرور"""
    if len(password) < 8:
        return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل"
    
    if not re.search(r'[A-Z]', password):
        return False, "يجب أن تحتوي على حرف كبير واحد على الأقل"
    
    if not re.search(r'[a-z]', password):
        return False, "يجب أن تحتوي على حرف صغير واحد على الأقل"
    
    if not re.search(r'[0-9]', password):
        return False, "يجب أن تحتوي على رقم واحد على الأقل"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "يجب أن تحتوي على رمز خاص واحد على الأقل"
    
    return True, "كلمة مرور قوية"

def validate_amount(amount: Union[str, int, float]) -> tuple[bool, Optional[float]]:
    """التحقق من صحة المبلغ"""
    try:
        amount_float = float(amount)
        
        if amount_float <= 0:
            return False, None
        
        if amount_float > 1000000:  # مليون كحد أقصى
            return False, None
        
        return True, amount_float
    except (ValueError, TypeError):
        return False, None

def validate_date(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """التحقق من صحة التاريخ"""
    from datetime import datetime
    
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False

def validate_time(time_str: str) -> bool:
    """التحقق من صحة الوقت"""
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$'
    return bool(re.match(pattern, time_str))

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """تنظيف المدخلات من الأحرف الضارة"""
    # إزالة الأحرف الخاصة الخطيرة
    text = re.sub(r'[<>"\'&;]', '', text)
    
    # تقليم النص إذا كان طويلاً
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()

def is_valid_command(command: str) -> bool:
    """التحقق من صحة الأمر"""
    # يجب أن يبدأ بنقطة
    if not command.startswith('.'):
        return False
    
    # يجب أن يحتوي على حروف وأرقام فقط
    command_body = command[1:]  # إزالة النقطة
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, command_body))