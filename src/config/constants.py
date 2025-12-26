"""
الثوابت المستخدمة في التطبيق
"""

# أنواع الاشتراكات
SUBSCRIPTION_TYPES = {
    "trial": "تجريبي",
    "weekly": "أسبوعي",
    "monthly": "شهري",
    "yearly": "سنوي",
    "lifetime": "مدى الحياة"
}

# فترات الاشتراك بالأيام
SUBSCRIPTION_PERIODS = {
    "trial": 3,
    "weekly": 7,
    "monthly": 30,
    "yearly": 365,
    "lifetime": 3650  # 10 سنوات
}

# أسعار الاشتراكات (بالدولار)
SUBSCRIPTION_PRICES = {
    "weekly": 5,
    "monthly": 15,
    "yearly": 50,
    "lifetime": 200
}

# أوامر التجميع التلقائي
COLLECTION_BOTS = [
    "@DamKombot",
    "@VCBots",
    "@TGBot_CH",
    "@NintendoSwitchRobot",
    "@SpamBot"
]

# فلاتر الصور المتاحة
IMAGE_FILTERS = [
    'Scream', 'Submarine', 'Cheetah', 'Sadness', 'Graffiti', 'Landscape',
    'Polygons', 'Illusion', 'Flames', 'Mola', 'Tattoo', 'Mushroom', 'Nebula',
    'Daisies', 'Fur', 'Space', 'Brains', 'Acid', 'Night', 'Quirky', 'Waves',
    'Coldrain', 'Sparks', 'Splash', 'Floating', 'Frost', 'Berry', 'Leather',
    'Frida', 'Grey', 'Nouveau', 'Ceremony', 'Psychedelic', 'Blueswirls',
    'Creepy', 'Gauguin', 'Redblush', 'Crayon', 'Escher', 'Fantasy',
    'Reptile', 'Pen', 'Homer', 'Tiedye', 'Monster', 'Starry2',
    'Paper Folding', 'Scribble', 'Wallpaper', 'sketch4', 'Tuscany',
    'Barcelona', 'Beauty', 'Rembrandt', 'Delaunay', 'Geometric', 'Metallic',
    'Garden', 'Connections', 'Edtaonisl', 'Vangogh', 'Picasso', 'Swirls',
    'Shattered', 'Candy', 'Futuristic', 'Yarn', 'Coffee', 'Rave', 'Lily',
    'Devilish', 'Smoke', 'Composition', 'Dark', 'Fairy', 'Watercolor',
    'Mosaic2', 'Abstract', 'Blood', 'Brave', 'Jungle', 'Matrix', 'Dreaming',
    'Mosaic', 'Flow', 'Reds', 'Flowers', 'Oldrug', 'Chalkboard', 'Storytime',
    'Watercolor2', 'Kandinsky', 'Adventure', 'Pasley', 'Sketch2', 'Sketch3'
]

# ترجمة الفلاتر إلى العربية
FILTERS_ARABIC = {
    'Scream': 'صرخة', 'Submarine': 'غواصة', 'Cheetah': 'فهد',
    'Sadness': 'حزن', 'Graffiti': 'جرافيتي', 'Landscape': 'منظر طبيعي',
    'Polygons': 'أشكال هندسية', 'Illusion': 'وهم بصري', 'Flames': 'لهب',
    'Mola': 'مولا', 'Tattoo': 'وشم', 'Mushroom': 'فطر',
    'Nebula': 'سديم', 'Daisies': 'أقحوان', 'Fur': 'فرو',
    'Space': 'فضاء', 'Brains': 'أدمغة', 'Acid': 'حمض',
    'Night': 'ليل', 'Quirky': 'غريب', 'Waves': 'أمواج',
    'Coldrain': 'مطر بارد', 'Sparks': 'شرر', 'Splash': 'رشاش ماء',
    'Floating': 'طافي', 'Frost': 'صقيع', 'Berry': 'توت',
    'Leather': 'جلد', 'Frida': 'فريدا', 'Grey': 'رمادي',
    'Nouveau': 'جديد', 'Ceremony': 'احتفال', 'Psychedelic': 'نفسي',
    'Blueswirls': 'دوامات زرقاء', 'Creepy': 'مخيف', 'Gauguin': 'غوغان',
    'Redblush': 'احمرار أحمر', 'Crayon': 'قلم تلوين', 'Escher': 'إيشر',
    'Fantasy': 'خيال', 'Reptile': 'زواحف', 'Pen': 'قلم',
    'Homer': 'هومر', 'Tiedye': 'صباغة معقودة', 'Monster': 'وحش',
    'Starry2': 'مليء بالنجوم 2', 'Paper Folding': 'طي الورق', 'Scribble': 'خربشة',
    'Wallpaper': 'ورق جدران', 'sketch4': 'رسم تخطيطي 4', 'Tuscany': 'توسكانا',
    'Barcelona': 'برشلونة', 'Beauty': 'جمال', 'Rembrandt': 'رامبرانت',
    'Delaunay': 'ديلوناي', 'Geometric': 'هندسي', 'Metallic': 'معدني',
    'Garden': 'حديقة', 'Connections': 'روابط', 'Edtaonisl': 'إدتاونيسل',
    'Vangogh': 'فان جوخ', 'Picasso': 'بيكاسو', 'Swirls': 'دوامات',
    'Shattered': 'محطم', 'Candy': 'حلوى', 'Futuristic': 'مستقبلي',
    'Yarn': 'غزل', 'Coffee': 'قهوة', 'Rave': 'حفلة صاخبة',
    'Lily': 'زنبق', 'Devilish': 'شيطاني', 'Smoke': 'دخان',
    'Composition': 'تكوين', 'Dark': 'ظلام', 'Fairy': 'جنية',
    'Watercolor': 'ألوان مائية', 'Mosaic2': 'فسيفساء 2', 'Abstract': 'تجريدي',
    'Blood': 'دم', 'Brave': 'شجاع', 'Jungle': 'غابة',
    'Matrix': 'مصفوفة', 'Dreaming': 'حلم', 'Mosaic': 'فسيفساء',
    'Flow': 'تدفق', 'Reds': 'أحمر', 'Flowers': 'زهور',
    'Oldrug': 'سجادة قديمة', 'Chalkboard': 'سبورة طباشير', 'Storytime': 'وقت القصة',
    'Watercolor2': 'ألوان مائية 2', 'Kandinsky': 'كاندينسكي', 'Adventure': 'مغامرة',
    'Pasley': 'بيزلي', 'Sketch2': 'رسم تخطيطي 2', 'Sketch3': 'رسم تخطيطي 3'
}

# إيموجيات المستويات
TIER_BADGES = {
    "bronze": "🥉",
    "silver": "🥈", 
    "gold": "🥇",
    "platinum": "💎"
}

# رسائل النظام
SYSTEM_MESSAGES = {
    "welcome": "👋 أهلاً بك في سورس كومن الذكي!",
    "subscription_expired": "⚠️ اشتراكك منتهي، يرجى التجديد",
    "admin_required": "⛔️ هذا الأمر مخصص للإدارة فقط",
    "permission_denied": "⛔️ ليس لديك صلاحية لهذا الأمر",
    "success": "✅ تمت العملية بنجاح",
    "error": "❌ حدث خطأ ما",
    "processing": "🔄 جاري المعالجة...",
    "not_found": "🔍 لم يتم العثور",
    "invalid_input": "⚠️ مدخل غير صالح"
}