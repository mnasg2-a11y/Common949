"""
نظام الذكاء الاصطناعي Gemini المتقدم
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from langdetect import detect
from deep_translator import GoogleTranslator

from src.config.settings import GEMINI_API_KEY, GEMINI_API_URL
from src.utils.logger import get_logger

logger = get_logger(__name__)

class GeminiAI:
    """فئة الذكاء الاصطناعي Gemini المتقدم"""
    
    def __init__(self, userbot_instance=None):
        self.conversation_history = {}
        self.headers = {
            'User-Agent': "Ktor client", 
            'Accept': "application/json", 
            'Content-Type': "application/json", 
            'x-goog-api-key': GEMINI_API_KEY, 
            'x-goog-api-client': "gl-kotlin/2.2.0-ai fire/16.5.0", 
            'x-firebase-appid': "1:652803432695:android:c4341db6033e62814f33f2", 
            'x-firebase-appversion': "79", 
            'x-firebase-appcheck': "eyJlcnJvciI6IlVOS05PV05fRVJST1IifQ=="
        }
        self.userbot = userbot_instance
        self.commands_list = self._load_commands()
        logger.info("✅ تم تهيئة الذكاء الاصطناعي Gemini المتقدم")
    
    def _load_commands(self) -> Dict[str, str]:
        """تحميل قائمة الأوامر"""
        return {
            # نظام الشركاء
            'شركاء': "🤝 **نظام الشركاء:**\nاستخدم `.شركاء` لعرض نظام الشركاء والإحالة",
            'احالة': "🔗 **رابط الإحالة:**\nاستخدم `.احالة` للحصول على رابط الإحالة",
            
            # الذكاء الاصطناعي
            'سؤال': "🤔 **أمر السؤال:**\nاستخدم `.سؤال [سؤالك]` للاستفسار",
            'اصنع صورة': "🎨 **أمر صنع الصور:**\nاستخدم `.اصنع صورة [وصف]` لإنشاء صورة",
            
            # ... باقي الأوامر
        }
    
    async def chat(self, user_id: int, user_message: str, system_prompt: str = "أنت مساعد ذكي ومفيد.") -> str:
        """محادثة ذكية مع Gemini AI"""
        try:
            # تحليل الأوامر
            command_response = await self._analyze_command(user_id, user_message)
            if command_response:
                return command_response
            
            # التحقق من سؤال المطور
            if any(keyword in user_message.lower() for keyword in ['منو طورك', 'من صنعك', 'المطور']):
                return "🛠 **المطور:** حسين\n👤 **يوزر المطور:** @iomk0\n🔥 **سورس كومن الذكي**"
            
            # إعداد التاريخ
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            history = self.conversation_history[user_id][-4:]
            full_prompt = f"System: {system_prompt}\n\n"
            
            for msg in history:
                role = "User" if msg["role"] == "user" else "Assistant"
                full_prompt += f"{role}: {msg['content']}\n"
            
            full_prompt += f"User: {user_message}\nAssistant:"
            
            # تحضير البيانات
            payload = {
                "model": "projects/gemmy-ai-bdc03/locations/us-central1/publishers/google/models/gemini-2.0-flash-lite", 
                "contents": [{
                    "role": "user", 
                    "parts": [{"text": full_prompt}]
                }]
            }
            
            # إرسال الطلب
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    GEMINI_API_URL,
                    json=payload,
                    headers=self.headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'candidates' in result and result['candidates']:
                            ai_reply = result['candidates'][0]['content']['parts'][0]['text'].strip()
                            
                            # إضافة النقطة للرد
                            if not ai_reply.startswith("•") and not ai_reply.startswith("."):
                                ai_reply = f"• {ai_reply}"
                            
                            # تحديث التاريخ
                            self.conversation_history[user_id].extend([
                                {"role": "user", "content": user_message},
                                {"role": "assistant", "content": ai_reply}
                            ])
                            
                            return ai_reply
                        else:
                            return "• 🧠 **الجواب:** لم يتم الحصول على رد من الذكاء الاصطناعي."
                    else:
                        return f"• ⚠️ **خطأ في الاتصال:** {response.status}"
        
        except Exception as e:
            logger.error(f"AI Exception: {e}")
            return "• 🧠 **الجواب:** حدث خطأ غير متوقع. حاول مرة أخرى."
    
    async def _analyze_command(self, user_id: int, message: str) -> Optional[str]:
        """تحليل الأوامر في الرسالة"""
        message_lower = message.lower()
        
        # البحث عن الأوامر
        for cmd, response in self.commands_list.items():
            if cmd in message_lower:
                return response
        
        # إذا طلب صنع صورة
        if any(keyword in message_lower for keyword in ['اصنع صورة', 'انشاء صورة', 'صنع صورة']):
            return "🎨 **أريد إنشاء صورة لك!**\nيرجى إرسال وصف مفصل للصورة..."
        
        return None
    
    async def generate_image_writecream(self, text: str) -> Optional[str]:
        """صنع صورة باستخدام writecream"""
        try:
            # ترجمة النص للإنجليزية
            dt_lg = detect(text)
            if dt_lg != 'en':
                tr_tx = GoogleTranslator(source='auto', target='en').translate(text)
            else:
                tr_tx = text
            
            params = {
                'prompt': tr_tx,
                'aspect_ratio': 'Select Aspect Ratio',
                'link': 'writecream.com',
            }
            
            headers = {
                'accept': '/',
                'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
                'origin': 'https://www.writecream.com',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://1yjs1yldj7.execute-api.us-east-1.amazonaws.com/default/ai_image',
                    params=params,
                    headers=headers,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        rp_js = await response.json()
                        return rp_js.get("image_link")
                    else:
                        logger.error(f"Writecream API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error generating image (writecream): {e}")
            return None
    
    async def generate_code(self, user_id: int, language: str, description: str) -> str:
        """توليد كود برمجي"""
        system_prompt = f"أنت مبرمج خبير بلغة {language}. اكتب كود ممتاز وواضح"
        return await self.chat(user_id, f"اكتب كود {language} لـ: {description}", system_prompt)
    
    async def translate_text(self, user_id: int, text: str, target_lang: str = 'arabic') -> str:
        """ترجمة ذكية"""
        system_prompt = f"أنت مترجم محترف. ترجم النص بدقة إلى {target_lang}"
        return await self.chat(user_id, f"ترجم النص التالي إلى {target_lang}: {text}", system_prompt)
    
    async def summarize_text(self, user_id: int, text: str) -> str:
        """تلخيص النص"""
        system_prompt = "أنت مختص في تلخيص النصوص. لخص النص بشكل مختصر ومفيد."
        return await self.chat(user_id, f"لخص النص التالي: {text}", system_prompt)
    
    async def solve_problem(self, user_id: int, problem: str) -> str:
        """حل المشكلات"""
        system_prompt = "أنت خبير في حل المشكلات. قدم حلاً عملياً ومفصلاً للمشكلة."
        return await self.chat(user_id, f"حل المشكلة التالية: {problem}", system_prompt)