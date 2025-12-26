"""
البوت الرئيسي للإدارة والتحكم
"""

import asyncio
from datetime import datetime
from typing import Dict

from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

from src.config.settings import (
    API_ID, API_HASH, BOT_TOKEN, SESSION_NAME,
    REQUIRED_CHANNEL, SUPPORT_USER, ADMIN_USERS
)
from src.modules.subscription import SubscriptionManager
from src.modules.referral_system import AdvancedReferralSystem
from src.modules.userbot import CommonUserBot
from src.utils.logger import get_logger
from src.handlers.commands import CommandHandler
from src.handlers.callbacks import CallbackHandler
from src.handlers.messages import MessageHandler

logger = get_logger(__name__)

class ManagerBot:
    """البوت الرئيسي للإدارة"""
    
    def __init__(self):
        self.client = TelegramClient(
            SESSION_NAME, 
            API_ID, 
            API_HASH,
            connection_retries=None,
            retry_delay=0,
            timeout=10,
            device_model="Common Rocket",
            system_version="Speed 10.0",
            app_version="1.0"
        )
        
        # الأنظمة
        self.subscription_manager = SubscriptionManager()
        self.referral_system = AdvancedReferralSystem()
        self.active_userbots = {}
        
        # المعالجات
        self.command_handler = CommandHandler(self)
        self.callback_handler = CallbackHandler(self)
        self.message_handler = MessageHandler(self)
        
        # الحالات
        self.login_states = {}
        self.waiting_for_admin = {}
        
        logger.info("✅ تم تهيئة البوت الرئيسي")
    
    async def start(self, **kwargs):
        """بدء تشغيل البوت"""
        await self.client.start(bot_token=BOT_TOKEN, **kwargs)
        await self._setup_handlers()
        await self._send_startup_message()
    
    async def _setup_handlers(self):
        """إعداد معالجات الأحداث"""
        # معالجات الأوامر
        self.client.add_event_handler(self._start_command, events.NewMessage(pattern='/start'))
        self.client.add_event_handler(self._admin_command, events.NewMessage(pattern='/admin'))
        self.client.add_event_handler(self._stats_command, events.NewMessage(pattern='/stats'))
        self.client.add_event_handler(self._stop_command, events.NewMessage(pattern='/stop'))
        
        # معالجات الأزرار
        self.client.add_event_handler(self.callback_handler.handle_callbacks, events.CallbackQuery)
        
        # معالجات الرسائل
        self.client.add_event_handler(self.message_handler.handle_messages, events.NewMessage)
        
        logger.info("✅ تم إعداد معالجات الأحداث")
    
    async def _send_startup_message(self):
        """إرسال رسالة بدء التشغيل"""
        startup_msg = """
⚡ سورس كومن الذكي V8 - الإصدار المتكامل

✅ **تم بدء التشغيل بنجاح!**

🧠 **المميزات الرئيسية:**
• ذكاء اصطناعي Gemini المتقدم
• نظام شركاء وإحالة متكامل
• تجميع نقاط تلقائي من بوتات
• إنشاء صور حقيقية بالذكاء الاصطناعي
• إدارة متقدمة للمجموعات والخاص
• أكثر من 300 أمر متاحة

💰 **نظام الربح:**
• عمولات تصل إلى 30% من الإحالات
• لوحة متصدرين وجوائز
• سحب أرباح مباشرة

👨‍💻 **المطور:** حسين - @iomk0
📢 **القناة:** @iomk3
🚀 **ابدأ الربح الآن باستخدام:** `.شركاء`
        """
        
        for admin_id in ADMIN_USERS:
            try:
                await self.client.send_message(admin_id, startup_msg)
            except:
                pass
        
        logger.info("🚀 بدء تشغيل سورس كومن الذكي V8")
    
    async def _start_command(self, event):
        """معالج أمر /start"""
        user_id = event.sender_id
        
        # التحقق من رابط الإحالة
        if event.raw_text and 'start=' in event.raw_text:
            parts = event.raw_text.split()
            for part in parts:
                if 'start=' in part:
                    start_param = part.split('start=')[1]
                    
                    # إذا كان رابط إحالة
                    if start_param.startswith('ref_'):
                        referral_code = start_param[4:]
                        await self._handle_referral(user_id, referral_code, event)
                        return
        
        # التحقق من الاشتراك الإجباري
        if REQUIRED_CHANNEL:
            try:
                await self.client(GetParticipantRequest(
                    channel=REQUIRED_CHANNEL, 
                    participant=user_id
                ))
            except UserNotParticipantError:
                await event.respond(
                    "⚠️ **عذراً، يجب عليك الاشتراك في قناة السورس أولاً.**",
                    buttons=[[Button.url("✅ اشترك الآن", f"https://t.me/{REQUIRED_CHANNEL}")]]
                )
                return
        
        # التحقق من صلاحية المستخدم
        if user_id in ADMIN_USERS:
            await self.command_handler.handle_admin_start(event)
        else:
            await self.command_handler.handle_user_start(event)
    
    async def _handle_referral(self, user_id: int, referral_code: str, event):
        """معالجة رابط الإحالة"""
        result = self.referral_system.track_referral(referral_code, user_id)
        
        if result["success"]:
            # إضافة 3 أيام مجانية
            user_id_str = str(user_id)
            if user_id_str not in self.subscription_manager.trials:
                self.subscription_manager.activate_trial(user_id_str, 3)
            
            await event.respond(
                f"👋 **أهلاً بك في سورس كومن الذكي**\n\n"
                f"🎉 **تم تفعيل التجربة المجانية لمدة 3 أيام باستخدام رابط الإحالة!**\n\n"
                f"💰 **مكافآت الإحالة:**\n"
                f"• 3 أيام مجانية إضافية\n"
                f"• 100 نقطة هدية\n"
                f"• نظام شركاء مفعّل\n\n"
                f"👇 **اختر من القائمة:**",
                buttons=self.callback_handler.user_keyboard()
            )
        else:
            await event.respond(
                f"⚠️ **{result['message']}**\n\n"
                f"👋 أهلاً بك في سورس كومن الذكي!",
                buttons=self.callback_handler.user_keyboard()
            )
    
    async def _admin_command(self, event):
        """معالج أمر /admin"""
        if event.sender_id in ADMIN_USERS:
            await self.command_handler.handle_admin_panel(event)
        else:
            await event.respond('⛔️ ليس لديك صلاحية الوصول الى لوحة الادمن')
    
    async def _stats_command(self, event):
        """معالج أمر /stats"""
        if event.sender_id in ADMIN_USERS:
            await self.command_handler.handle_stats(event)
    
    async def _stop_command(self, event):
        """معالج أمر /stop"""
        await self.command_handler.handle_stop(event)
    
    async def run_until_disconnected(self):
        """تشغيل البوت حتى الإيقاف"""
        await self.client.run_until_disconnected()