from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import pytz
from .config import config
from .database import db
from .economic_calendar import calendar
from .content_generator import generator

class BotScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)
        self.timezone = pytz.timezone(config.TIMEZONE)

    def start(self):
        """بدء الجدولة"""
        # جدولة المنشورات التعليمية
        for time_str in config.EDUCATION_POST_TIMES:
            try:
                hour, minute = map(int, time_str.strip().split(":"))
                self.scheduler.add_job(
                    self.post_education,
                    CronTrigger(hour=hour, minute=minute, timezone=self.timezone),
                    id=f"education_{hour}_{minute}",
                    replace_existing=True
                )
                print(f"✅ جدولة تعليم: {hour:02d}:{minute:02d}")
            except Exception as e:
                print(f"❌ خطأ جدولة تعليم {time_str}: {e}")

        # جدولة ملخص الأخبار
        for time_str in config.NEWS_POST_TIMES:
            try:
                hour, minute = map(int, time_str.strip().split(":"))
                self.scheduler.add_job(
                    self.post_news_summary,
                    CronTrigger(hour=hour, minute=minute, timezone=self.timezone),
                    id=f"news_{hour}_{minute}",
                    replace_existing=True
                )
                print(f"✅ جدولة أخبار: {hour:02d}:{minute:02d}")
            except Exception as e:
                print(f"❌ خطأ جدولة أخبار {time_str}: {e}")

        # فحص التقويم الاقتصادي كل ساعة
        self.scheduler.add_job(
            self.check_important_news,
            IntervalTrigger(minutes=config.ECONOMIC_CALENDAR_CHECK_INTERVAL, timezone=self.timezone),
            id="calendar_check",
            replace_existing=True
        )

        # منشور تحفيزي يومي 21:00
        self.scheduler.add_job(
            self.post_motivational,
            CronTrigger(hour=21, minute=0, timezone=self.timezone),
            id="motivational",
            replace_existing=True
        )

        # افتتاح السوق 07:00
        self.scheduler.add_job(
            self.post_market_open,
            CronTrigger(hour=7, minute=0, timezone=self.timezone),
            id="market_open",
            replace_existing=True
        )

        self.scheduler.start()
        print("🚀 بدأ المجدول بنجاح!")

    def stop(self):
        self.scheduler.shutdown()

    async def post_education(self):
        """نشر منشور تعليمي"""
        if not config.ENABLE_EDUCATION or not config.CHANNEL_ID:
            return
        
        try:
            progress = db.get_education_progress()
            day = progress['day']
            
            content = generator.generate_education_post(day)
            
            await self.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=content,
                parse_mode='Markdown'
            )
            
            db.mark_education_posted(f"edu_{day}_{datetime.now().date()}")
            db.next_education_day()
            
            print(f"✅ تم نشر درس اليوم {day}")
            
            # إشعار للمشرفين
            if config.ADMIN_IDS:
                for admin_id in config.ADMIN_IDS[:1]:  # أول أدمن فقط
                    try:
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=f"✅ تم نشر درس اليوم {day} تلقائياً للقناة"
                        )
                    except:
                        pass
                        
        except Exception as e:
            print(f"❌ خطأ نشر تعليمي: {e}")

    async def post_news_summary(self):
        """نشر ملخص الأخبار"""
        if not config.ENABLE_ECONOMIC_NEWS or not config.CHANNEL_ID:
            return
        
        try:
            events = calendar.get_today_high_impact_events()
            content = generator.generate_daily_news_summary(events)
            
            await self.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=content,
                parse_mode='Markdown'
            )
            
            db.set_last_news_post()
            print(f"✅ تم نشر ملخص الأخبار - {len(events)} حدث")
            
        except Exception as e:
            print(f"❌ خطأ نشر أخبار: {e}")

    async def check_important_news(self):
        """فحص الأخبار المهمة القادمة وتنبيه"""
        if not config.ENABLE_ECONOMIC_NEWS:
            return
        
        try:
            events = calendar.get_today_high_impact_events()
            now = datetime.now(self.timezone)
            
            # البحث عن أخبار خلال الساعة القادمة
            urgent_events = []
            for event in events:
                try:
                    # محاولة تحليل الوقت
                    time_str = event.get('time', '')
                    if ':' in time_str:
                        hour, minute = map(int, time_str.split(':')[:2])
                        event_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        diff = (event_time - now).total_seconds() / 60
                        
                        # إذا الخبر خلال 60 دقيقة القادمة
                        if 0 <= diff <= 65:
                            urgent_events.append(event)
                except:
                    continue
            
            # إرسال تنبيه عاجل للأخبار القريبة
            if urgent_events and config.CHANNEL_ID:
                for event in urgent_events:
                    event_id = f"urgent_{event.get('id')}_{now.date()}"
                    if not db.is_news_posted(event_id):
                        alert = f"""
🚨 **تنبيه عاجل - خبر بعد قليل!**

{calendar.format_event_for_telegram(event, with_analysis=True)}

⏰ متبقي أقل من ساعة!

#تنبيه_عاجل
"""
                        try:
                            await self.bot.send_message(
                                chat_id=config.CHANNEL_ID,
                                text=alert,
                                parse_mode='Markdown'
                            )
                            db.mark_news_posted(event_id)
                            print(f"🚨 تنبيه عاجل: {event.get('title')}")
                        except Exception as e:
                            print(f"خطأ تنبيه: {e}")
            
            db.set_last_calendar_check()
            
        except Exception as e:
            print(f"❌ خطأ فحص التقويم: {e}")

    async def post_motivational(self):
        """منشور تحفيزي مسائي"""
        if not config.CHANNEL_ID:
            return
        try:
            # مرة كل 3 أيام فقط لتجنب الإزعاج
            import random
            if random.random() < 0.33:
                content = generator.generate_motivational_post()
                await self.bot.send_message(
                    chat_id=config.CHANNEL_ID,
                    text=content,
                    parse_mode='Markdown'
                )
                print("✅ منشور تحفيزي")
        except Exception as e:
            print(f"خطأ تحفيزي: {e}")

    async def post_market_open(self):
        """منشور افتتاح السوق"""
        if not config.CHANNEL_ID:
            return
        try:
            content = generator.generate_market_open_post()
            await self.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=content,
                parse_mode='Markdown'
            )
            print("✅ منشور افتتاح السوق")
        except Exception as e:
            print(f"خطأ افتتاح: {e}")
