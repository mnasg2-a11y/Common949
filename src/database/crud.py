"""
عمليات CRUD على قاعدة البيانات
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from src.database.connection import db_connection
from src.database.models import User, Subscription, Referral, Earning, Session

class BaseCRUD:
    """الفئة الأساسية لعمليات CRUD"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db = db_connection
    
    def create(self, data: Dict[str, Any]) -> int:
        """إنشاء سجل جديد"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        values = tuple(data.values())
        
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, values)
            return cursor.lastrowid
    
    def read(self, record_id: int) -> Optional[Dict[str, Any]]:
        """قراءة سجل"""
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        results = self.db.execute_query(query, (record_id,))
        
        if results:
            return dict(results[0])
        return None
    
    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        """تحديث سجل"""
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = tuple(data.values()) + (record_id,)
        
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        
        rows_affected = self.db.execute_update(query, values)
        return rows_affected > 0
    
    def delete(self, record_id: int) -> bool:
        """حذف سجل"""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        rows_affected = self.db.execute_update(query, (record_id,))
        return rows_affected > 0
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """الحصول على جميع السجلات"""
        query = f"SELECT * FROM {self.table_name} LIMIT ? OFFSET ?"
        results = self.db.execute_query(query, (limit, offset))
        return [dict(row) for row in results]
    
    def count(self) -> int:
        """عدد السجلات"""
        query = f"SELECT COUNT(*) as count FROM {self.table_name}"
        results = self.db.execute_query(query)
        return results[0]['count'] if results else 0

class UserCRUD(BaseCRUD):
    """عمليات CRUD للمستخدمين"""
    
    def __init__(self):
        super().__init__('users')
    
    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """الحصول على مستخدم بواسطة معرف تليجرام"""
        query = "SELECT * FROM users WHERE telegram_id = ?"
        results = self.db.execute_query(query, (telegram_id,))
        
        if results:
            return User.from_dict(dict(results[0]))
        return None
    
    def get_by_referral_code(self, referral_code: str) -> Optional[User]:
        """الحصول على مستخدم بواسطة كود الإحالة"""
        query = "SELECT * FROM users WHERE referral_code = ?"
        results = self.db.execute_query(query, (referral_code,))
        
        if results:
            return User.from_dict(dict(results[0]))
        return None
    
    def update_balance(self, telegram_id: int, amount: float) -> bool:
        """تحديث رصيد المستخدم"""
        query = "UPDATE users SET balance = balance + ?, total_earnings = total_earnings + ? WHERE telegram_id = ?"
        rows_affected = self.db.execute_update(query, (amount, max(amount, 0), telegram_id))
        return rows_affected > 0
    
    def update_tier(self, telegram_id: int, tier: str) -> bool:
        """تحديث مستوى المستخدم"""
        query = "UPDATE users SET tier = ? WHERE telegram_id = ?"
        rows_affected = self.db.execute_update(query, (tier, telegram_id))
        return rows_affected > 0

class SubscriptionCRUD(BaseCRUD):
    """عمليات CRUD للاشتراكات"""
    
    def __init__(self):
        super().__init__('subscriptions')
    
    def get_active_by_user(self, user_id: int) -> Optional[Subscription]:
        """الحصول على اشتراك نشط للمستخدم"""
        query = '''
            SELECT * FROM subscriptions 
            WHERE user_id = ? AND status = 'active' AND end_date > datetime('now')
            ORDER BY end_date DESC
            LIMIT 1
        '''
        results = self.db.execute_query(query, (user_id,))
        
        if results:
            return Subscription.from_dict(dict(results[0]))
        return None
    
    def get_all_active(self) -> List[Subscription]:
        """الحصول على جميع الاشتراكات النشطة"""
        query = '''
            SELECT * FROM subscriptions 
            WHERE status = 'active' AND end_date > datetime('now')
            ORDER BY end_date
        '''
        results = self.db.execute_query(query)
        return [Subscription.from_dict(dict(row)) for row in results]
    
    def expire_old_subscriptions(self):
        """انتهاء صلاحية الاشتراكات القديمة"""
        query = "UPDATE subscriptions SET status = 'expired' WHERE end_date <= datetime('now') AND status = 'active'"
        rows_affected = self.db.execute_update(query)
        return rows_affected

class ReferralCRUD(BaseCRUD):
    """عمليات CRUD للإحالات"""
    
    def __init__(self):
        super().__init__('referrals')
    
    def get_by_referrer(self, referrer_id: int) -> List[Referral]:
        """الحصول على إحالات الشريك"""
        query = "SELECT * FROM referrals WHERE referrer_id = ? ORDER BY created_at DESC"
        results = self.db.execute_query(query, (referrer_id,))
        return [Referral.from_dict(dict(row)) for row in results]
    
    def get_by_referred(self, referred_id: int) -> Optional[Referral]:
        """الحصول على إحالة للمدعو"""
        query = "SELECT * FROM referrals WHERE referred_id = ? LIMIT 1"
        results = self.db.execute_query(query, (referred_id,))
        
        if results:
            return Referral.from_dict(dict(results[0]))
        return None
    
    def get_converted_count(self, referrer_id: int) -> int:
        """عدد الإحالات المحولة"""
        query = "SELECT COUNT(*) as count FROM referrals WHERE referrer_id = ? AND status = 'converted'"
        results = self.db.execute_query(query, (referrer_id,))
        return results[0]['count'] if results else 0
    
    def get_total_commission(self, referrer_id: int) -> float:
        """إجمالي العمولات"""
        query = "SELECT SUM(commission_amount) as total FROM referrals WHERE referrer_id = ? AND status = 'converted'"
        results = self.db.execute_query(query, (referrer_id,))
        return results[0]['total'] or 0.0 if results else 0.0

class EarningCRUD(BaseCRUD):
    """عمليات CRUD للأرباح"""
    
    def __init__(self):
        super().__init__('earnings')
    
    def get_by_user(self, user_id: int, limit: int = 50) -> List[Earning]:
        """الحصول على أرباح المستخدم"""
        query = "SELECT * FROM earnings WHERE user_id = ? ORDER BY created_at DESC LIMIT ?"
        results = self.db.execute_query(query, (user_id, limit))
        return [Earning.from_dict(dict(row)) for row in results]
    
    def get_total_by_user(self, user_id: int) -> float:
        """إجمالي أرباح المستخدم"""
        query = "SELECT SUM(amount) as total FROM earnings WHERE user_id = ?"
        results = self.db.execute_query(query, (user_id,))
        return results[0]['total'] or 0.0 if results else 0.0
    
    def get_today_earnings(self, user_id: int) -> float:
        """أرباح اليوم"""
        query = "SELECT SUM(amount) as total FROM earnings WHERE user_id = ? AND DATE(created_at) = DATE('now')"
        results = self.db.execute_query(query, (user_id,))
        return results[0]['total'] or 0.0 if results else 0.0

class SessionCRUD(BaseCRUD):
    """عمليات CRUD للجلسات"""
    
    def __init__(self):
        super().__init__('sessions')
    
    def get_by_user(self, user_id: int) -> List[Session]:
        """الحصول على جلسات المستخدم"""
        query = "SELECT * FROM sessions WHERE user_id = ? ORDER BY last_active DESC"
        results = self.db.execute_query(query, (user_id,))
        return [Session.from_dict(dict(row)) for row in results]
    
    def update_last_active(self, session_id: int):
        """تحديث وقت النشاط الأخير"""
        query = "UPDATE sessions SET last_active = datetime('now') WHERE id = ?"
        self.db.execute_update(query, (session_id,))
    
    def cleanup_inactive(self, timeout_minutes: int = 30):
        """تنظيف الجلسات غير النشطة"""
        query = "DELETE FROM sessions WHERE datetime('now', ?) > last_active"
        params = (f'-{timeout_minutes} minutes',)
        rows_affected = self.db.execute_update(query, params)
        return rows_affected