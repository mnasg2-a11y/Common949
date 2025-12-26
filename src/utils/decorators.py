"""
ديكورات مساعدة
"""

import asyncio
import functools
import time
from typing import Callable, Any, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)

def rate_limit(requests_per_minute: int = 60):
    """تقييد معدل الطلبات"""
    def decorator(func: Callable) -> Callable:
        last_called = [0.0]
        min_interval = 60.0 / requests_per_minute
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
            last_called[0] = time.time()
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """إعادة المحاولة عند الفشل"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"فشلت جميع محاولات {func.__name__}: {e}")
                        raise
                    
                    logger.warning(f"محاولة {attempt + 1} فشلت لـ {func.__name__}: {e}")
                    await asyncio.sleep(delay * (attempt + 1))  # زيادة التأخير تدريجياً
            
            return None
        
        return wrapper
    return decorator

def admin_only(func: Callable) -> Callable:
    """الديكور للأدمن فقط"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        from src.config.settings import ADMIN_USERS
        
        # استخراج معرف المستخدم من الوسائط
        event = args[0] if args else None
        
        if hasattr(event, 'sender_id'):
            user_id = event.sender_id
            
            if user_id not in ADMIN_USERS:
                await event.respond("⛔️ هذا الأمر مخصص للإدارة فقط")
                return None
        
        return await func(*args, **kwargs)
    
    return wrapper

def subscription_required(func: Callable) -> Callable:
    """الديكور للمشتركين فقط"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        from src.modules.subscription import SubscriptionManager
        
        # استخراج معرف المستخدم من الوسائط
        event = args[0] if args else None
        
        if hasattr(event, 'sender_id'):
            user_id = event.sender_id
            subscription_manager = SubscriptionManager()
            sub_status = subscription_manager.check_subscription(str(user_id))
            
            if not sub_status["active"]:
                await event.respond(
                    "⚠️ **ليس لديك اشتراك نشط.**\n"
                    "يرجى شراء اشتراك أو استخدام التجربة المجانية."
                )
                return None
        
        return await func(*args, **kwargs)
    
    return wrapper

def handle_errors(func: Callable) -> Callable:
    """معالجة الأخطاء"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"خطأ في {func.__name__}: {e}")
            
            # محاولة إرسال رسالة خطأ
            event = args[0] if args else None
            if event and hasattr(event, 'respond'):
                try:
                    await event.respond(f"❌ **حدث خطأ:** {str(e)}")
                except:
                    pass
            
            return None
    
    return wrapper

def log_execution_time(func: Callable) -> Callable:
    """تسجيل وقت التنفيذ"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.debug(f"{func.__name__} تنفيذ خلال {execution_time:.2f} ثانية")
        
        return result
    
    return wrapper

def cache_result(ttl: int = 300):  # 5 دقائق افتراضياً
    """تخزين النتائج مؤقتاً"""
    cache = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # إنشاء مفتاح فريد من الوسائط
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            if key in cache:
                cached_data, timestamp = cache[key]
                
                if time.time() - timestamp < ttl:
                    logger.debug(f"استرجاع {func.__name__} من الكاش")
                    return cached_data
            
            # تنفيذ الدالة وتخزين النتيجة
            result = await func(*args, **kwargs)
            cache[key] = (result, time.time())
            
            return result
        
        return wrapper
    return decorator