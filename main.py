#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت قناة التداول الذكي - صانع محتوى متكامل
Trading Channel AI Content Maker Bot

المميزات:
- منشورات تعليمية يومية بمنهج 30 يوم
- أخبار اقتصادية وتقويم اقتصادي تلقائي
- ذكاء اصطناعي لتحسين المحتوى
- جدولة تلقائية ونشر للقناة
"""

import asyncio
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from bot.config import config
from bot.handlers import (
    start_command, help_command, education_command, lesson_command,
    news_command, calendar_command, status_command, motivational_command,
    market_command, post_education_command, post_news_command,
    post_daily_summary_command, next_day_command, set_day_command,
    reset_command, curriculum_command, button_callback
)
from bot.scheduler import BotScheduler

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تقليل ضوضاء السجلات
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

async def main():
    """الدالة الرئيسية"""
    print("""
╔════════════════════════════════════════╗
║   🤖 بوت قناة التداول الذكي            ║
║   Trading Channel AI Bot               ║
║                                        ║
║   📚 تعليم + 📰 أخبار + 🤖 ذكاء اصطناعي  ║
╚════════════════════════════════════════╝
    """)
    
    # التحقق من الإعدادات
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ خطأ في الإعدادات: {e}")
        print("📝 تأكد من ملف .env و BOT_TOKEN")
        return

    print(f"✅ التوكن: {config.BOT_TOKEN[:10]}...")
    print(f"✅ القناة: {config.CHANNEL_ID}")
    print(f"✅ المنطقة الزمنية: {config.TIMEZONE}")
    print(f"✅ الذكاء الاصطناعي: {'مفعل' if config.OPENAI_API_KEY else 'معطل - سيستخدم القوالب'}")

    # إنشاء التطبيق
    application = Application.builder().token(config.BOT_TOKEN).build()

    # إضافة المعالجات - أوامر عامة
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("education", education_command))
    application.add_handler(CommandHandler("lesson", lesson_command))
    application.add_handler(CommandHandler("news", news_command))
    application.add_handler(CommandHandler("calendar", calendar_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("motivational", motivational_command))
    application.add_handler(CommandHandler("market", market_command))
    application.add_handler(CommandHandler("curriculum", curriculum_command))
    application.add_handler(CommandHandler("taqweem", calendar_command))
    application.add_handler(CommandHandler("ta3leem", education_command))

    # أوامر المشرفين
    application.add_handler(CommandHandler("post_education", post_education_command))
    application.add_handler(CommandHandler("post_news", post_news_command))
    application.add_handler(CommandHandler("post_daily_summary", post_daily_summary_command))
    application.add_handler(CommandHandler("next_day", next_day_command))
    application.add_handler(CommandHandler("set_day", set_day_command))
    application.add_handler(CommandHandler("reset", reset_command))

    # معالج الأزرار
    application.add_handler(CallbackQueryHandler(button_callback))

    # بدء المجدول
    scheduler = BotScheduler(application.bot)
    
    # بدء البوت
    await application.initialize()
    await application.start()
    
    scheduler.start()
    
    print("\n🚀 البوت يعمل الآن...")
    print("📱 اذهب لتليجرام واكتب /start")
    print("⏹️ للإيقاف اضغط Ctrl+C\n")
    
    # تشغيل البوت
    await application.updater.start_polling()

    try:
        # إبقاء البوت يعمل
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ إيقاف البوت...")
    finally:
        scheduler.stop()
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        print("✅ تم الإيقاف بنجاح")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 تم الإيقاف")
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
