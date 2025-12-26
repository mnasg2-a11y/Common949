"""
معالج الأزرار للبوت الرئيسي
"""

import asyncio
from datetime import datetime
from typing import Dict

from telethon import events, Button
from telethon.sessions import StringSession

from src.config.settings import ADMIN_USERS, SUPPORT_USER
from src.utils.logger import get_logger

logger = get_logger(__name__)

class CallbackHandler:
    """معالج الأزرار"""
    
    def __init__(self, manager_bot):
        self.manager = manager_bot
    
    async def handle_callbacks(self, event):
        """معالجة جميع الأزرار"""
        user_id = event.sender_id
        data = event.data.decode('utf-8')
        
        logger.info(f"Callback from {user_id}: {data}")
        
        # تحويل البيانات إلى دالة
        handler_name = f"_handle_{data}"
        if hasattr(self, handler_name):
            await getattr(self, handler_name)(event)
        else:
            # معالجة الأزرار العامة
            await self._handle_general_callback(event, data)
    
    async def _handle_stats(self, event):
        """معالجة زر الإحصائيات"""
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
        await event.edit(stats_info, buttons=self.admin_keyboard())
    
    async def _handle_codes(self, event):
        """معالجة زر الكوبونات"""
        activation_codes = self.manager.subscription_manager.activation_codes
        
        if not activation_codes:
            await event.edit('لا توجد كوبونات.', buttons=self.admin_keyboard())
            return
        
        codes_list = []
        for code, details in list(activation_codes.items())[:20]:
            status = "🟢 مستخدم" if details.get("used") else "🟡 غير مستخدم"
            codes_list.append(f"`{code}` - {details['type']} - {details['days']} يوم - {status}")
        
        text = "📋 **قائمة الكوبونات:**\n\n" + "\n".join(codes_list)
        if len(activation_codes) > 20:
            text += f"\n\n📊 **إجمالي الكوبونات:** {len(activation_codes)}"
        
        await event.edit(text, buttons=self.admin_keyboard())
    
    async def _handle_create_code(self, event):
        """معالجة زر إنشاء كود"""
        user_id = event.sender_id
        self.manager.waiting_for_admin[user_id] = 'create_code'
        
        await event.edit(
            '🔐 **إنشاء كود تفعيل جديد:**\n\n'
            'أرسل التفاصيل بالصيغة التالية:\n'
            '`[عدد الأيام] [نوع الاشتراك]`\n\n'
            '**مثال:** `30 مدفوع` أو `7 أسبوعي`\n'
            '**الأنواع:** مدفوع، أسبوعي، شهري، سنوي',
            buttons=[[Button.inline('رجوع', b'back')]]
        )
    
    async def _handle_instructions(self, event):
        """معالجة زر التعليمات"""
        instructions = """
**📚 تعليمات استخدام سورس كومن الذكي:**

✅ **كيفية التنصيب:**
1. اضغط على زر "تنصيب السورس"
2. أرسل رقم هاتف الحساب (مع رمز الدولة)
3. انتظر كود التأكيد على التليجرام
4. أرسل الكود إلى البوت
5. إذا كان الحساب محمي بكلمة سر، أرسلها

💰 **نظام الشركاء والربح:**
- استخدم `.شركاء` لعرض نظام الربح
- استخدم `.احالة` للحصول على رابط الإحالة
- شارك الرابط واربح 10-30% من كل اشتراك

🧠 **الذكاء الاصطناعي:**
- اكتب `.ذكاء` لعرض جميع الأوامر
- استخدم `.سؤال [سؤالك]` للأسئلة
- استخدم `.محادثة` للدردشة التفاعلية
- استخدم `.اصنع صورة [وصف]` لإنشاء صور حقيقية

📞 **للإستفسار والدعم:** @iomk0
        """
        
        await event.edit(instructions, buttons=[[Button.inline("رجوع", b'back')]])
    
    async def _handle_buy_sub(self, event):
        """معالجة زر شراء اشتراك"""
        await event.respond(
            "🛒 **خيارات الاشتراك المتاحة:**\n\n"
            "1️⃣ **أسبوعي:** 5$\n   - مدة: 7 أيام\n   - عمولة شركاء: 10%\n\n"
            "2️⃣ **شهري:** 15$\n   - مدة: 30 يوم\n   - عمولة شركاء: 15%\n\n"
            "3️⃣ **سنوي:** 50$\n   - مدة: 365 يوم\n   - عمولة شركاء: 20%\n\n"
            "🤝 **نظام الشركاء مفعّل:**\n"
            "- ربح 10-30% من كل إحالة\n\n"
            "💳 **طريقة الدفع:**\n"
            "1. قم بالتحويل إلى الحساب البنكي\n"
            "2. أرسل إيصال التحويل إلى @iomk0\n"
            "3. سيرسل لك كود التفعيل\n"
            "4. استخدم الكود لتفعيل الاشتراك\n\n"
            "📞 **للدفع والاستفسار:** @iomk0",
            buttons=[[Button.url("التواصل مع المطور", f"https://t.me/{SUPPORT_USER}")]]
        )
    
    async def _handle_activate_code(self, event):
        """معالجة زر تفعيل الاشتراك"""
        user_id = event.sender_id
        chat_id = event.chat_id

        sub_status = self.manager.subscription_manager.check_subscription(user_id)
        if sub_status["active"]:
            await event.respond("⚠️ **لديك اشتراك نشط بالفعل.**")
            return

        await event.respond(
            "🔑 **تفعيل الاشتراك بواسطة الكود:**\n\n"
            "📝 **أرسل كود التفعيل الآن:**\n"
            "(يجب أن يكون الكود مكون من 8 أحرف مثل: xxxxxxxx)",
            buttons=[[Button.inline("❌ إلغاء", b'cancel')]]
        )
        self.manager.waiting_for_admin[user_id] = 'activate_code_user'
    
    async def _handle_install(self, event):
        """معالجة زر تنصيب السورس"""
        chat_id = event.chat_id
        user_id = event.sender_id
        
        sub_status = self.manager.subscription_manager.check_subscription(user_id)
        
        if not sub_status["active"]:
            await event.respond("⚠️ **ليس لديك اشتراك نشط.**\nيرجى شراء اشتراك أو استخدام التجربة المجانية.")
            return
        
        install_check = self.manager.subscription_manager.check_installation_limit(str(user_id))
        if not install_check["allowed"]:
            await event.respond(f"⛔️ **{install_check['reason']}**")
            return
        
        new_client = TelegramClient(StringSession(), self.manager.client.api_id, self.manager.client.api_hash)
        await new_client.connect()
        self.manager.login_states[chat_id] = {'client': new_client, 'step': 'phone', 'user_id': user_id}
        
        await event.respond(
            "📞 **أرسل رقم هاتف الحساب المراد تنصيب السورس عليه**\n\n"
            "**ملاحظات:**\n"
            "✅ يمكنك إدخال أي رقم هاتف (حسابك أو حساب شخص آخر)\n"
            "📱 مثال: `+9647700000000`\n\n"
            "🧠 **السورس يحتوي على:**\n"
            "- ذكاء اصطناعي متكامل\n"
            "- نظام شركاء وربح\n"
            "- تجميع نقاط تلقائي\n"
            "- أكثر من 200 ميزة",
            buttons=[[Button.inline("❌ إلغاء", b'cancel')]]
        )
    
    async def _handle_back(self, event):
        """معالجة زر الرجوع"""
        user_id = event.sender_id
        
        if user_id in ADMIN_USERS:
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
            await event.edit(admin_info, buttons=self.admin_keyboard())
        else:
            sub_status = self.manager.subscription_manager.check_subscription(user_id)
            if sub_status["active"]:
                await event.edit(
                    f"👋 **أهلاً بك في سورس كومن الذكي**\n\n"
                    f"✅ **لديك اشتراك نشط:**\n"
                    f"📊 **النوع:** {sub_status['type']}\n"
                    f"⏳ **الأيام المتبقية:** {sub_status['days_left']}\n"
                    f"🧠 **الذكاء الاصطناعي:** مفعّل\n\n"
                    f"👇 **اختر الخيار المناسب:**",
                    buttons=self.user_keyboard()
                )
            else:
                await event.edit(
                    "👋 **أهلاً بك في سورس كومن الذكي**\n\n"
                    "⚠️ **لقد انتهت تجربتك المجانية.**\n"
                    "🧠 **الذكاء الاصطناعي:** جاهز\n"
                    "🤝 **نظام الشركاء:** جاهز للربح\n"
                    "📅 **يمكنك الاشتراك الآن للحصول على السورس:**",
                    buttons=self.user_keyboard()
                )
    
    async def _handle_cancel(self, event):
        """معالجة زر الإلغاء"""
        chat_id = event.chat_id
        if chat_id in self.manager.login_states:
            await self.manager.login_states[chat_id]['client'].disconnect()
            del self.manager.login_states[chat_id]
        
        await event.respond("❌ تم الإلغاء.", buttons=self.user_keyboard())
    
    async def _handle_general_callback(self, event, data: str):
        """معالجة الأزرار العامة"""
        # إذا كان زر إيقاف جلسة
        if data.startswith('stop_session_'):
            await self._handle_stop_session(event, data)
        else:
            await event.respond(f"⚠️ زر غير معروف: {data}")
    
    async def _handle_stop_session(self, event, data: str):
        """معالجة إيقاف جلسة محددة"""
        try:
            target_uid = int(data.split('_')[2])
            
            if target_uid in self.manager.active_userbots:
                entry = self.manager.active_userbots[target_uid]
                
                entry['userbot'].client.disconnect()
                entry['task'].cancel()
                del self.manager.active_userbots[target_uid]
                
                installer_id = str(entry.get('installer', target_uid))
                self.manager.subscription_manager.update_user_installation(installer_id, target_uid)
                
                await event.edit(f"✅ **تم إيقاف الجلسة لـ `{target_uid}` بنجاح.**", 
                                buttons=[[Button.inline('رجوع', b'back')]])
            else:
                await event.edit("❌ **الجلسة غير موجودة.**", 
                                buttons=[[Button.inline('رجوع', b'back')]])
        except Exception as e:
            await event.edit(f"❌ **خطأ:** {str(e)}", 
                            buttons=[[Button.inline('رجوع', b'back')]])
    
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
        
        for sub in self.manager.subscription_manager.subscriptions.values():
            if sub.get('activated_date', '').startswith(today):
                count += 1
        
        for trial in self.manager.subscription_manager.trials.values():
            if trial.get('start_date', '').startswith(today):
                count += 1
        
        return count
    
    def admin_keyboard(self):
        """لوحة مفاتيح الأدمن"""
        return [
            [Button.inline('الاحصائيات', b'stats'), Button.inline('الكوبونات', b'codes')],
            [Button.inline('اذاعة للجميع', b'broadcast'), Button.inline('تفعيل يدوي', b'manual_activate')],
            [Button.inline('الجلسات النشطة', b'sessions'), Button.inline('الغاء اشتراك', b'remove_sub')],
            [Button.inline('إنشاء كود', b'create_code'), Button.inline('اغلاق اللوحة', b'close')]
        ]
    
    def user_keyboard(self):
        """لوحة مفاتيح المستخدم"""
        return [
            [Button.inline('📖 التعليمات', b'instructions'), Button.inline('🛒 شراء اشتراك', b'buy_sub')],
            [Button.inline('🔑 تفعيل الاشتراك', b'activate_code'), Button.inline('الدعم الفني 🆘', b'support')],
            [Button.inline('📲 تنصيب السورس', b'install')]
        ]