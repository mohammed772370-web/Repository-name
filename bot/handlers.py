from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .config import config
from .database import db
from .education_plan import get_education_lesson, get_phase_info, EDUCATION_CURRICULUM
from .economic_calendar import calendar
from .content_generator import generator
from datetime import datetime

def is_admin(user_id: int) -> bool:
    if not config.ADMIN_IDS:
        return True  # إذا لم يحدد أدمن، الجميع أدمن في البداية
    return user_id in config.ADMIN_IDS

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome = f"""
👋 أهلاً {user.first_name}!

🤖 **بوت قناة التداول الذكي**

أنا بوت صانع محتوى متكامل لقناة التداول:

📚 **التعليم:**
• خطة 30 يوم للمبتدئين
• منشورين يومياً بمنهج متدرج
• يحافظ على الانتباه ويبني أساس قوي

📰 **الأخبار الاقتصادية:**
• تقويم اقتصادي يومي
• تنبيهات الأخبار عالية التأثير
• تحليل تأثير كل خبر على السوق

🎯 **الأوامر المتاحة:**
/education - نشر درس تعليمي الآن
/news - ملخص أخبار اليوم
/calendar - تقويم الأسبوع
/lesson [رقم] - درس محدد (1-30)
/status - إحصائيات البوت
/motivational - منشور تحفيزي
/market - حالة السوق
/help - المساعدة

🔧 **للمشرفين:**
/post_education - نشر تعليمي للقناة
/post_news - نشر أخبار للقناة
/next_day - الانتقال لليوم التالي
/reset - إعادة الخطة من البداية

━━━━━━━━━━━━━━━
💡 البوت يعمل تلقائياً حسب الجدولة في الإعدادات
"""
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 **دليل استخدام البوت**

**للمتابعين:**
• /start - البداية
• /education - درس اليوم
• /lesson 5 - درس رقم 5 مثلاً
• /news - أخبار اليوم
• /calendar - تقويم الأسبوع
• /status - إحصائيات

**للمشرفين:**
• /post_education - نشر درس للقناة الآن
• /post_news - نشر خبر للقناة
• /post_daily_summary - نشر ملخص يومي
• /next_day - اليوم التالي في الخطة
• /set_day 10 - الانتقال ليوم محدد
• /reset - إعادة من الصفر

**الإعداد التلقائي:**
البوت ينشر تلقائياً:
• 08:00 - ملخص التقويم الاقتصادي
• 10:00 - درس تعليمي صباحي
• 14:00 - تحديث أخبار
• 18:00 - درس تعليمي مسائي
• 20:00 - ملخص مسائي

⚙️ يمكن تغيير الأوقات من ملف .env

