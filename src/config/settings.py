"""
إعدادات التطبيق الرئيسية
"""

import os
from dotenv import load_dotenv
import logging

# تحميل المتغيرات البيئية
load_dotenv()

# إعدادات API
API_ID = int(os.getenv("API_ID", 22439859))
API_HASH = os.getenv("API_HASH", "312858aa733a7bfacf54eede0c275db4")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU")

# إعدادات السورس
SESSION_NAME = "Mnager_V8_Final"
REQUIRED_CHANNEL = "iomk3"
SUPPORT_USER = "iomk0"
ADMIN_USERS = [7259620384]

# مسارات الملفات
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_DIR = os.path.join(DATA_DIR, "databases")
JSON_DIR = os.path.join(DATA_DIR, "json_files")
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# إنشاء المجلدات إذا لم تكن موجودة
for directory in [DATA_DIR, DATABASE_DIR, JSON_DIR, SESSIONS_DIR, ASSETS_DIR]:
    os.makedirs(directory, exist_ok=True)

# مسارات الملفات المحددة
ALLOWED_FILE = os.path.join(JSON_DIR, "allowed_users.json")
SUBSCRIPTIONS_FILE = os.path.join(JSON_DIR, "subscriptions.json")
TRIALS_FILE = os.path.join(JSON_DIR, "trials.json")
ACTIVATION_CODES_FILE = os.path.join(JSON_DIR, "activation_codes.json")
USER_INSTALLATIONS_FILE = os.path.join(JSON_DIR, "user_installations.json")
USER_STATS_FILE = os.path.join(JSON_DIR, "user_stats.json")
REFERRAL_DB = os.path.join(DATABASE_DIR, "referrals.db")

# إعدادات الذكاء الاصطناعي
GEMINI_API_KEY = "AIzaSyD6QwvrvnjU7j-R6fkOghfIVKwtvc7SmLk"
GEMINI_API_URL = "https://firebasevertexai.googleapis.com/v1beta/projects/gemmy-ai-bdc03/locations/us-central1/publishers/google/models/gemini-2.0-flash-lite:generateContent"

# إعدادات نظام الشركاء
COMMISSION_RATES = {
    "bronze": 10,   # 10% للمستوى الأول
    "silver": 15,   # 15% 
    "gold": 20,     # 20%
    "platinum": 30  # 30% للشركاء المميزين
}

INVITEE_REWARDS = {
    "first_invite": {"days": 3, "points": 100},
    "fifth_invite": {"days": 7, "points": 500},
    "tenth_invite": {"days": 30, "points": 1000}
}

TIER_REQUIREMENTS = {
    "bronze": {"invites": 0, "earnings": 0},
    "silver": {"invites": 10, "earnings": 50},
    "gold": {"invites": 50, "earnings": 200},
    "platinum": {"invites": 100, "earnings": 500}
}

# إعدادات التسجيل
def setup_logging():
    """إعداد نظام التسجيل"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(DATA_DIR, "common_bot.log")),
            logging.StreamHandler()
        ]
    )