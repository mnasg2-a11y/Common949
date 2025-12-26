"""
محرك اليوزربوت الرئيسي لسورس كومن
"""

import asyncio
import os
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from io import BytesIO

from telethon import TelegramClient, events, functions, types, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import CreateChannelRequest, EditChatPhotoRequest
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.types import ChatBannedRights

import yt_dlp
import aiohttp
from urllib.parse import quote

from src.config.settings import (
    API_ID, API_HASH, ALLOWED_FILE,
    VIDEO_FILE, IMAGE_FILE, COLLECTION_BOTS
)
from src.modules.ai_system import GeminiAI
from src.modules.referral_system import AdvancedReferralSystem
from src.utils.logger import get_logger

logger = get_logger(__name__)

class CommonUserBot:
    """فئة اليوزربوت الرئيسية"""
    
    def __init__(self, session_str: str, user_id: int, installer_id: int):
        self.client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        self.user_id = user_id
        self.installer_id = installer_id
        
        # الإعدادات
        self.config = {
            "auto_save": True,
            "ghost": False,
            "reply": False,
            "auto_block": False,
            "clock": False,
            "anim_name": False,
            "online": True,
            "reply_txt": "👋 **أهلاً بك، أنا مشغول حالياً.**",
            "auto_collect": False,
            "auto_hunt": False
        }
        
        self.log_channels = {"private": None, "groups": None}
        self.flood_cache = {}
        self.allowed_users = self._load_allowed_users()
        self.start_time = time.time()
        self.auto_post_tasks = {}
        self.image_cache = {}
        
        # الأنظمة
        self.ai = GeminiAI(self)
        self.ai_enabled = True
        self.ai_conversation_mode = False
        self.referral_system = AdvancedReferralSystem()
        
        logger.info(f"✅ تم إنشاء يوزربوت جديد للمستخدم: {user_id}")
    
    def _load_allowed_users(self) -> Set[int]:
        """تحميل قائمة السماح"""
        if os.path.exists(ALLOWED_FILE):
            try:
                with open(ALLOWED_FILE, 'r') as f:
                    data = json.load(f)
                    return set(data)
            except Exception as e:
                logger.error(f"خطأ في تحميل قائمة السماح: {e}")
        return set()
    
    def _save_allowed_users(self):
        """حفظ قائمة السماح"""
        try:
            with open(ALLOWED_FILE, 'w') as f:
                json.dump(list(self.allowed_users), f)
        except Exception as e:
            logger.error(f"خطأ في حفظ قائمة السماح: {e}")
    
    async def setup_channels(self):
        """إنشاء مجموعات التخزين"""
        try:
            # البحث عن المجموعات الحالية
            async for dialog in self.client.iter_dialogs():
                if dialog.title == "📦 مخزن الرسائل (Common)": 
                    self.log_channels["private"] = dialog.id
                elif dialog.title == "🛡 مخزن المجموعات (Common)": 
                    self.log_channels["groups"] = dialog.id
            
            # رفع الصورة
            uploaded_photo = None
            if os.path.exists(IMAGE_FILE):
                try:
                    uploaded_photo = await self.client.upload_file(IMAGE_FILE)
                except:
                    pass
            
            # إنشاء مجموعة الرسائل الخاصة
            if not self.log_channels["private"]:
                try:
                    c = await self.client(CreateChannelRequest(
                        title="📦 مخزن الرسائل (Common)", 
                        about="سورس ڪومن | 𝗰𝗼𝗺𝗺𝗼𝗻 الاقوى في تلكرام🔥",
                        megagroup=True
                    ))
                    self.log_channels["private"] = c.chats[0].id
                    
                    if uploaded_photo:
                        try:
                            await self.client(EditChatPhotoRequest(
                                self.log_channels["private"], 
                                photo=uploaded_photo
                            ))
                        except:
                            pass
                except Exception as e:
                    logger.error(f"خطأ في إنشاء قناة الرسائل: {e}")
            
            # إنشاء مجموعة المجموعات
            if not self.log_channels["groups"]:
                try:
                    c = await self.client(CreateChannelRequest(
                        title="🛡 مخزن المجموعات (Common)", 
                        about="سورس ڪومن | 𝗰𝗼𝗺𝗺𝗼𝗻 الاقوى في تلكرام🔥",
                        megagroup=True
                    ))
                    self.log_channels["groups"] = c.chats[0].id
                    
                    if uploaded_photo:
                        try:
                            await self.client(EditChatPhotoRequest(
                                self.log_channels["groups"], 
                                photo=uploaded_photo
                            ))
                        except:
                            pass
                except Exception as e:
                    logger.error(f"خطأ في إنشاء قناة المجموعات: {e}")
            
            # إرسال رسالة الترحيب
            caption = (
                "**⚡ تم تفعيل سورس كومن الذكي**\n\n"
                "✅ **الحالة:** شغال 100٪\n" 
                "🧠 **الذكاء الاصطناعي:** Common Pro مفعّل\n"
                "🤝 **نظام الشركاء:** مفعّل\n"
                "👤 **المطور:** حسين - @iomk0\n\n"
                "🚀 **الميزات المتاحة:**\n"
                "• ذكاء اصطناعي Common المتقدم\n"
                "• إدارة متقدمة للمجموعات\n"
                "• حماية من السبام والتكرار\n"
                "• نشر تلقائي\n"
                "• اسم وقتي ومتحرك\n"
                "• نظام شركاء وربح\n"
                "• أكثر من 200 ميزة\n\n"
                "📞 **الدعم الفني:** @iomk0"
            )
            
            if os.path.exists(VIDEO_FILE) and self.log_channels["private"]:
                await self.client.send_file(
                    self.log_channels["private"], 
                    VIDEO_FILE, 
                    caption=caption
                )
            else:
                await self.client.send_message(
                    self.log_channels["private"], 
                    caption
                )
            
            # إرسال رسالة ترحيب للرسائل المحفوظة
            try:
                me = await self.client.get_me()
                welcome_msg = (
                    "**🎉 أهلاً بك في سورس كومن الذكي!**\n\n"
                    "✅ **تم تفعيل السورس بنجاح على حسابك.**\n"
                    "🧠 **الذكاء الاصطناعي:** Common Pro جاهز للاستخدام\n"
                    "🤝 **نظام الشركاء:** جاهز للربح\n"
                    "⚡ **لبدء الاستخدام اكتب `.الاوامر`**\n\n"
                    "📍 **معلومات حسابك:**\n"
                    f"👤 **الاسم:** {me.first_name if me.first_name else 'غير معروف'}\n"
                    f"🆔 **ID:** `{me.id}`\n\n"
                    "💰 **للربح من السورس:**\n"
                    "• `.شركاء` - عرض نظام الشركاء\n"
                    "• `.احالة` - رابط الإحالة الخاص بك\n"
                    "• `.ربح` - طرق الربح\n\n"
                    "🚀 **للتحكم في السورس:**\n"
                    "• `.الاوامر` - لعرض جميع الأوامر\n"
                    "• `.ذكاء` - لقائمة الذكاء الاصطناعي\n"
                    "📞 **للتواصل والدعم:** @iomk0\n"
                    "💎 **قناة السورس:** @iomk3"
                )
                
                if os.path.exists(VIDEO_FILE):
                    await self.client.send_file("me", VIDEO_FILE, caption=welcome_msg)
                else:
                    await self.client.send_message("me", welcome_msg)
                
                logger.info(f"✅ تم إرسال رسالة الترحيب للمستخدم: {me.id}")
            except Exception as e:
                logger.error(f"❌ خطأ في إرسال رسالة الترحيب: {e}")
        
        except Exception as e:
            logger.error(f"Setup Error: {e}")
    
    async def clock_loop(self):
        """حلقة تحديث الساعة في الاسم"""
        while self.config['clock']:
            try:
                # الوقت العراقي (UTC+3)
                now = datetime.utcnow() + timedelta(hours=3)
                wide_time = self._make_wide(now.strftime("%I:%M"))
                me = await self.client.get_me()
                base = me.first_name.split()[0] if me.first_name else "User"
                if wide_time not in base:
                    new_name = f"{base} {wide_time}"
                    await self.client(functions.account.UpdateProfileRequest(first_name=new_name))
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Clock loop error: {e}")
                await asyncio.sleep(60)
    
    def _make_wide(self, text: str) -> str:
        """تحويل الأرقام إلى خط عريض"""
        mapping = str.maketrans("0123456789:", "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗꞉")
        return text.translate(mapping)
    
    async def animation_loop(self):
        """حلقة الاسم المتحرك"""
        i = 0
        while self.config['anim_name']:
            try:
                me = await self.client.get_me()
                base = me.first_name.split()[0] if me.first_name else "User"
                names = [base, f"✨ {base}", f"⚡ {base}", f"🔥 {base} 🔥", f"👑 {base}", f"🇮🇶 {base}"]
                await self.client(functions.account.UpdateProfileRequest(first_name=names[i % len(names)]))
                i += 1
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Animation loop error: {e}")
                await asyncio.sleep(5)
    
    async def auto_collect_points(self):
        """التجميع التلقائي للنقاط"""
        while self.config['auto_collect']:
            try:
                collected = 0
                for bot in COLLECTION_BOTS:
                    try:
                        await self.client.send_message(bot, "/start")
                        await asyncio.sleep(1)
                        await self.client.send_message(bot, "/play")
                        await asyncio.sleep(1)
                        await self.client.send_message(bot, "/daily")
                        collected += 1
                        await asyncio.sleep(2)
                    except:
                        continue
                
                if collected > 0:
                    logger.info(f"تم جمع النقاط من {collected} بوت")
                
                await asyncio.sleep(3600)  # كل ساعة
                
            except Exception as e:
                logger.error(f"Auto collect error: {e}")
                await asyncio.sleep(60)
    
    async def generate_image_flux_max(self, prompt: str) -> Optional[str]:
        """صنع صورة باستخدام flux-max"""
        try:
            # ترجمة النص للإنجليزية
            import requests
            from deep_translator import GoogleTranslator
            from langdetect import detect
            
            lang = detect(prompt)
            if lang != 'en':
                translated_prompt = GoogleTranslator(source='auto', target='en').translate(prompt)
            else:
                translated_prompt = prompt
            
            seed = random.randint(1, 999999999)
            
            if "logo" in translated_prompt.lower() or "شعار" in prompt.lower():
                style = "vector art, centered, clean, minimalist, high contrast, 8k resolution"
            else:
                style = (
                    "hyper-realistic, shot on Sony A7R IV, 85mm lens, "
                    "cinematic lighting, detailed skin texture, "
                    "no blur, extremely detailed, masterpiece, 8k, raw photo"
                )
            
            full_prompt = f"{translated_prompt}, {style}"
            encoded_prompt = quote(full_prompt)
            
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux-realism&width=1280&height=720&seed={seed}&nologo=true&enhance=false"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=60) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        # حفظ الصورة مؤقتاً
                        file_name = f"flux_image_{seed}.jpg"
                        with open(file_name, 'wb') as f:
                            f.write(image_data)
                        return file_name
                    else:
                        return None
        except Exception as e:
            logger.error(f"Error generating image (flux): {e}")
            return None
    
    async def start(self):
        """بدء تشغيل اليوزربوت"""
        await self.client.connect()
        
        # إضافة المعالجات
        self.client.add_event_handler(self._incoming_handler, events.NewMessage(incoming=True))
        self.client.add_event_handler(self._command_handler, events.NewMessage(outgoing=True))
        self.client.add_event_handler(self._button_handler, events.CallbackQuery)
        
        # الإعدادات الأولية
        await self.setup_channels()
        
        # تشغيل المهام الخلفية
        if self.config['clock']:
            asyncio.create_task(self.clock_loop())
        
        if self.config['anim_name']:
            asyncio.create_task(self.animation_loop())
        
        if self.config['auto_collect']:
            asyncio.create_task(self.auto_collect_points())
        
        if self.config['online']:
            await self.client(functions.account.UpdateStatusRequest(offline=False))
        
        logger.info(f"✅ بدء تشغيل اليوزربوت للمستخدم: {self.user_id}")
    
    async def _incoming_handler(self, event):
        """معالج الرسائل الواردة"""
        try:
            sender = await event.get_sender()
            if not sender:
                return
            
            # تسجيل الرسائل في المخزن
            if event.is_private and self.log_channels["private"]:
                try:
                    await self.client.send_message(
                        self.log_channels["private"], 
                        f"📨 **رسالة واردة من:** {sender.first_name}\n👤 **ID:** `{sender.id}`"
                    )
                    await event.forward_to(self.log_channels["private"])
                except:
                    pass
            
            # الحماية من التكرار
            if self.config['auto_block'] and event.is_private and not sender.bot and not sender.is_self:
                await self._handle_flood_protection(event, sender)
            
            # الرد التلقائي
            if self.config['reply'] and event.is_private and not sender.bot:
                await self._handle_auto_reply(event, sender)
            
            # الذكاء الاصطناعي التلقائي
            if self.ai_enabled and event.is_private and not sender.bot and not sender.is_self:
                await self._handle_ai_response(event, sender)
            
            # وضع الشبح
            if self.config['ghost'] and event.is_private:
                await event.message.mark_read()
            
            # حفظ الصور ذاتية التدمير
            if self.config['auto_save'] and event.is_private and event.media:
                await self._handle_self_destruct(event, sender)
                
        except Exception as e:
            logger.error(f"Incoming handler error: {e}")
    
    async def _handle_flood_protection(self, event, sender):
        """حماية من التكرار"""
        uid = sender.id
        now = time.time()
        
        if uid not in self.flood_cache:
            self.flood_cache[uid] = {'count': 1, 'time': now}
        else:
            if now - self.flood_cache[uid]['time'] > 60:
                self.flood_cache[uid] = {'count': 1, 'time': now}
            else:
                self.flood_cache[uid]['count'] += 1
        
        current_count = self.flood_cache[uid]['count']
        
        if current_count > 3:
            try:
                final_msg = (
                    "⛔ **تم حظرك تلقائياً!**\n"
                    "⚠️ **لقد تجاوزت عدد الرسائل المسموح به (3).**\n"
                    "🤖 **System Blocked You.**"
                )
                await event.reply(final_msg)
                await self.client(BlockRequest(uid))
                del self.flood_cache[uid]
                
                if self.log_channels["private"]:
                    await self.client.send_message(
                        self.log_channels["private"], 
                        f"👮‍♂️ **تم حظر {sender.first_name} تلقائياً بسبب التكرار.**"
                    )
                return
            except Exception as e:
                logger.error(f"Block Error: {e}")
        
        elif current_count > 1:
            warning_msg = (
                f"✋ **تحذير تلقائي ({current_count}/3)**\n\n"
                f"⚠️ **عذراً، أنا مشغول ولا أستطيع الرد الآن.**\n"
                f"🛑 **الرجاء التوقف عن التكرار لتجنب الحظر.**"
            )
            await event.reply(warning_msg)
    
    async def _handle_auto_reply(self, event, sender):
        """الرد التلقائي"""
        uid = sender.id
        if uid not in self.flood_cache or self.flood_cache[uid]['count'] == 1:
            await asyncio.sleep(1)
            nice_reply = (
                f"👋 **أهلاً بك عزيزي**\n\n"
                f"💬 **{self.config['reply_txt']}**\n"
                f"⏱ **سأقوم بالرد عليك عند تفرغي.**"
            )
            await event.reply(nice_reply)
    
    async def _handle_ai_response(self, event, sender):
        """الرد الذكي التلقائي"""
        if self.ai_conversation_mode:
            response = await self.ai.chat(self.user_id, event.text)
            if not response.startswith("•"):
                response = f"• {response}"
            await event.reply(f"🧠 **الذكاء الاصطناعي:**\n\n{response}")
            return
        
        ai_triggers = ['ai', 'ذكاء', 'chatgpt', 'بوت ذكي', 'Common', 'مساعدة', 'سؤال']
        if any(trigger in event.text.lower() for trigger in ai_triggers):
            response = await self.ai.chat(self.user_id, event.text)
            if not response.startswith("•"):
                response = f"• {response}"
            await event.reply(f"🧠 **رد ذكي:**\n\n{response}")
    
    async def _handle_self_destruct(self, event, sender):
        """حفظ الصور ذاتية التدمير"""
        if hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds:
            try:
                p = await event.download_media()
                await self.client.send_file(
                    'me', 
                    p, 
                    caption=f"💣 **تم صيد ميديا مؤقتة من:** {sender.first_name}"
                )
                os.remove(p)
            except:
                pass
    
    async def _command_handler(self, event):
        """معالج الأوامر"""
        if not event.text:
            return
        
        txt = event.text.strip()
        chat = event.chat_id
        
        # تسجيل الأوامر في المخزن
        if event.is_private and self.log_channels["private"]:
            try:
                await self.client.send_message(
                    self.log_channels["private"], 
                    f"📤 **رسالة صادرة إلى:** {chat}"
                )
                await event.forward_to(self.log_channels["private"])
            except:
                pass
        
        # معالجة الأوامر
        await self._process_command(event, txt, chat)
    
    async def _process_command(self, event, txt: str, chat: int):
        """معالجة الأوامر"""
        # نظام الشركاء
        if txt == ".شركاء":
            await self._show_partner_system(event)
        elif txt == ".احالة":
            await self._show_referral_link(event)
        elif txt == ".احصائياتي":
            await self._show_partner_stats(event)
        elif txt == ".متصدرين":
            await self._show_leaderboard(event)
        
        # الذكاء الاصطناعي
        elif txt.startswith(".سؤال "):
            await self._handle_ai_question(event, txt)
        elif txt.startswith(".اصنع صورة "):
            await self._handle_create_image(event, txt)
        
        # باقي الأوامر...
        else:
            # البحث في الأوامر العامة
            await self._handle_general_commands(event, txt)
    
    async def _show_partner_system(self, event):
        """عرض نظام الشركاء"""
        await event.edit("""
🤝 **نظام الشركاء والإحالة - ربح من السورس!**

💰 *كيفية الربح:*
1. شارك رابط الإحالة الخاص بك
2. كل صديق ينضم = 10% من اشتراكه الأول
3. كل 10 إحالات = ترقية للمستوى التالي
4. اربح حتى 30% من كل اشتراك

🏆 *المستويات والأرباح:*
• 🥉 برونز: 10% عمولة
• 🥈 فضة: 15% عمولة (بعد 10 إحالات)
• 🥇 ذهب: 20% عمولة (بعد 50 إحالة)
• 💎 بلاتينيوم: 30% عمولة (بعد 100 إحالة)

🎁 *مكافآت المدعوين:*
• 3 أيام مجانية إضافية
• 100 نقطة هدية
• دعم فني متميز

📊 *أوامر النظام:*
• `.احالة` - رابط الإحالة الخاص بك
• `.احصائياتي` - إحصائياتك كشريك
• `.متصدرين` - أفضل الشركاء
• `.سحب [مبلغ]` - سحب أرباحك
• `.ربح` - طرق الربح المتاحة

🚀 *ابدأ الربح الآن!*
        """)
    
    async def _show_referral_link(self, event):
        """عرض رابط الإحالة"""
        referral_data = self.referral_system.generate_referral_link(self.user_id)
        
        message = f"""
🔗 *رابط الإحالة الخاص بك:*

🎫 *كود الإحالة:* 
`{referral_data['referral_code']}`

🔗 *الرابط المباشر:*
{referral_data['telegram_link']}

📱 *QR Code:*
{referral_data['qr_code']}

📤 *شارك الرابط واربح!*
        """
        await event.edit(message)
    
    async def _show_partner_stats(self, event):
        """عرض إحصائيات الشريك"""
        stats = self.referral_system.get_partner_stats(self.user_id)
        
        if "error" in stats:
            await event.edit("⚠️ **أنت لست شريكاً بعد! استخدم `.احالة` للانضمام للنظام**")
            return
        
        # توليد شريط التقدم
        def generate_progress_bar(percentage, length=10):
            filled = int(percentage / 100 * length)
            empty = length - filled
            bar = "🟩" * filled + "⬜" * empty
            return f"{bar} {percentage:.1f}%"
        
        progress_bar = generate_progress_bar(stats.get('progress_to_next_tier', {}).get('progress', 0))
        
        message = f"""
📊 *إحصائيات الشريك الخاص بك*

🎖️ *المستوى:* {stats['tier']} 
📈 *نسبة العمولة:* {stats['commission_rate']}%

👥 *الإحالات:*
• إجمالي المدعوين: {stats['total_invites']}
• الإحالات الناجحة: {stats['successful_invites']}
• معدل التحويل: {stats['conversion_rate']:.1f}%
• إحالات اليوم: {stats['daily_invites']}

💰 *الأرباح:*
• إجمالي الأرباح: ${stats['total_earnings']:.2f}
• الرصيد المعلق: ${stats['pending_earnings']:.2f}
• الحد الأدنى للسحب: $10.00

🎯 *التقدم للمستوى التالي ({stats.get('next_tier', '--')}):*
{progress_bar}
        """
        
        await event.edit(message)
    
    async def _show_leaderboard(self, event):
        """عرض لوحة المتصدرين"""
        leaderboard = self.referral_system.generate_leaderboard(10)
        
        message = "🏆 *لوحة متصدرين الشركاء*\n\n"
        
        for entry in leaderboard:
            message += f"{entry['rank']}. {entry['badge']} ID: {entry['user_id']}\n"
            message += f"   💰 ${entry['earnings']:.2f} | 👥 {entry['invites']} إحالة\n"
        
        # البحث عن ترتيب المستخدم
        all_partners = self.referral_system.generate_leaderboard(1000)
        user_rank = None
        
        for i, entry in enumerate(all_partners, 1):
            if entry['user_id'] == self.user_id:
                user_rank = i
                break
        
        if user_rank:
            message += f"\n🎯 *ترتيبك:* #{user_rank}"
        
        await event.edit(message)
    
    async def _handle_ai_question(self, event, txt: str):
        """معالجة سؤال الذكاء الاصطناعي"""
        await event.edit("🤔 **جارِ التفكير...**")
        question = txt.split(maxsplit=1)[1]
        
        response = await self.ai.chat(self.user_id, question)
        
        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for i, part in enumerate(parts):
                if i == 0:
                    await event.edit(f"🧠 **إجابة الذكاء الاصطناعي (الجزء {i+1}):**\n\n{part}")
                else:
                    await event.respond(f"🧠 **استكمال الإجابة (الجزء {i+1}):**\n\n{part}")
        else:
            await event.edit(f"🧠 **إجابة الذكاء الاصطناعي:**\n\n{response}")
    
    async def _handle_create_image(self, event, txt: str):
        """معالجة إنشاء صورة"""
        await event.edit("🎨 **جارِ إنشاء الصورة...**")
        description = txt.split(maxsplit=1)[1]
        
        image_url = await self.ai.generate_image_writecream(description)
        if image_url:
            await event.delete()
            try:
                await self.client.send_file(
                    "me", 
                    image_url, 
                    caption=f"🖼 **تم إنشاء الصورة بنجاح!**\n📝 الوصف: {description}"
                )
            except:
                pass
            await event.respond(
                file=image_url, 
                caption=f"🖼 **تم إنشاء الصورة بنجاح!**\n📝 الوصف: {description}"
            )
        else:
            await event.edit("❌ **فشل إنشاء الصورة.**")
    
    async def _handle_general_commands(self, event, txt: str):
        """معالجة الأوامر العامة"""
        # الأوامر الأساسية
        if txt == ".فحص":
            start = datetime.now()
            await event.edit("📶 Pinging...")
            end = datetime.now()
            ms = (end - start).microseconds / 1000
            await event.edit(f"🚀 **Pong!**\nLatency: `{ms}ms`")
        
        elif txt == ".ايدي":
            me = await self.client.get_me()
            await event.edit(f"🆔 **ID:** `{me.id}`\n👤 **Name:** {me.first_name}")
        
        # المزيد من الأوامر...
    
    async def _button_handler(self, event):
        """معالج أحداث الأزرار"""
        data = event.data.decode('utf-8')
        chat_id = event.chat_id
        
        if data == "regen_image":
            description = self.image_cache.get(chat_id)
            if description:
                await event.edit("🔄 **جارِ إعادة إنشاء الصورة...**")
                image_file = await self.generate_image_flux_max(description)
                if image_file:
                    await event.delete()
                    keyboard = [[Button.inline("🔄 توليد مرة أخرى", b"regen_image")]]
                    await event.respond(
                        file=image_file, 
                        caption=f"🖼 **تم إعادة إنشاء الصورة!**\n📝 الوصف: {description}", 
                        buttons=keyboard
                    )
                    try:
                        os.remove(image_file)
                    except:
                        pass
                else:
                    await event.edit("❌ **فشل إعادة إنشاء الصورة.**")
            else:
                await event.edit("❌ **لم يتم العثور على الوصف.**")