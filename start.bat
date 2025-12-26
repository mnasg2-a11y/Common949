@echo off
chcp 65001 >nul
echo 🚀 بدء تشغيل سورس كومن الذكي V8

REM التحقق من Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت
    pause
    exit /b 1
)

REM التحقق من الملفات
if not exist "requirements.txt" (
    echo ❌ ملف requirements.txt غير موجود
    pause
    exit /b 1
)

if not exist ".env" (
    echo ⚠️ ملف .env غير موجود، جاري إنشاء نسخة من .env.example
    if exist ".env.example" (
        copy .env.example .env
        echo 📝 يرجى تعديل ملف .env بإعداداتك
        pause
        exit /b 1
    ) else (
        echo ❌ ملف .env.example غير موجود
        pause
        exit /b 1
    )
)

REM تثبيت المكاتب
echo 📦 تثبيت/تحديث المكاتب...
pip install -r requirements.txt --upgrade

REM إنشاء المجلدات
if not exist "data\databases" mkdir "data\databases"
if not exist "data\json_files" mkdir "data\json_files"
if not exist "data\sessions" mkdir "data\sessions"
if not exist "logs" mkdir "logs"

REM تشغيل السورس
echo ⚡ جاري تشغيل السورس...
python run.py

pause