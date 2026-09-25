#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعداد البوت التفاعلي - للمبتدئين
شغل هذا الملف وسيطلب منك المعلومات خطوة بخطوة
"""

import os
import re

def print_header():
    print("""
╔════════════════════════════════════════════════╗
║  🤖 إعداد بوت قناة التداول - خطوة بخطوة      ║
║  لا تحتاج خبرة، فقط اتبع التعليمات           ║
╚════════════════════════════════════════════════╝
    """)

def ask_token():
    print("\n" + "="*50)
    print("الخطوة 1: توكن البوت")
    print("="*50)
    print("التوكن هو رمز طويل مثل:")
    print("1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw")
    print("\nأخذته من @BotFather صح؟")
    
    while True:
        token = input("\n👉 الصق توكن البوت هنا: ").strip()
        if not token:
            print("❌ التوكن فارغ!")
            continue
        if ":" not in token or len(token) < 20:
            print("❌ هذا لا يبدو توكن صحيح، يجب أن يحتوي على : ويكون طويل")
            continue
        print(f"✅ تمام، التوكن: {token[:10]}...{token[-5:]}")
        return token

def ask_channel():
    print("\n" + "="*50)
    print("الخطوة 2: معرف القناة")
    print("="*50)
    print("إذا قناتك عامة: اكتب @اسم_القناة")
    print("مثال: @TradingYemen أو @GoldSignals")
    print("")
    print("إذا قناتك خاصة: اكتب الايدي الرقمي")
    print("مثال: -1001234567890")
    print("")
    print("💡 كيف تجيب معرف القناة؟")
    print("  - لو عامة: انسخ رابط القناة، الجزء بعد t.me/ هو المعرف")
    print("  - لو خاصة: ارسل أي رسالة من القناة لبوت @userinfobot وسيعطيك الايدي")
    
    while True:
        channel = input("\n👉 اكتب معرف قناتك: ").strip()
        if not channel:
            print("❌ فارغ!")
            continue
        # إضافة @ إذا لم يوجد وكان ليس رقم
        if not channel.startswith("@") and not channel.startswith("-100"):
            if channel.replace("_","").replace("0","").replace("1","").isalnum() or "_" in channel:
                # يبدو يوزر بدون @
                channel = "@" + channel
                print(f"تمت إضافة @ تلقائياً: {channel}")
        
        print(f"✅ القناة: {channel}")
        return channel

def ask_admin():
    print("\n" + "="*50)
    print("الخطوة 3: ايدي حسابك (اختياري لكن مهم)")
    print("="*50)
    print("هذا حتى تصبح أنت المشرف وتقدر تنشر يدوياً")
    print("كيف تجيبه؟")
    print("1. ابحث في تليجرام عن @userinfobot")
    print("2. أرسل له أي رسالة")
    print("3. سيرد عليك برقم مثل 123456789 هذا هو ايديك")
    
    admin = input("\n👉 اكتب ايديك (أو اضغط Enter للتخطي): ").strip()
    if admin and admin.isdigit():
        print(f"✅ ايديك: {admin}")
        return admin
    else:
        print("⏭️ تم التخطي، سيتمكن الجميع من استخدام أوامر المشرف مؤقتاً")
        return ""

def ask_ai():
    print("\n" + "="*50)
    print("الخطوة 4: الذكاء الاصطناعي (اختياري)")
    print("="*50)
    print("البوت يعمل بدون ذكاء اصطناعي بقوالب احترافية!")
    print("لكن مع الذكاء الاصطناعي يصبح أذكى وأجمل")
    print("")
    print("هل عندك مفتاح Groq المجاني أو OpenAI؟")
    print("لو ما عندك، اضغط Enter وسيعمل بدون AI")
    print("لو عندك، الصقه هنا")
    print("")
    print("💡 للحصول على مفتاح مجاني سريع:")
    print("اذهب لـ https://console.groq.com واعمل حساب مجاني")
    
    ai_key = input("\n👉 مفتاح AI (أو Enter للتخطي): ").strip()
    if ai_key:
        print(f"✅ تم حفظ مفتاح AI")
        return ai_key
    else:
        print("⏭️ سيعمل بالقوالب الاحترافية")
        return ""

def create_env(token, channel, admin, ai_key):
    content = f"""# تم إنشاؤه تلقائياً بواسطة إعداد_البوت.py
BOT_TOKEN={token}
CHANNEL_ID={channel}
ADMIN_IDS={admin}

# الذكاء الاصطناعي
OPENAI_API_KEY={ai_key}
OPENAI_MODEL=llama-3.1-8b-instant
OPENAI_BASE_URL=https://api.groq.com/openai/v1

# الإعدادات
TIMEZONE=Asia/Riyadh
EDUCATION_POST_TIMES=10:00,18:00
NEWS_POST_TIMES=08:00,14:00,20:00
ECONOMIC_CALENDAR_CHECK_INTERVAL=60

LANGUAGE=ar
ENABLE_AI_GENERATION=True
ENABLE_ECONOMIC_NEWS=True
ENABLE_EDUCATION=True
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("\n" + "="*50)
    print("✅ تم إنشاء ملف .env بنجاح!")
    print("="*50)
    print(f"📁 الملف موجود في: {os.path.abspath('.env')}")

def test_setup():
    print("\n" + "="*50)
    print("🧪 اختبار الإعدادات")
    print("="*50)
    try:
        from bot.config import Config
        print(f"✅ التوكن: {Config.BOT_TOKEN[:15]}...")
        print(f"✅ القناة: {Config.CHANNEL_ID}")
        print(f"✅ المنطقة الزمنية: {Config.TIMEZONE}")
        if Config.OPENAI_API_KEY:
            print(f"✅ AI: مفعل")
        else:
            print(f"✅ AI: سيعمل بالقوالب (بدون AI)")
        return True
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def main():
    print_header()
    
    print("\n👋 أهلاً! سأساعدك في إعداد البوت خطوة بخطوة")
    print("إذا عندك التوكن والقناة جاهزين، الموضوع يأخذ دقيقتين فقط")
    
    input("\nاضغط Enter للبدء...")
    
    token = ask_token()
    channel = ask_channel()
    admin = ask_admin()
    ai_key = ask_ai()
    
    create_env(token, channel, admin, ai_key)
    
    if test_setup():
        print("\n" + "="*50)
        print("🎉 مبروك! الإعداد اكتمل")
        print("="*50)
        print("\nالآن لتشغيل البوت:")
        print("1. شغل: python main.py")
        print("2. اذهب لتليجرام واكتب /start للبوت")
        print("3. جرب /education و /news")
        print("4. للنشر للقناة: /post_education")
        print("\n💡 البوت سينشر تلقائياً كل يوم حسب الجدولة")
        print("\n⚠️ مهم: لا تغلق نافذة الأوامر، البوت يجب أن يبقى يعمل")
        print("لتشغيل 24 ساعة، سأعطيك طريقة بعد قليل")
    else:
        print("\n❌ هناك مشكلة في الإعداد، تأكد من التوكن")
    
    print("\n" + "="*50)
    print("هل تريد تشغيل البوت الآن؟")
    choice = input("اكتب y للتشغيل أو n للخروج: ").strip().lower()
    if choice == 'y':
        print("\n🚀 تشغيل البوت...")
        os.system("python main.py")

if __name__ == "__main__":
    main()
