# run.py - الملف الرئيسي البسيط
print("🚀 جاري تشغيل سورس كومن...")

# 1. أولاً: نطلب من المستخدم إدخال API
print("\n📱 نحتاج لبعض المعلومات من my.telegram.org:")

api_id = input("• أدخل API ID: ").strip()
api_hash = input("• أدخل API HASH: ").strip()
bot_token = input("• أدخل BOT TOKEN (من @BotFather): ").strip()

print(f"\n✅ تم الحفظ:")
print(f"API ID: {api_id}")
print(f"API HASH: {api_hash[:10]}...")
print(f"BOT TOKEN: {bot_token[:20]}...")

# 2. حفظ المعلومات في ملف .env
with open('.env', 'w', encoding='utf-8') as f:
    f.write(f'''API_ID={api_id}
API_HASH={api_hash}
BOT_TOKEN={bot_token}
SESSION_NAME=Common_V8
REQUIRED_CHANNEL=iomk3
SUPPORT_USER=iomk0
ADMIN_IDS=7259620384
''')

print("\n✅ تم حفظ الإعدادات في ملف .env")

# 3. الآن ننشئ السورس الأساسي
print("\n⚡ جاري إنشاء السورس...")

# إنشاء المجلدات
import os
os.makedirs('data/json_files', exist_ok=True)

# إنشاء ملفات JSON الفارغة
import json
json_files = {
    'allowed_users.json': [],
    'subscriptions.json': {},
    'trials.json': {},
    'activation_codes.json': {},
    'user_installations.json': {},
    'user_stats.json': {"total_users":0,"today_users":0,"last_reset":"2024-01-01"}
}

for filename, content in json_files.items():
    with open(f'data/json_files/{filename}', 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2)
    print(f"✅ تم إنشاء: data/json_files/{filename}")

print("\n🎉 تم تجهيز السورس!")
print("🚀 الآن سنربطه بحسابك...")
