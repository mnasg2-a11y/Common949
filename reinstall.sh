#!/bin/bash
echo "🔄 إعادة تثبيت سورس كومن..."

# 1. أوقف السورس
echo "⏹️ جاري إيقاف السورس..."
pkill -f python3 2>/dev/null
pkill -f python 2>/dev/null
pkill -f common 2>/dev/null
pkill -f bot 2>/dev/null
sleep 2

# 2. احفظ بياناتك المهمة (إذا عندك)
echo "💾 جاري نسخ البيانات احتياطياً..."
mkdir -p ~/backup_common
cp -r ~/Common*/data ~/backup_common/ 2>/dev/null
cp ~/Common*/*.session ~/backup_common/ 2>/dev/null
cp ~/Common*/*.json ~/backup_common/ 2>/dev/null

# 3. احذف القديم
echo "🗑️ جاري حذف السورس القديم..."
rm -rf ~/Common*
rm -rf ~/common*
rm -rf ~/Comman*
rm -rf ~/bot*

# 4. نزل الجديد
echo "⬇️ جاري تنزيل السورس الجديد..."
git clone https://github.com/mnasg2-a11y/Common949.git
cd Common949

# 5. ثبت المكاتب
echo "📦 جاري تثبيت المكتبات..."
pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt

# 6. استرجع البيانات (إذا تريد)
echo "📂 جاري استعادة البيانات..."
cp -r ~/backup_common/data . 2>/dev/null
cp ~/backup_common/*.session . 2>/dev/null
cp ~/backup_common/*.json . 2>/dev/null

echo "✅ تمت إعادة التثبيت بنجاح!"
echo "🚀 ابدأ التشغيل: python3 run.py"
