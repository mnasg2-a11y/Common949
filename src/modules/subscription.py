"""
نظام الاشتراكات والإدارة
"""

import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.config.settings import (
    SUBSCRIPTIONS_FILE, TRIALS_FILE, 
    ACTIVATION_CODES_FILE, USER_INSTALLATIONS_FILE,
    SUBSCRIPTION_PERIODS, SUBSCRIPTION_TYPES
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SubscriptionManager:
    """مدير نظام الاشتراكات"""
    
    def __init__(self):
        self.subscriptions = self._load_json(SUBSCRIPTIONS_FILE)
        self.trials = self._load_json(TRIALS_FILE)
        self.activation_codes = self._load_json(ACTIVATION_CODES_FILE)
        self.user_installations = self._load_json(USER_INSTALLATIONS_FILE)
        
        logger.info("✅ تم تهيئة مدير الاشتراكات")
    
    def _load_json(self, filename: str) -> Dict:
        """تحميل ملف JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, filename: str, data: Dict):
        """حفظ ملف JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
    
    def check_subscription(self, user_id: str) -> Dict:
        """التحقق من صلاحية الاشتراك"""
        user_id = str(user_id)
        
        # التحقق من الاشتراكات المدفوعة
        if user_id in self.subscriptions:
            end_date_str = self.subscriptions[user_id]["end_date"]
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            
            if datetime.now() < end_date:
                days_left = (end_date - datetime.now()).days
                return {
                    "active": True, 
                    "type": self.subscriptions[user_id]["type"], 
                    "days_left": days_left,
                    "end_date": end_date_str
                }
        
        # التحقق من التجارب المجانية
        if user_id in self.trials:
            end_date_str = self.trials[user_id]["end_date"]
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            
            if datetime.now() < end_date:
                days_left = (end_date - datetime.now()).days
                return {
                    "active": True, 
                    "type": "trial", 
                    "days_left": days_left,
                    "end_date": end_date_str
                }
        
        return {"active": False}
    
    def activate_trial(self, user_id: str, days: int = 3) -> datetime:
        """تفعيل تجربة مجانية"""
        user_id = str(user_id)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        self.trials[user_id] = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        self._save_json(TRIALS_FILE, self.trials)
        logger.info(f"✅ تم تفعيل تجربة لمدة {days} أيام للمستخدم: {user_id}")
        
        return end_date
    
    def activate_subscription(self, user_id: str, days: int, sub_type: str) -> datetime:
        """تفعيل اشتراك مدفوع"""
        user_id = str(user_id)
        end_date = datetime.now() + timedelta(days=days)
        
        self.subscriptions[user_id] = {
            "end_date": end_date.strftime("%Y-%m-%d"),
            "type": sub_type,
            "activated_date": datetime.now().strftime("%Y-%m-%d"),
            "days": days
        }
        
        self._save_json(SUBSCRIPTIONS_FILE, self.subscriptions)
        logger.info(f"✅ تم تفعيل اشتراك {sub_type} لمدة {days} أيام للمستخدم: {user_id}")
        
        return end_date
    
    def remove_subscription(self, user_id: str) -> Dict:
        """إلغاء اشتراك مستخدم"""
        user_id = str(user_id)
        removed = False
        message = ""
        
        if user_id in self.subscriptions:
            del self.subscriptions[user_id]
            self._save_json(SUBSCRIPTIONS_FILE, self.subscriptions)
            removed = True
            message += "✅ **تم إلغاء الاشتراك المدفوع**\n"
        
        if user_id in self.trials:
            del self.trials[user_id]
            self._save_json(TRIALS_FILE, self.trials)
            removed = True
            message += "✅ **تم إلغاء التجربة المجانية**\n"
        
        if removed:
            message += f"\n👤 **المستخدم:** `{user_id}`\n📅 **التاريخ:** {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            return {"success": True, "message": message}
        
        return {"success": False, "message": "⚠️ **المستخدم ليس لديه اشتراك نشط**"}
    
    def generate_activation_code(self, days: int, sub_type: str, admin_id: int) -> str:
        """إنشاء كود تفعيل"""
        code = secrets.token_hex(4).upper()
        
        self.activation_codes[code] = {
            "days": days,
            "type": sub_type,
            "used": False,
            "created_by": admin_id,
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self._save_json(ACTIVATION_CODES_FILE, self.activation_codes)
        logger.info(f"✅ تم إنشاء كود تفعيل: {code} لمدة {days} أيام")
        
        return code
    
    def use_activation_code(self, code: str, user_id: str) -> Dict:
        """استخدام كود التفعيل"""
        code = code.upper()
        
        if code in self.activation_codes and not self.activation_codes[code]["used"]:
            # تحديث الكود كمستخدم
            self.activation_codes[code]["used"] = True
            self.activation_codes[code]["used_by"] = user_id
            self.activation_codes[code]["used_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_json(ACTIVATION_CODES_FILE, self.activation_codes)
            
            # تفعيل الاشتراك
            days = self.activation_codes[code]["days"]
            sub_type = self.activation_codes[code]["type"]
            end_date = self.activate_subscription(user_id, days, sub_type)
            
            logger.info(f"✅ تم استخدام كود تفعيل {code} بواسطة المستخدم: {user_id}")
            
            return {
                "success": True, 
                "days": days, 
                "type": sub_type, 
                "end_date": end_date
            }
        
        return {"success": False, "message": "كود غير صالح أو مستخدم مسبقاً"}
    
    def update_user_installation(self, user_id: str, session_id: int):
        """تحديث قائمة تثبيتات المستخدم"""
        user_id = str(user_id)
        
        if user_id not in self.user_installations:
            self.user_installations[user_id] = []
        
        if session_id not in self.user_installations[user_id]:
            self.user_installations[user_id].append(session_id)
            self._save_json(USER_INSTALLATIONS_FILE, self.user_installations)
            logger.info(f"✅ تم تحديث تثبيتات المستخدم {user_id}")
    
    def check_installation_limit(self, user_id: str) -> Dict:
        """التحقق من عدد التثبيتات المسموح بها"""
        user_id = str(user_id)
        
        sub_status = self.check_subscription(user_id)
        
        if not sub_status["active"]:
            return {"allowed": False, "reason": "ليس لديك اشتراك نشط"}
        
        if sub_status["type"] == "trial":
            if user_id in self.user_installations and len(self.user_installations[user_id]) >= 1:
                return {"allowed": False, "reason": "التجريبية تسمح بتثبيت واحد فقط"}
        
        return {"allowed": True, "reason": "مسموح بالتثبيت"}
    
    def get_all_subscriptions(self) -> Dict:
        """الحصول على جميع الاشتراكات"""
        return {
            "paid": self.subscriptions,
            "trials": self.trials,
            "total_users": len(set(list(self.subscriptions.keys()) + list(self.trials.keys()))),
            "total_paid": len(self.subscriptions),
            "total_trials": len(self.trials)
        }
    
    def get_user_installations(self, user_id: str) -> List[int]:
        """الحصول على تثبيتات المستخدم"""
        user_id = str(user_id)
        return self.user_installations.get(user_id, [])