💬 للدعم: تواصل مع مشرف القناة
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def education_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض درس اليوم"""
    progress = db.get_education_progress()
    day = progress['day']
    lesson_content = generator.generate_education_post(day)
    
    keyboard = [
        [InlineKeyboardButton("📚 الدرس السابق", callback_data=f"lesson_{day-1}"),
         InlineKeyboardButton("📚 الدرس التالي", callback_data=f"lesson_{day+1}")],
        [InlineKeyboardButton("📅 خطة 30 يوم", callback_data="curriculum"),
         InlineKeyboardButton("📊 تقدمي", callback_data="my_progress")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(lesson_content, parse_mode='Markdown', reply_markup=reply_markup)

async def lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درس محدد برقم"""
    try:
        if context.args:
            day = int(context.args[0])
        else:
            progress = db.get_education_progress()
            day = progress['day']
        
        if day < 1 or day > 60:
            await update.message.reply_text("❌ رقم الدرس يجب أن يكون بين 1 و 30")
            return
        
        lesson_content = generator.generate_education_post(day)
        
        keyboard = [
            [InlineKeyboardButton("⬅️ السابق", callback_data=f"lesson_{day-1}"),
             InlineKeyboardButton("➡️ التالي", callback_data=f"lesson_{day+1}")],
            [InlineKeyboardButton("📚 القائمة الكاملة", callback_data="curriculum")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(lesson_content, parse_mode='Markdown', reply_markup=reply_markup)
        
    except ValueError:
        await update.message.reply_text("❌ استخدم: /lesson 5 مثلاً")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أخبار اليوم"""
    await update.message.reply_text("⏳ جاري جلب أخبار اليوم...")
    
    try:
        events = calendar.get_today_high_impact_events()
        summary = generator.generate_daily_news_summary(events)
        await update.message.reply_text(summary, parse_mode='Markdown')
        
        # عرض أول 3 أخبار بالتفصيل
        for event in events[:2]:
            detail = calendar.format_event_for_telegram(event)
            await update.message.reply_text(detail, parse_mode='Markdown')
            
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في جلب الأخبار: {e}")

async def calendar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تقويم الأسبوع"""
    await update.message.reply_text("⏳ جلب تقويم الأسبوع...")
    try:
        events = calendar.get_weekly_calendar()
        if not events:
            await update.message.reply_text("لا توجد بيانات هذا الأسبوع")
            return
            
        message = f"📅 **تقويم الأسبوع - {len(events)} حدث مهم**\n\n"
        for event in events[:15]:
            impact = "🔴" if event.get('impact') in ['high','3'] else "🟡"
            message += f"{impact} {event.get('date','')} {event.get('time','')} - {event.get('title','')[:35]} ({event.get('currency')})\n"
        
        message += "\n#التقويم_الاقتصادي #أسبوع_حافل"
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    progress = db.get_education_progress()
    stats = db.get_stats()
    lesson = get_education_lesson(progress['day'])
    phase_info = get_phase_info(progress['phase'])
    
    status_text = f"""
📊 **حالة البوت**

📚 **التعليم:**
• اليوم الحالي: {progress['day']}/30
• المرحلة: {phase_info['emoji']} {phase_info['name']}
• الدرس الحالي: {lesson['title']}
• التقدم: {int((progress['day']/30)*100)}%

📈 **الإحصائيات:**
• إجمالي المنشورات: {stats['total_posts']}
• منشورات تعليمية: {stats['education_posts']}
• منشورات أخبار: {stats['news_posts']}

🤖 **النظام:**
• الذكاء الاصطناعي: {'✅ مفعل' if generator.enable_ai else '❌ معطل (يستخدم القوالب)'}
• القناة: {config.CHANNEL_ID or 'غير محددة'}
• المنطقة الزمنية: {config.TIMEZONE}

⏰ **الجدولة:**
• تعليم: {', '.join(config.EDUCATION_POST_TIMES)}
• أخبار: {', '.join(config.NEWS_POST_TIMES)}

#حالة_البوت
"""
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def motivational_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post = generator.generate_motivational_post()
    await update.message.reply_text(post, parse_mode='Markdown')

async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post = generator.generate_market_open_post()
    await update.message.reply_text(post, parse_mode='Markdown')

# أوامر المشرفين
async def post_education_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ هذا الأمر للمشرفين فقط")
        return
    
    progress = db.get_education_progress()
    day = progress['day']
    
    if context.args:
        try:
            day = int(context.args[0])
        except:
            pass
    
    content = generator.generate_education_post(day)
    
    # إرسال للقناة
    try:
        if config.CHANNEL_ID:
            await context.bot.send_message(chat_id=config.CHANNEL_ID, text=content, parse_mode='Markdown')
            db.mark_education_posted(f"edu_{day}_{datetime.now().date()}")
            db.next_education_day()
            await update.message.reply_text(f"✅ تم نشر درس اليوم {day} للقناة وتقدمت لليوم التالي")
        else:
            await update.message.reply_text(f"⚠️ CHANNEL_ID غير محدد، هذا محتوى اليوم {day}:\n\n{content}", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ فشل النشر: {e}\n\nالمحتوى:\n{content[:1000]}", parse_mode='Markdown')

async def post_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ للمشرفين فقط")
        return
    
    try:
        events = calendar.get_today_high_impact_events()
        if not events:
            await update.message.reply_text("لا توجد أخبار مهمة اليوم")
            return
        
        summary = generator.generate_daily_news_summary(events)
        
        if config.CHANNEL_ID:
            await context.bot.send_message(chat_id=config.CHANNEL_ID, text=summary, parse_mode='Markdown')
            db.set_last_news_post()
            await update.message.reply_text("✅ تم نشر ملخص الأخبار للقناة")
        else:
            await update.message.reply_text(summary, parse_mode='Markdown')
            
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

async def post_daily_summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await post_news_command(update, context)

async def next_day_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ للمشرفين فقط")
        return
    next_day = db.next_education_day()
    lesson = get_education_lesson(next_day)
    await update.message.reply_text(f"✅ تم الانتقال لليوم {next_day}: {lesson['title']}")

async def set_day_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ للمشرفين فقط")
        return
    try:
        day = int(context.args[0])
        if 1 <= day <= 30:
            db.update_education_progress(day)
            lesson = get_education_lesson(day)
            await update.message.reply_text(f"✅ تم التعيين لليوم {day}: {lesson['title']}")
        else:
            await update.message.reply_text("❌ اليوم بين 1 و 30")
    except:
        await update.message.reply_text("❌ استخدم: /set_day 10")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ للمشرفين فقط")
        return
    db.update_education_progress(1, 1)
    await update.message.reply_text("✅ تمت إعادة الخطة لليوم 1")

async def curriculum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض خطة 30 يوم"""
    text = """
📚 **خطة 30 يوم لاحتراف التداول**

🟢 **المرحلة 1: الأساسيات (1-7)**
1. ما هو التداول
2. المصطلحات
3. أنواع الأسواق
4. الوسطاء
5. المنصات
6. أنواع الأوامر
7. إدارة رأس المال

🔵 **المرحلة 2: التحليل الفني (8-16)**
8. الشموع اليابانية
9. الدعم والمقاومة ⭐ أهم درس
10. الترند
11. المتوسطات
12. RSI
13. نماذج الشموع
14. الفيبوناتشي
15. النماذج الفنية
16. استراتيجية مجمعة

🟡 **المرحلة 3: التحليل الأساسي (17-22)**
17. ما هو التحليل الأساسي
18. أسعار الفائدة
19. التضخم CPI
20. الوظائف NFP
21. الذهب والدولار
22. دمج التحليلين

🔴 **المرحلة 4: علم النفس (23-30)**
23. سيكولوجية التداول
24. خطة التداول
25. أخطاء قاتلة
26. إدارة مخاطر متقدمة
27. بناء استراتيجيتك
28. دفتر التداول
29. ديمو لحقيقي
30. الخلاصة وخارطة الطريق

💡 استخدم /lesson [رقم] للانتقال لدرس محدد
"""
    await update.message.reply_text(text, parse_mode='Markdown')

# Callback handlers
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("lesson_"):
        try:
            day = int(data.split("_")[1])
            if day < 1:
                day = 30
            if day > 30:
                day = 1
            content = generator.generate_education_post(day)
            
            keyboard = [
                [InlineKeyboardButton("⬅️ السابق", callback_data=f"lesson_{day-1}"),
                 InlineKeyboardButton("➡️ التالي", callback_data=f"lesson_{day+1}")],
                [InlineKeyboardButton("📚 الخطة الكاملة", callback_data="curriculum")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(content, parse_mode='Markdown', reply_markup=reply_markup)
        except Exception as e:
            await query.edit_message_text(f"خطأ: {e}")
    
    elif data == "curriculum":
        await curriculum_command(update, context)
    
    elif data == "my_progress":
        progress = db.get_education_progress()
        text = f"📊 تقدمك: اليوم {progress['day']}/30 ({int((progress['day']/30)*100)}%)"
        await query.edit_message_text(text)
