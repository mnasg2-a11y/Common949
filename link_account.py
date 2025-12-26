# link_account.py - لربط حسابك الشخصي
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

async def link_my_account():
    """ربط حسابك الشخصي بالسورس"""
    print("📱 جاري ربط حسابك الشخصي...")
    
    # 1. أدخل API الخاص بك (نفس api_id و api_hash)
    api_id = int(input("• أدخل API ID: "))
    api_hash = input("• أدخل API HASH: ")
    
    # 2. إنشاء العميل
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.connect()
    
    # 3. إرسال طلب تسجيل الدخول
    phone = input("• أدخل رقم هاتفك (مع +): ")
    
    # إرسال الكود
    sent = await client.send_code_request(phone)
    print(f"✅ تم إرسال الكود إلى {phone}")
    
    # 4. أدخل الكود
    code = input("• أدخل الكود الذي وصلك: ").strip()
    
    try:
        # تسجيل الدخول
        await client.sign_in(phone, code, phone_code_hash=sent.phone_code_hash)
        print("✅ تم تسجيل الدخول بنجاح!")
    except Exception as e:
        print(f"❌ خطأ: {e}")
        
        # إذا كان فيه كلمة سر (2FA)
        if "password" in str(e):
            password = input("• أدخل كلمة السر (2FA): ")
            await client.sign_in(password=password)
            print("✅ تم تسجيل الدخول بكلمة السر!")
    
    # 5. حفظ الجلسة
    session_string = client.session.save()
    
    with open('my_account.session', 'w', encoding='utf-8') as f:
        f.write(session_string)
    
    print(f"✅ تم حفظ الجلسة في: my_account.session")
    
    # 6. معلومات الحساب
    me = await client.get_me()
    print(f"\n🎉 تم ربط الحساب:")
    print(f"👤 الاسم: {me.first_name}")
    print(f"🆔 الآيدي: {me.id}")
    print(f"📞 الرقم: {phone}")
    
    await client.disconnect()

# التشغيل
asyncio.run(link_my_account())
