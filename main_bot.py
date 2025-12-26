# main_bot.py - السورس الفعلي
import os
import asyncio
import json
from datetime import datetime
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from dotenv import load_dotenv

# تحميل الإعدادات
load_dotenv()

class CommonBot:
    """البوت الأساسي"""
    
    def __init__(self):
        self.api_id = int(os.getenv("API_ID"))
        self.api_hash = os.getenv("API_HASH")
        self.bot_token = os.getenv("BOT_TOKEN")
        self.client = None
        
    async def start(self):
        """بدء البوت"""
        print("🚀 جاري بدء تشغيل سورس كومن...")
        
        # إنشاء العميل
        self.client = TelegramClient(
            StringSession(), 
            self.api_id, 
            self.api_hash
        )
        
        # بدء التشغيل
        await self.client.start(bot_token=self.bot_token)
        
        # الحصول على معلومات البوت
        me = await self.client.get_me()
        print(f"✅ البوت شغال: @{me.username}")
        print(f"🆔 آيدي البوت: {me.id}")
        
        # إضافة المعالجات
        self.client.add_event_handler(self.handle_start, events.NewMessage(pattern='/start'))
        self.client.add_event_handler(self.handle_message, events.NewMessage)
        
        print("🎉 البوت جاهز للاستخدام!")
        print(f"🔗 رابط البوت: https://t.me/{me.username}")
        
        # تشغيل حتى الإيقاف
        await self.client.run_until_disconnected()
    
    async def handle_start(self, event):
        """معالج أمر /start"""
        user = await event.get_sender()
        
        welcome_msg = f"""
👋 **أهلاً بك {user.first_name} في سورس كومن الذكي!**

🧠 **المميزات:**
• ذكاء اصطناعي متقدم
• نظام شركاء وربح
• أكثر من 300 أمر
• تحميل من اليوتيوب
• إنشاء صور ذكية

💰 **ابدأ الربح الآن:**
`.شركاء` - عرض نظام الشركاء
`.احالة` - رابط الإحالة الخاص بك

⚡ **الأوامر السريعة:**
`.الاوامر` - جميع الأوامر
`.سؤال` - محادثة مع الذكاء الاصطناعي
`.فحص` - فحص سرعة البوت

👨‍💻 **المطور:** @iomk0
📢 **القناة:** @iomk3
"""
        
        await event.respond(welcome_msg)
    
    async def handle_message(self, event):
        """معالج الرسائل العادية"""
        if not event.text:
            return
        
        text = event.text.strip()
        user = await event.get_sender()
        
        # نظام الشركاء
        if text == ".شركاء":
            await event.respond("""
🤝 **نظام الشركاء والإحالة**

💰 **كيف تربح:**
1. شارك رابط الإحالة
2. كل صديق ينضم = 10% من اشتراكه
3. اربح حتى 30%

🔗 **لحصول على رابطك:**
`.احالة`

📊 **لرؤية إحصائياتك:**
`.احصائياتي`
""")
        
        # الذكاء الاصطناعي
        elif text.startswith(".سؤال "):
            question = text[6:]
            await event.respond(f"🧠 **سؤال:** {question}\n\n🤔 **جاري التفكير...**")
            await asyncio.sleep(1)
            await event.respond("• الذكاء الاصطناعي قيد التطوير\n• سيكون جاهزاً قريباً!")
        
        # فحص البوت
        elif text == ".فحص":
            await event.respond("⚡ **Pong!**\n✅ البوت شغال 100%")
        
        # الأوامر
        elif text == ".الاوامر":
            await event.respond("""
📜 **أهم الأوامر:**

💰 **نظام الشركاء:**
`.شركاء` - نظام الربح
`.احالة` - رابط الإحالة
`.احصائياتي` - إحصائياتك

🧠 **الذكاء الاصطناعي:**
`.سؤال` - محادثة ذكية
`.اصنع صورة` - إنشاء صور

⚡ **أوامر سريعة:**
`.فحص` - فحص البوت
`.ايدي` - آيديك
`.تسليه` - ألعاب وتسلية
""")

async def main():
    """الدالة الرئيسية"""
    bot = CommonBot()
    await bot.start()

if __name__ == "__main__":
    print("="*50)
    print("🤖 سورس كومن الذكي - الإصدار البسيط")
    print("="*50)
    
    asyncio.run(main())
