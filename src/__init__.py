"""
سورس كومن الذكي V8 - الحزمة الرئيسية
"""

__version__ = "8.0.0"
__author__ = "حسين - @iomk0"
__email__ = "iomk0@telegram"
__description__ = "سورس كومن الذكي V8 - الإصدار المتكامل بالذكاء الاصطناعي ونظام الشركاء"

# تصدير الموديولات الرئيسية
__all__ = [
    'config',
    'modules', 
    'handlers',
    'database',
    'utils'
]

# يمكنك استيراد الموديولات الرئيسية مباشرة
from .config import settings, constants
from .modules import (
    GeminiAI, 
    AdvancedReferralSystem, 
    CommonUserBot, 
    SubscriptionManager, 
    ManagerBot
)
from .handlers import CommandHandler, CallbackHandler, MessageHandler
from .database import DatabaseConnection, User, Subscription, Referral
from .utils import helpers, logger, validators, decorators

# رسالة تحميل
import sys
if not hasattr(sys, 'ps1'):  # إذا كان التشغيل ليس تفاعلياً
    print(f"✅ تم تحميل سورس كومن الذكي {__version__}")
    print(f"👨‍💻 المطور: {__author__}")
    print(f"📝 {__description__}")
