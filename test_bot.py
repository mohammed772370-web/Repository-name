#!/usr/bin/env python3
"""
اختبار البوت بدون تليجرام - يعرض أمثلة للمحتوى
"""

from bot.education_plan import get_education_lesson, get_phase_info
from bot.economic_calendar import calendar
from bot.content_generator import generator
from bot.database import db

def test_education():
    print("\n" + "="*60)
    print("📚 اختبار المنشورات التعليمية")
    print("="*60)
    
    for day in [1, 7, 9, 18, 23]:
        lesson = get_education_lesson(day)
        phase = get_phase_info(lesson['phase'])
        print(f"\n--- اليوم {day}: {lesson['title']} ---")
        print(f"المرحلة: {phase['name']} {phase['emoji']}")
        print(f"Hook: {lesson['hook']}")
        
        content = generator.generate_education_post(day)
        print(content[:500] + "...")
        print("\n" + "-"*60)

def test_news():
    print("\n" + "="*60)
    print("📰 اختبار الأخبار الاقتصادية")
    print("="*60)
    
    events = calendar.get_today_high_impact_events()
    print(f"\nوجد {len(events)} حدث مهم اليوم:\n")
    
    for event in events[:3]:
        print(f"🔴 {event['title']} - {event['currency']} - {event['time']}")
        formatted = calendar.format_event_for_telegram(event)
        print(formatted[:400] + "...\n")
    
    print("\n--- ملخص يومي ---")
    summary = generator.generate_daily_news_summary(events)
    print(summary)

def test_database():
    print("\n" + "="*60)
    print("💾 اختبار قاعدة البيانات")
    print("="*60)
    
    progress = db.get_education_progress()
    print(f"التقدم الحالي: اليوم {progress['day']}/30")
    
    stats = db.get_stats()
    print(f"الإحصائيات: {stats}")

if __name__ == "__main__":
    print("""
╔════════════════════════════════════╗
║  🧪 اختبار بوت التداول             ║
║  بدون الحاجة لتليجرام              ║
╚════════════════════════════════════╝
    """)
    
    test_database()
    test_news()
    test_education()
    
    print("\n✅ انتهى الاختبار - البوت جاهز!")
    print("💡 لتشغيل البوت الحقيقي: python main.py")
