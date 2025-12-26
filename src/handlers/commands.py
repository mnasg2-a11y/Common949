"""
معالج الأوامر للبوت الرئيسي
"""

from datetime import datetime
from typing import Dict

from telethon import events, Button
from telethon.sessions import StringSession

from src.config.settings import ADMIN_USERS
from src.utils.logger import get_logger

logger = get_logger(__name__)

class CommandHandler:
    """معالج الأوامر"""
    
    def __init__(self, manager_bot):
        self.manager = manager_bot
    
    async def handle_admin_start(self, event):
        """معالجة بدء الأدمن"""
        user_id = event.sender_id
        
        admin_info = f'''
**🛠 لوحة التحكم الخاصة بالأدمن**

👤 المعرف: `{user_id}`
🧠 الذكاء الاصطناعي: نشط
🤝 نظام الشركاء: مفعّل
📊 عدد المستخدمين النشطين: {len(self.manager.active_userbots)}
👥 إجمالي المستخدمين: {self._get_total_users()}
📈 مستخدمين اليوم: {self._get_today_users()}

👇 **اختر الخيار المناسب:**
'''
        await event.respond(admin_info, buttons=self._admin_keyboard())
    
    async def handle_user_start(self, event):
        """معالجة بدء المستخدم"""
        user_id = event.sender_id
        
        # التحقق من الاشتراك
        sub_status = self.manager.subscription_manager.check_subscription(user_id)
        
        if not sub_status["active"]:
            # تفعيل تجربة مجانية
            self.manager.subscription_manager.activate_trial(str(user_id), 3)
            sub_status = self.manager.subscription_manager.check_subscription(user_id)
        
        if sub_status["active"]:
            # الحصول على إحصائيات الشريك
            partner_stats = self.manager.referral_system.get_partner_stats(user_id)
            partner_info = ""
            if "error" not in partner_stats:
                partner_info = f"\n🤝 **إحصائيات الشريك:**\n"
                partner_info += f"• المستوى: {partner_stats['tier']}\n"
                partner_info += f"• الإحالات: {partner_stats['total_invites']}\n"
                partner_info += f"• الأرباح: ${partner_stats['total_earnings']:.2f}\n"
            
            await event.respond(
                f"👋 **أهلاً بك في سورس كومن الذكي**\n\n"
                f"✅ **لديك اشتراك نشط:**\n"
                f"📊 **النوع:** {sub_status['type']}\n"
                f"⏳ **الأيام المتبقية:** {sub_status['days_left']}\n"
                f"🧠 **الذكاء الاصطناعي:** مفعّل\n"
                f"{partner_info}\n"
                f"👇 **اختر من القائمة:**",
                buttons=self._user_keyboard()
            )
        else:
            await event.respond(
                "👋 **أهلاً بك في سورس كومن الذكي**\n\n"
                "⚠️ **لقد انتهت تجربتك المجانية.**\n"
                "🧠 **الذكاء الاصطناعي:** جاهز\n"
                "🤝 **نظام الشركاء:** جاهز للربح\n"
                "📅 **يمكنك الاشتراك الآن للحصول على السورس:**",
                buttons=self._user_keyboard()
            )
    
    async def handle_admin_panel(self, event):
        """معالجة لوحة الأدمن"""
        user_id = event.sender_id
        
        admin_info = f'''
**🛠 لوحة التحكم الخاصة بالأدمن**

👤 المعرف: `{user_id}`
🧠 الذكاء الاصطناعي: نشط
🤝 نظام الشركاء: مفعّل
📊 عدد المستخدمين النشطين: {len(self.manager.active_userbots)}
👥 إجمالي المستخدمين: {self._get_total_users()}
📈 مستخدمين اليوم: {self._get_today_users()}

👇 **اختر الخيار المناسب:**
'''
        await event.respond(admin_info, buttons=self._admin_keyboard())
    
    async def handle_stats(self, event):
        """معالجة إحصائيات النظام"""
        stats_info = f'''
**📊 الإحصائيات الحالية:**

🧠 الذكاء الاصطناعي: نشط
🤝 نظام الشركاء: مفعّل
👥 المستخدمين النشطين: {len(self.manager.active_userbots)}
👤 إجمالي المستخدمين: {self._get_total_users()}
📈 مستخدمين اليوم: {self._get_today_users()}

💰 المدفوعين: {len(self.manager.subscription_manager.subscriptions)}
🎫 التجارب: {len(self.manager.subscription_manager.trials)}
👮‍♂️ الادمنية: {len(ADMIN_USERS)}
'''
        await event.respond(stats_info, buttons=self._admin_keyboard())
    
    async def handle_stop(self, event):
        """معالجة إيقاف السورس"""
        user_id = event.sender_id
        
        to_stop = []
        for uid, entry in self.manager.active_userbots.items():
            if entry.get('installer') == user_id or uid == user_id:
                to_stop.append((uid, entry))
        
        if not to_stop:
            await event.respond("⚠️ **ليس لديك سورس نشط لإيقافه.**")
            return
        
        for uid, entry in to_stop:
            try:
                entry['userbot'].client.disconnect()
                entry['task'].cancel()
                del self.manager.active_userbots[uid]
                
                installer_id = str(entry.get('installer', uid))
                self.manager.subscription_manager.update_user_installation(installer_id, uid)
                
                await event.respond(f"✅ **تم إيقاف السورس للحساب:** `{uid}`")
            except Exception as e:
                await event.respond(f"❌ **حدث خطأ أثناء إيقاف الحساب {uid}:** {e}")
        
        if len(to_stop) > 1:
            await event.respond(f"📊 **تم إيقاف {len(to_stop)} سورس بنجاح.**")
    
    def _get_total_users(self) -> int:
        """الحصول على إجمالي المستخدمين"""
        all_users = set()
        all_users.update(self.manager.subscription_manager.subscriptions.keys())
        all_users.update(self.manager.subscription_manager.trials.keys())
        return len(all_users)
    
    def _get_today_users(self) -> int:
        """الحصول على مستخدمين اليوم"""
        today = datetime.now().strftime("%Y-%m-%d")
        count = 0
        
        # حساب المستخدمين الجدد اليوم
        for sub in self.manager.subscription_manager.subscriptions.values():
            if sub.get('activated_date', '').startswith(today):
                count += 1
        
        for trial in self.manager.subscription_manager.trials.values():
            if trial.get('start_date', '').startswith(today):
                count += 1
        
        return count
    
    def _admin_keyboard(self):
        """لوحة مفاتيح الأدمن"""
        return [
            [Button.inline('الاحصائيات', b'stats'), Button.inline('الكوبونات', b'codes')],
            [Button.inline('اذاعة للجميع', b'broadcast'), Button.inline('تفعيل يدوي', b'manual_activate')],
            [Button.inline('الجلسات النشطة', b'sessions'), Button.inline('الغاء اشتراك', b'remove_sub')],
            [Button.inline('إنشاء كود', b'create_code'), Button.inline('اغلاق اللوحة', b'close')]
        ]
    
    def _user_keyboard(self):
        """لوحة مفاتيح المستخدم"""
        return [
            [Button.inline('📖 التعليمات', b'instructions'), Button.inline('🛒 شراء اشتراك', b'buy_sub')],
            [Button.inline('🔑 تفعيل الاشتراك', b'activate_code'), Button.inline('الدعم الفني 🆘', b'support')],
            [Button.inline('📲 تنصيب السورس', b'install')]
        ]