"""
نماذج قاعدة البيانات
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class BaseModel:
    """النموذج الأساسي"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل النموذج إلى قاموس"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """إنشاء نموذج من قاموس"""
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance

@dataclass
class User(BaseModel):
    """نموذج المستخدم"""
    telegram_id: int = 0
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    subscription_status: str = "inactive"
    balance: float = 0.0
    total_earnings: float = 0.0
    referral_code: Optional[str] = None
    tier: str = "bronze"
    
    def get_full_name(self) -> str:
        """الحصول على الاسم الكامل"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else "مستخدم"
    
    def has_active_subscription(self) -> bool:
        """التحقق من وجود اشتراك نشط"""
        return self.subscription_status == "active"

@dataclass
class Subscription(BaseModel):
    """نموذج الاشتراك"""
    user_id: int = 0
    subscription_type: str = "trial"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "active"
    payment_amount: float = 0.0
    payment_method: Optional[str] = None
    
    def is_active(self) -> bool:
        """التحقق من نشاط الاشتراك"""
        if self.status != "active":
            return False
        
        if self.end_date and datetime.now() > self.end_date:
            return False
        
        return True
    
    def days_remaining(self) -> int:
        """عدد الأيام المتبقية"""
        if not self.end_date:
            return 0
        
        remaining = self.end_date - datetime.now()
        return max(0, remaining.days)

@dataclass
class Referral(BaseModel):
    """نموذج الإحالة"""
    referrer_id: int = 0
    referred_id: int = 0
    referral_code: str = ""
    status: str = "pending"
    commission_amount: float = 0.0
    
    def is_converted(self) -> bool:
        """التحقق من تحويل الإحالة"""
        return self.status == "converted"
    
    def get_commission(self) -> float:
        """الحصول على قيمة العمولة"""
        return self.commission_amount if self.is_converted() else 0.0

@dataclass
class Earning(BaseModel):
    """نموذج الأرباح"""
    user_id: int = 0
    amount: float = 0.0
    source: str = ""
    description: Optional[str] = None

@dataclass
class Session(BaseModel):
    """نموذج الجلسة"""
    user_id: int = 0
    session_string: str = ""
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    last_active: Optional[datetime] = None
    
    def is_active(self, timeout_minutes: int = 30) -> bool:
        """التحقق من نشاط الجلسة"""
        if not self.last_active:
            return False
        
        inactive_for = datetime.now() - self.last_active
        return inactive_for.total_seconds() < (timeout_minutes * 60)