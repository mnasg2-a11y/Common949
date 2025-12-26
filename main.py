"""
الملف الرئيسي لتشغيل سورس كومن الذكي
"""

import asyncio
import logging
from src.config.settings import setup_logging, API_ID, API_HASH, BOT_TOKEN
from src.utils.logger import get_logger
from src.modules.manager_bot import ManagerBot

logger = get_logger(__name__)

def main():
    """الدالة الرئيسية لتشغيل السورس"""
    try:
        # إعداد التسجيل
        setup_logging()
        
        # التحقق من المتغيرات البيئية
        if not all([API_ID, API_HASH, BOT_TOKEN]):
            logger.error("❌ يرجى تعيين جميع المتغيرات البيئية المطلوبة")
            sys.exit(1)
        
        logger.info("🚀 بدء تشغيل سورس كومن الذكي V8...")
        logger.info("🧠 نظام الذكاء الاصطناعي: مفعّل")
        logger.info("💰 نظام الشركاء: جاهز")
        logger.info("🤖 بوتات التجميع: مفعّل")
        
        # تشغيل البوت الرئيسي
        asyncio.run(run_bot())
        
    except Exception as e:
        logger.error(f"❌ خطأ في التشغيل الرئيسي: {e}")
        sys.exit(1)

async def run_bot():
    """تشغيل البوت بشكل غير متزامن"""
    try:
        manager = ManagerBot()
        await manager.start(bot_token=BOT_TOKEN)
        
        logger.info("✅ تم بدء تشغيل البوت الرئيسي بنجاح")
        logger.info("👨‍💻 المطور: حسين - @iomk0")
        logger.info("📢 القناة: @iomk3")
        logger.info("💰 ابدأ الربح باستخدام: .شركاء")
        
        # تشغيل البوت حتى الإيقاف
        await manager.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")