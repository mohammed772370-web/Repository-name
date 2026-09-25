#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نشر مباشر للقناة - يستخدم في GitHub Actions
يقرأ التوكن من متغيرات البيئة وينشر
"""

import os
import sys
import requests
from datetime import datetime

# إضافة مسار البوت
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from bot.education_plan import get_education_lesson, get_phase_info
    from bot.economic_calendar import calendar
    from bot.content_generator import generator
    from bot.database import db
    BOT_AVAILABLE = True
except Exception as e:
    print(f"⚠️ لا يمكن استيراد مكونات البوت: {e}")
    BOT_AVAILABLE = False

def send_message(bot_token, channel_id, text):
    """إرسال رسالة للقناة"""
    if not bot_token or not channel_id:
        print("❌ التوكن أو معرف القناة مفقود")
        return False
    
    # تنظيف التوكن من المسافات
    bot_token = bot_token.strip()
    channel_id = channel_id.strip()
    
    # التحقق من شكل التوكن
    if ":" not in bot_token:
        print(f"❌ شكل التوكن غير صحيح، يجب أن يحتوي على : - التوكن: {bot_token[:10]}...")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": channel_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        print(f"📤 إرسال إلى {channel_id}...")
        response = requests.post(url, json=payload, timeout=15)
        result = response.json()
        
        print(f"📡 رد تليجرام: {result}")
        
        if result.get("ok"):
            print(f"✅ تم النشر بنجاح في {channel_id}")
            return True
        else:
            error = result.get("description", "خطأ غير معروف")
            print(f"❌ فشل النشر: {error}")
            print(f"كود الخطأ: {result.get('error_code')}")
            
            # تشخيص الأخطاء الشائعة
            if "chat not found" in error.lower():
                print("💡 السبب: معرف القناة غير صحيح أو البوت ليس مشرف في القناة")
                print(f"   تأكد أن البوت مشرف في {channel_id}")
            elif "unauthorized" in error.lower() or "invalid token" in error.lower():
                print("💡 السبب: التوكن غير صحيح أو منتهي")
                print("   اذهب لـ @BotFather واعمل /mybots وانسخ التوكن الجديد")
            elif "not enough rights" in error.lower():
                print("💡 السبب: البوت ليس لديه صلاحية النشر")
                print("   اجعل البوت مشرف مع صلاحية نشر الرسائل")
            
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False

def publish_education(day=None):
    """نشر درس تعليمي"""
    if not BOT_AVAILABLE:
        print("❌ مكونات البوت غير متوفرة")
        return False
    
    try:
        if day is None:
            progress = db.get_education_progress()
            day = progress['day']
        
        print(f"📚 نشر درس اليوم {day}")
        content = generator.generate_education_post(day)
        
        bot_token = os.getenv("BOT_TOKEN", "").strip()
        channel_id = os.getenv("CHANNEL_ID", "@Trading_TOB").strip()
        
        success = send_message(bot_token, channel_id, content)
        
        if success:
            try:
                db.mark_education_posted(f"edu_{day}_{datetime.now().date()}")
                db.next_education_day()
                print(f"✅ تم تحديث التقدم لليوم التالي")
            except Exception as e:
                print(f"⚠️ لم يتم تحديث التقدم: {e}")
        
        return success
    except Exception as e:
        print(f"❌ خطأ في نشر التعليم: {e}")
        import traceback
        traceback.print_exc()
        return False

def publish_news():
    """نشر أخبار اليوم"""
    if not BOT_AVAILABLE:
        print("❌ مكونات البوت غير متوفرة")
        return False
    
    try:
        print(f"📰 نشر أخبار اليوم")
        events = calendar.get_today_high_impact_events()
        content = generator.generate_daily_news_summary(events)
        
        bot_token = os.getenv("BOT_TOKEN", "").strip()
        channel_id = os.getenv("CHANNEL_ID", "@Trading_TOB").strip()
        
        return send_message(bot_token, channel_id, content)
    except Exception as e:
        print(f"❌ خطأ في نشر الأخبار: {e}")
        import traceback
        traceback.print_exc()
        return False

def publish_motivational():
    """نشر منشور تحفيزي"""
    if not BOT_AVAILABLE:
        print("❌ مكونات البوت غير متوفرة")
        return False
    
    try:
        content = generator.generate_motivational_post()
        bot_token = os.getenv("BOT_TOKEN", "").strip()
        channel_id = os.getenv("CHANNEL_ID", "@Trading_TOB").strip()
        return send_message(bot_token, channel_id, content)
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def test_token():
    """اختبار التوكن فقط"""
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    channel_id = os.getenv("CHANNEL_ID", "@Trading_TOB").strip()
    
    print(f"🔍 اختبار التوكن...")
    print(f"التوكن: {bot_token[:15]}...{bot_token[-5:] if len(bot_token)>10 else ''}")
    print(f"القناة: {channel_id}")
    
    if not bot_token:
        print("❌ BOT_TOKEN غير موجود في متغيرات البيئة")
        return False
    
    if ":" not in bot_token:
        print("❌ شكل التوكن غير صحيح")
        print("💡 التوكن يجب أن يكون مثل: 1234567890:AAHdqTcv...")
        print("💡 انسخه من @BotFather -> /mybots -> اختر بوتك -> API Token")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        print(f"📡 فحص التوكن...")
        response = requests.get(url, timeout=10)
        result = response.json()
        
        print(f"📡 الرد: {result}")
        
        if result.get("ok"):
            bot = result.get("result", {})
            print(f"✅ التوكن صحيح!")
            print(f"🤖 البوت: @{bot.get('username')} - {bot.get('first_name')}")
            return True
        else:
            print(f"❌ التوكن غير صحيح: {result.get('description')}")
            print(f"💡 اذهب لـ @BotFather وانسخ التوكن الجديد")
            return False
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="نشر لقناة التداول")
    parser.add_argument("type", choices=["education", "news", "motivational", "test", "market"], help="نوع النشر")
    parser.add_argument("--day", type=int, help="رقم اليوم للتعليم")
    
    args = parser.parse_args()
    
    print(f"🚀 نشر {args.type} لقناة {os.getenv('CHANNEL_ID', '@Trading_TOB')}")
    print(f"⏰ الوقت: {datetime.now()}")
    
    if args.type == "education":
        success = publish_education(args.day)
    elif args.type == "news":
        success = publish_news()
    elif args.type == "motivational":
        success = publish_motivational()
    elif args.type == "test":
        success = test_token()
    elif args.type == "market":
        if BOT_AVAILABLE:
            content = generator.generate_market_open_post()
            bot_token = os.getenv("BOT_TOKEN", "").strip()
            channel_id = os.getenv("CHANNEL_ID", "@Trading_TOB").strip()
            success = send_message(bot_token, channel_id, content)
        else:
            success = False
    
    sys.exit(0 if success else 1)
