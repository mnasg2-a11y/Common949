"""
نظام الشركاء والإحالة المتقدم
"""

import sqlite3
import hashlib
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from src.config.settings import (
    REFERRAL_DB, COMMISSION_RATES, 
    INVITEE_REWARDS, TIER_REQUIREMENTS,
    TIER_BADGES
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AdvancedReferralSystem:
    """نظام الشركاء والإحالة المتقدم"""
    
    def __init__(self):
        self.db_path = REFERRAL_DB
        self.commission_rates = COMMISSION_RATES
        self.invitee_rewards = INVITEE_REWARDS
        self.tier_requirements = TIER_REQUIREMENTS
        self.bot_username = "comman_bot"
        self.init_database()
    
    def init_database(self):
        """تهيئة قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول الشركاء
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS partners (
                user_id INTEGER PRIMARY KEY,
                referral_code TEXT UNIQUE,
                tier TEXT DEFAULT 'bronze',
                total_invites INTEGER DEFAULT 0,
                successful_invites INTEGER DEFAULT 0,
                total_earnings REAL DEFAULT 0.0,
                pending_earnings REAL DEFAULT 0.0,
                join_date TIMESTAMP,
                last_active TIMESTAMP
            )
        ''')
        
        # جدول الإحالات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                referral_id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                referral_code TEXT,
                status TEXT DEFAULT 'pending',
                commission_amount REAL DEFAULT 0.0,
                conversion_date TIMESTAMP,
                created_at TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES partners (user_id)
            )
        ''')
        
        # جدول المدفوعات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payouts (
                payout_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                method TEXT,
                status TEXT DEFAULT 'pending',
                transaction_id TEXT,
                requested_at TIMESTAMP,
                processed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES partners (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ تم تهيئة قاعدة بيانات نظام الشركاء")
    
    def generate_referral_link(self, user_id: int, campaign: str = "default") -> Dict:
        """إنشاء رابط إحالة فريد"""
        referral_code = self._create_unique_code(user_id)
        telegram_link = f"https://t.me/{self.bot_username}?start=ref_{referral_code}"
        
        qr_data = {
            "telegram_link": telegram_link,
            "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={telegram_link}"
        }
        
        # حفظ في قاعدة البيانات
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO partners (user_id, referral_code, join_date, last_active)
            VALUES (?, ?, ?, ?)
        ''', (user_id, referral_code, datetime.now(), datetime.now()))
        
        cursor.execute('''
            UPDATE partners SET referral_code = ?, last_active = ?
            WHERE user_id = ?
        ''', (referral_code, datetime.now(), user_id))
        
        conn.commit()
        conn.close()
        
        return {
            "referral_code": referral_code,
            "telegram_link": telegram_link,
            "qr_code": qr_data["qr_code_url"],
            "promo_text": self._generate_promo_text(user_id, referral_code),
            "stats_link": f"t.me/{self.bot_username}?start=stats_{user_id}"
        }
    
    def _create_unique_code(self, user_id: int) -> str:
        """إنشاء كود إحالة فريد"""
        timestamp = int(datetime.now().timestamp())
        base_string = f"{user_id}_{timestamp}_{random.randint(1000, 9999)}"
        hash_object = hashlib.md5(base_string.encode())
        short_hash = hash_object.hexdigest()[:8].upper()
        return f"COMMAN-{short_hash}"
    
    def _generate_promo_text(self, user_id: int, referral_code: str) -> str:
        """نص ترويجي جاهز للمشاركة"""
        promo_templates = [
            f"""🔥 *سورس كومن - أقوى سورس تليجرام مع ذكاء اصطناعي!*

🚀 *المميزات:*
• 🧠 ذكاء اصطناعي متكامل
• 🎬 صناعة فيديوهات احترافية
• 💻 مبرمج ذكي داخلي

💰 *انضم باستخدام رابطي واحصل على:*
• 3 أيام تجربة مجانية إضافية
• 100 نقطة هدية
• دعم فني متميز

🔗 *رابط الانضمام:* t.me/comman_bot?start=ref_{referral_code}
🎯 *كود الإحالة:* `{referral_code}`"""
        ]
        
        return random.choice(promo_templates)
    
    def track_referral(self, referral_code: str, new_user_id: int) -> Dict:
        """تتبع الإحالة الجديدة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # البحث عن صاحب كود الإحالة
        cursor.execute('''
            SELECT user_id, tier FROM partners 
            WHERE referral_code = ?
        ''', (referral_code,))
        
        result = cursor.fetchone()
        
        if not result:
            return {"success": False, "message": "كود إحالة غير صحيح"}
        
        referrer_id, tier = result
        
        # تجنب الإحالة الذاتية
        if referrer_id == new_user_id:
            return {"success": False, "message": "لا يمكن استخدام رابطك الخاص"}
        
        # التحقق من استخدام رابط سابق
        cursor.execute('''
            SELECT referred_id FROM referrals 
            WHERE referred_id = ?
        ''', (new_user_id,))
        
        if cursor.fetchone():
            return {"success": False, "message": "هذا المستخدم استخدم رابط إحالة مسبقاً"}
        
        # تسجيل الإحالة
        cursor.execute('''
            INSERT INTO referrals 
            (referrer_id, referred_id, referral_code, created_at)
            VALUES (?, ?, ?, ?)
        ''', (referrer_id, new_user_id, referral_code, datetime.now()))
        
        # تحديث إحصائيات الشريك
        cursor.execute('''
            UPDATE partners 
            SET total_invites = total_invites + 1,
                last_active = ?
            WHERE user_id = ?
        ''', (datetime.now(), referrer_id))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "referrer_id": referrer_id,
            "new_user_id": new_user_id,
            "tier": tier,
            "message": "تم تسجيل الإحالة بنجاح"
        }
    
    def calculate_commission(self, purchase_amount: float, tier: str) -> float:
        """حساب العمولة حسب المستوى"""
        rate = self.commission_rates.get(tier, 10)
        return (purchase_amount * rate) / 100
    
    def process_conversion(self, referred_id: int, purchase_amount: float = 0.0) -> Dict:
        """معالجة تحويل المدعو"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # البحث عن الإحالة
        cursor.execute('''
            SELECT referral_id, referrer_id, referral_code, status 
            FROM referrals 
            WHERE referred_id = ? AND status = 'pending'
        ''', (referred_id,))
        
        referral = cursor.fetchone()
        
        if not referral:
            return {"success": False, "message": "لا توجد إحالة معلقة"}
        
        referral_id, referrer_id, referral_code, status = referral
        
        # الحصول على معلومات الشريك
        cursor.execute('''
            SELECT tier FROM partners WHERE user_id = ?
        ''', (referrer_id,))
        
        tier_result = cursor.fetchone()
        tier = tier_result[0] if tier_result else "bronze"
        
        # حساب العمولة
        commission = self.calculate_commission(purchase_amount, tier)
        
        # تحديث الإحالة كمكتملة
        cursor.execute('''
            UPDATE referrals 
            SET status = 'converted',
                commission_amount = ?,
                conversion_date = ?
            WHERE referral_id = ?
        ''', (commission, datetime.now(), referral_id))
        
        # تحديث إحصائيات الشريك
        cursor.execute('''
            UPDATE partners 
            SET successful_invites = successful_invites + 1,
                total_earnings = total_earnings + ?,
                pending_earnings = pending_earnings + ?,
                last_active = ?
            WHERE user_id = ?
        ''', (commission, commission, datetime.now(), referrer_id))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "referrer_id": referrer_id,
            "commission": commission,
            "tier": tier,
            "message": f"تم تحويل الإحالة واكتمال العمولة: {commission}$"
        }
    
    def get_partner_stats(self, user_id: int) -> Dict:
        """الحصول على إحصائيات الشريك"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tier, total_invites, successful_invites, 
                   total_earnings, pending_earnings, join_date
            FROM partners 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return {"error": "شريك غير مسجل"}
        
        tier, total_invites, successful_invites, total_earnings, pending_earnings, join_date = result
        
        # الحصول على الإحالات الأخيرة
        cursor.execute('''
            SELECT referred_id, status, created_at, commission_amount
            FROM referrals 
            WHERE referrer_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id,))
        
        recent_referrals = [
            {
                "referred_id": row[0],
                "status": row[1],
                "date": row[2],
                "commission": row[3] or 0.0
            }
            for row in cursor.fetchall()
        ]
        
        # حساب التحويلات اليومية
        today = datetime.now().date()
        cursor.execute('''
            SELECT COUNT(*) FROM referrals 
            WHERE referrer_id = ? 
            AND DATE(created_at) = ?
        ''', (user_id, today))
        
        daily_invites = cursor.fetchone()[0]
        
        conn.close()
        
        # حساب التقدم للمستوى التالي
        progress = self._calculate_tier_progress(user_id, tier)
        
        return {
            "tier": tier,
            "total_invites": total_invites,
            "successful_invites": successful_invites,
            "total_earnings": total_earnings,
            "pending_earnings": pending_earnings,
            "join_date": join_date,
            "daily_invites": daily_invites,
            "conversion_rate": (successful_invites / total_invites * 100) if total_invites > 0 else 0,
            "recent_referrals": recent_referrals,
            "commission_rate": self.commission_rates.get(tier, 10),
            "next_tier": self._get_next_tier(tier),
            "progress_to_next_tier": progress
        }
    
    def _get_next_tier(self, current_tier: str) -> Optional[str]:
        """الحصول على المستوى التالي"""
        tiers = list(self.commission_rates.keys())
        current_index = tiers.index(current_tier) if current_tier in tiers else -1
        
        if current_index < len(tiers) - 1:
            return tiers[current_index + 1]
        return None
    
    def _calculate_tier_progress(self, user_id: int, current_tier: str) -> Dict:
        """حساب التقدم نحو المستوى التالي"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT successful_invites, total_earnings 
            FROM partners WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {"progress": 0, "requirements": {}}
        
        current_invites, current_earnings = result
        next_tier = self._get_next_tier(current_tier)
        
        if not next_tier:
            return {"progress": 100, "requirements": {}}
        
        req_invites = self.tier_requirements[next_tier]["invites"]
        req_earnings = self.tier_requirements[next_tier]["earnings"]
        
        invite_progress = min((current_invites / req_invites * 100) if req_invites > 0 else 100, 100)
        earning_progress = min((current_earnings / req_earnings * 100) if req_earnings > 0 else 100, 100)
        
        overall_progress = (invite_progress + earning_progress) / 2
        
        return {
            "progress": overall_progress,
            "invite_progress": invite_progress,
            "earning_progress": earning_progress,
            "required_invites": req_invites,
            "required_earnings": req_earnings,
            "current_invites": current_invites,
            "current_earnings": current_earnings,
            "next_tier": next_tier
        }
    
    def generate_leaderboard(self, limit: int = 20) -> List[Dict]:
        """إنشاء لوحة المتصدرين"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, total_earnings, successful_invites, tier
            FROM partners 
            WHERE successful_invites > 0
            ORDER BY total_earnings DESC
            LIMIT ?
        ''', (limit,))
        
        leaderboard = []
        rank = 1
        
        for row in cursor.fetchall():
            user_id, earnings, invites, tier = row
            
            leaderboard.append({
                "rank": rank,
                "user_id": user_id,
                "earnings": earnings,
                "invites": invites,
                "tier": tier,
                "badge": TIER_BADGES.get(tier, "👤")
            })
            rank += 1
        
        conn.close()
        return leaderboard