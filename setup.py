"""
ملف الإعداد لتثبيت السورس
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """التحقق من إصدار Python"""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"❌ تحتاج إلى Python {required_version[0]}.{required_version[1]} أو أعلى")
        print(f"   الإصدار الحالي: {current_version[0]}.{current_version[1]}.{current_version[2]}")
        sys.exit(1)
    
    print(f"✅ إصدار Python: {current_version[0]}.{current_version[1]}.{current_version[2]}")

def install_dependencies():
    """تثبيت المكاتب المطلوبة"""
    print("📦 تثبيت المكاتب المطلوبة...")
    
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print("❌ ملف requirements.txt غير موجود")
        sys.exit(1)
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("✅ تم تثبيت المكاتب بنجاح")
    except subprocess.CalledProcessError as e:
        print(f"❌ فشل تثبيت المكاتب: {e}")
        sys.exit(1)

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    directories = [
        "data/databases",
        "data/json_files",
        "data/sessions",
        "assets/images",
        "assets/videos",
        "assets/docs",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ تم إنشاء مجلد: {directory}")

def setup_environment():
    """إعداد ملف البيئة"""
    env_example = ".env.example"
    env_file = ".env"
    
    if not os.path.exists(env_example):
        print("❌ ملف .env.example غير موجود")
        sys.exit(1)
    
    if not os.path.exists(env_file):
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ تم إنشاء ملف .env")
        print("📝 يرجى تعديل ملف .env بإعداداتك")
    else:
        print("ℹ️ ملف .env موجود بالفعل")

def setup_database():
    """إعداد قاعدة البيانات"""
    from src.database.connection import db_connection
    
    try:
        db_connection.create_tables()
        print("✅ تم إعداد قاعدة البيانات")
    except Exception as e:
        print(f"❌ فشل إعداد قاعدة البيانات: {e}")
        sys.exit(1)

def show_welcome_message():
    """عرض رسالة الترحيب"""
    print("\n" + "="*50)
    print("🎉 تم إعداد سورس كومن الذكي V8 بنجاح!")
    print("="*50)
    print("\n🚀 **كيفية التشغيل:**")
    print("1. قم بتعديل ملف .env بإعداداتك")
    print("2. قم بتشغيل السورس:")
    print("   python run.py")
    print("\n💰 **لبدء الربح:**")
    print("1. ابدأ البوت واكتب /start")
    print("2. استخدم .شركاء لنظام الربح")
    print("3. استخدم .احالة للحصول على رابط الإحالة")
    print("\n🧠 **للذكاء الاصطناعي:**")
    print("1. استخدم .سؤال للأسئلة الذكية")
    print("2. استخدم .اصنع صورة لإنشاء صور")
    print("3. استخدم .اكتب كود لكتابة أكواد")
    print("\n👨‍💻 **المطور:** حسين - @iomk0")
    print("📢 **القناة:** @iomk3")
    print("="*50)

def main():
    """الدالة الرئيسية"""
    print("🛠️ إعداد سورس كومن الذكي V8")
    print("="*50)
    
    # التحقق من الإصدار
    check_python_version()
    
    # تثبيت المكاتب
    install_dependencies()
    
    # إنشاء المجلدات
    create_directories()
    
    # إعداد البيئة
    setup_environment()
    
    # إعداد قاعدة البيانات
    setup_database()
    
    # رسالة الترحيب
    show_welcome_message()

if __name__ == "__main__":
    main()