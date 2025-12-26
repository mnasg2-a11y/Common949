#!/bin/bash

# سورس كومن الذكي V8 - ملف التشغيل للينكس

echo "🚀 بدء تشغيل سورس كومن الذكي V8"

# التحقق من Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت"
    exit 1
fi

# التحقق من الملفات
if [ ! -f "requirements.txt" ]; then
    echo "❌ ملف requirements.txt غير موجود"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "⚠️ ملف .env غير موجود، جاري إنشاء نسخة من .env.example"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 يرجى تعديل ملف .env بإعداداتك"
        exit 1
    else
        echo "❌ ملف .env.example غير موجود"
        exit 1
    fi
fi

# تثبيت المكاتب
echo "📦 تثبيت/تحديث المكاتب..."
pip3 install -r requirements.txt --upgrade

# إنشاء المجلدات
mkdir -p data/databases data/json_files data/sessions logs

# تشغيل السورس
echo "⚡ جاري تشغيل السورس..."
python3 run.py