#!/usr/bin/env python3
"""
سورس كومن الذكي V8 - ملف التشغيل الرئيسي
الإصدار المتكامل مع الذكاء الاصطناعي ونظام الشركاء
"""

import sys
import os

# إضافة المسار الحالي إلى sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ تم إيقاف السورس بواسطة المستخدم")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        sys.exit(1)