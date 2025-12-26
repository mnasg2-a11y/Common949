"""
معالج الرسائل للبوت الرئيسي
"""

import asyncio
from datetime import datetime
from typing import Dict

from telethon import events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

from src.config.settings import ADMIN_USERS
from src.modules.userbot import CommonUserBot
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MessageHandler:
    """معالج الرسائل"""
    
    def __init__(self, manager_bot):
        self.manager = manager_bot
    
    async def handle_messages(self, event):
        """معالجة جميع الرسائل"""
        chat_id = event.chat_id
        user_id = event.sender_id
        
        # معالجة تسجيل الدخول
        if chat_id in self.manager.login_states:
            await self._handle_login_message(event)
            return
        
        # معالجة إجراءات الأدمن
        if user_id in ADMIN_USERS and user_id in self.manager.waiting_for_admin:
            await self._handle_admin_action(event)
            return
        
        # معالجة كود التفعيل للمستخدم
        if user_id in self.manager.waiting_for_admin and self.manager.waiting_for_admin[user_id] == 'activate_code_user':
            await self._handle_activation_code(event)
            return
    
    async def _handle_login_message(self, event):
        """معالجة رسائل تسجيل الدخول"""
        chat_id = event.chat_id
        state = self.manager.login_states[chat_id]
        client = state['client']
        text = event.text.strip()

        try:
            if state['step'] == 'phone':
                # إرسال طلب الكود
                send_code = await client.send_code_request(text)
                state['phone'] = text
                state['phone_code_hash'] = send_code.phone_code_hash
                state['step'] = 'code'
                await event.respond("💬 **أرسل الكود الذي وصلك.** (مع مسافات: 1 2 3 4 5)")
            
            elif state['step'] == 'code':
                # التحقق من الكود
                code = text.replace(' ', '')
                try:
                    await client.sign_in(
                        phone=state['phone'], 
                        code=code, 
                        phone_code_hash=state['phone_code_hash']
                    )
                    await self._handle_login_success(event, client, state['user_id'])
                except SessionPasswordNeededError:
                    state['step'] = 'password'
                    await event.respond("🔐 **الحساب محمي بكلمة سر (2FA). أرسلها الآن.**")
                except PhoneCodeInvalidError:
                    await event.respond("❌ الكود غير صحيح، حاول مرة أخرى.")
            
            elif state['step'] == 'password':
                # التحقق من كلمة السر
                try:
                    await client.sign_in(password=text)
                    await self._handle_login_success(event, client, state['user_id'])
                except Exception as e:
                    await event.respond(f"❌ كلمة السر خطأ: {e}")
        
        except Exception as e:
            await event.respond(f"⚠️ **حدث خطأ:** {e}\nأعد المحاولة بـ /start")
            if chat_id in self.manager.login_states:
                del self.manager.login_states[chat_id]
    
    async def _handle_login_success(self, event, client, user_id):
        """معالجة نجاح تسجيل الدخول"""
        chat_id = event.chat_id
        session_string = client.session.save()
        me = await client.get_me()
        
        # التحقق من الاشتراك
        sub_status = self.manager.subscription_manager.check_subscription(user_id)
        if not sub_status["active"]:
            await event.respond("⚠️ **ليس لديك اشتراك نشط.**\nيرجى شراء اشتراك أو استخدام التجربة المجانية.")
            await client.disconnect()
            if chat_id in self.manager.login_states:
                del self.manager.login_states[chat_id]
            return
        
        # التحقق من وجود سورس نشط
        if me.id in self.manager.active_userbots:
            await event.respond("⚠️ **هذا الحساب لديه سورس نشط بالفعل!**")
            await client.disconnect()
            if chat_id in self.manager.login_states:
                del self.manager.login_states[chat_id]
            return
        
        # التحقق من حد التثبيتات
        install_check = self.manager.subscription_manager.check_installation_limit(str(user_id))
        if not install_check["allowed"]:
            await event.respond(f"⛔️ **{install_check['reason']}**")
            await client.disconnect()
            if chat_id in self.manager.login_states:
                del self.manager.login_states[chat_id]
            return
        
        # إنشاء وتشغيل اليوزربوت
        userbot = CommonUserBot(session_string, me.id, user_id)
        task = asyncio.create_task(userbot.start())
        
        self.manager.active_userbots[me.id] = {
            'userbot': userbot, 
            'task': task, 
            'installer': user_id
        }
        
        # تحديث تثبيتات المستخدم
        self.manager.subscription_manager.update_user_installation(str(user_id), me.id)
        
        # التحقق من انتهاء التجربة
        if sub_status["type"] == "trial" and sub_status["days_left"] <= 0:
            self.manager.subscription_manager.remove_subscription(str(user_id))
            await event.respond("⏰ **انتهت فترة التجربة المجانية.**\nيرجى شراء اشتراك للاستمرار.")
            await client.disconnect()
            del self.manager.active_userbots[me.id]
            if chat_id in self.manager.login_states:
                del self.manager.login_states[chat_id]
            return
        
        # رسالة النجاح
        success_msg = (
            f"✅ **تم تنصيب سورس كومن الذكي بنجاح!**\n\n"
            f"👤 **الحساب المنصب:** {me.first_name}\n"
            f"🆔 **ID:** `{me.id}`\n"
            f"📊 **نوع الاشتراك:** {sub_status['type']}\n"
            f"⏳ **الأيام المتبقية:** {sub_status['days_left']}\n"
            f"🧠 **الذكاء الاصطناعي:** مفعّل\n"
            f"🤝 **نظام الشركاء:** جاهز للربح\n\n"
            f"💰 **للربح من السورس:**\n"
            f"1. اكتب `.شركاء` لنظام الشركاء\n"
            f"2. اكتب `.احالة` للحصول على رابط الإحالة\n"
            f"3. اكتب `.تجميع` للتجميع التلقائي\n\n"
            f"📍 **اذهب للرسائل المحفوظة واكتب `.الاوامر`**\n"
            f"🧠 **للذكاء الاصطناعي اكتب `.ذكاء`**\n"
            f"🛑 **لإيقاف السورس:** /stop"
        )
        
        await event.respond(success_msg)
        
        # تنظيف حالة التسجيل
        if chat_id in self.manager.login_states:
            del self.manager.login_states[chat_id]
        
        logger.info(f"✅ تم تنصيب سورس جديد للمستخدم {user_id} على الحساب {me.id}")
    
    async def _handle_admin_action(self, event):
        """معالجة إجراءات الأدمن"""
        user_id = event.sender_id
        action = self.manager.waiting_for_admin[user_id]
        text = event.text.strip()
        
        try:
            if action == 'create_code':
                await self._handle_create_code_action(event, text, user_id)
            elif action == 'manual_activation':
                await self._handle_manual_activation(event, text, user_id)
            elif action == 'remove_subscription':
                await self._handle_remove_subscription(event, text, user_id)
            elif action == 'broadcast_all':
                await self._handle_broadcast(event, text, user_id)
            
            # تنظيف حالة الانتظار
            self.manager.waiting_for_admin[user_id] = None
            
        except Exception as e:
            await event.respond(f'❌ خطأ: {str(e)}')
            self.manager.waiting_for_admin[user_id] = None
    
    async def _handle_create_code_action(self, event, text: str, user_id: int):
        """معالجة إنشاء كود"""
        try:
            parts = text.split()
            if len(parts) >= 2:
                days = int(parts[0])
                sub_type = parts[1]
                
                code = self.manager.subscription_manager.generate_activation_code(days, sub_type, user_id)
                
                await event.respond(
                    f"✅ **تم إنشاء كود تفعيل جديد!**\n\n"
                    f"🔑 **الكود:** `{code}`\n"
                    f"📅 **المدة:** {days} يوم\n"
                    f"📋 **النوع:** {sub_type}\n"
                    f"👤 **المنشئ:** `{user_id}`\n\n"
                    f"📝 **يمكن للمستخدمين تفعيله باستخدام زر 'تفعيل الاشتراك'**"
                )
            else:
                await event.respond("❌ صيغة غير صحيحة. مثال: `30 مدفوع`")
        except Exception as e:
            await event.respond(f"❌ خطأ: {str(e)}")
    
    async def _handle_manual_activation(self, event, text: str, user_id: int):
        """معالجة التفعيل اليدوي"""
        try:
            parts = text.split()
            if len(parts) >= 2:
                target_id = parts[0]
                sub_type = parts[1]
                
                if sub_type == 'أسبوعي':
                    days = 7
                    sub_type_name = "weekly"
                elif sub_type == 'شهري':
                    days = 30
                    sub_type_name = "monthly"
                elif sub_type == 'سنوي':
                    days = 365
                    sub_type_name = "yearly"
                else:
                    await event.respond("❌ نوع اشتراك غير صحيح. اختر: أسبوعي، شهري، سنوي")
                    return
                
                end_date = self.manager.subscription_manager.activate_subscription(target_id, days, sub_type_name)
                
                await event.respond(
                    f"✅ **تم تفعيل الاشتراك يدوياً!**\n\n"
                    f"👤 **المستخدم:** `{target_id}`\n"
                    f"📅 **المدة:** {days} يوم\n"
                    f"📋 **النوع:** {sub_type}\n"
                    f"⏳ **ينتهي في:** {end_date.strftime('%Y-%m-%d')}"
                )
            else:
                await event.respond("❌ صيغة غير صحيحة. مثال: `1234567890 أسبوعي`")
        except Exception as e:
            await event.respond(f"❌ خطأ: {str(e)}")
    
    async def _handle_remove_subscription(self, event, text: str, user_id: int):
        """معالجة إلغاء اشتراك"""
        try:
            target_id = text.strip()
            result = self.manager.subscription_manager.remove_subscription(target_id)
            
            if result["success"]:
                await event.respond(result["message"])
            else:
                await event.respond(result["message"])
        except Exception as e:
            await event.respond(f"❌ خطأ: {str(e)}")
    
    async def _handle_broadcast(self, event, text: str, user_id: int):
        """معالجة الإذاعة"""
        sent = 0
        total_users = set()
        
        # جمع جميع المستخدمين
        total_users.update(self.manager.active_userbots.keys())
        total_users.update(self.manager.subscription_manager.subscriptions.keys())
        total_users.update(self.manager.subscription_manager.trials.keys())
        
        for uid in total_users:
            try:
                if isinstance(uid, str):
                    uid = int(uid)
                await self.manager.client.send_message(
                    uid, 
                    f"📢 **إذاعة من الإدارة:**\n\n{text}"
                )
                sent += 1
                await asyncio.sleep(0.1)
            except:
                pass
        
        await event.reply(f'📡 تم ارسال الاذاعة الى {sent} مستخدم من أصل {len(total_users)}')
    
    async def _handle_activation_code(self, event):
        """معالجة كود التفعيل للمستخدم"""
        user_id = event.sender_id
        code = event.text.strip().upper()
        
        result = self.manager.subscription_manager.use_activation_code(code, str(user_id))
        if result["success"]:
            await event.respond(
                f"✅ **تم تفعيل الاشتراك بنجاح!**\n\n"
                f"🎉 **مبروك!** تم تفعيل اشتراكك.\n"
                f"📅 **المدة:** {result['days']} يوم\n"
                f"📋 **النوع:** {result['type']}\n"
                f"⏳ **ينتهي في:** {result['end_date'].strftime('%Y-%m-%d')}\n\n"
                f"🤝 **نظام الشركاء مفعّل!**\n"
                f"استخدم `.شركاء` للبدء في الربح\n\n"
                f"👇 **الآن يمكنك تنصيب السورس:**"
            )
        else:
            await event.respond(
                "❌ **الكود غير صالح:**\n\n"
                "قد يكون السباب:\n"
                "1. الكود غير صحيح\n"
                "2. الكود مستخدم مسبقاً\n"
                "3. الكود منتهي الصلاحية\n\n"
                "📞 **للحصول على كود جديد:** @iomk0"
            )
        
        self.manager.waiting_for_admin[user_id] = None