#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
لوحة تحكم ويب متكاملة للبوت - تعمل من الجوال
تدير قناة @Trading_TOB
"""

from flask import Flask, render_template_string, request, jsonify, redirect
import os
import json
from datetime import datetime

app = Flask(__name__)

# محاولة استيراد مكونات البوت
try:
    from bot.database import db
    from bot.education_plan import get_education_lesson, get_phase_info, EDUCATION_CURRICULUM
    from bot.economic_calendar import calendar
    from bot.content_generator import generator
    from bot.config import config
    BOT_AVAILABLE = True
except Exception as e:
    print(f"تحذير: {e}")
    BOT_AVAILABLE = False
    # قيم افتراضية
    class Dummy:
        def get_education_progress(self): return {"day": 1, "phase": 1}
        def get_stats(self): return {"total_posts": 0, "education_posts": 0, "news_posts": 0}
        def next_education_day(self): return 2
        def update_education_progress(self, d, p=None): pass
    db = Dummy()
    EDUCATION_CURRICULUM = {1: {"title": "ما هو التداول", "phase": 1}}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم @Trading_TOB</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family: 'Segoe UI', Tahoma, sans-serif; }
        body { background:#0f172a; color:#e2e8f0; padding:10px; }
        .container { max-width:1200px; margin:0 auto; }
        h1 { text-align:center; margin:15px 0; color:#38bdf8; font-size:1.5em; }
        h2 { color:#22c55e; margin:15px 0 10px; font-size:1.2em; }
        .grid { display:grid; grid-template-columns: 1fr; gap:15px; margin:15px 0; }
        @media(min-width:768px){ .grid{ grid-template-columns: repeat(2, 1fr); } }
        .card { background:#1e293b; border-radius:12px; padding:15px; border:1px solid #334155; }
        .card h3 { color:#38bdf8; margin-bottom:12px; font-size:1.1em; }
        .stat { font-size:1.8em; font-weight:bold; color:#22c55e; }
        .btn { background:#0ea5e9; color:white; border:none; padding:10px 15px; border-radius:8px; cursor:pointer; margin:4px; display:inline-block; text-decoration:none; font-size:0.9em; width:100%; text-align:center; }
        .btn:hover { background:#0284c7; }
        .btn-danger { background:#ef4444; }
        .btn-success { background:#22c55e; }
        .btn-warning { background:#f59e0b; }
        .progress-bar { background:#334155; height:18px; border-radius:10px; overflow:hidden; margin:8px 0; }
        .progress-fill { background:linear-gradient(90deg, #0ea5e9, #22c55e); height:100%; transition:width 0.3s; }
        textarea { width:100%; background:#0f172a; color:#e2e8f0; border:1px solid #334155; border-radius:8px; padding:12px; min-height:250px; font-size:0.9em; }
        .lesson-list { max-height:350px; overflow-y:auto; }
        .lesson-item { padding:8px; border-bottom:1px solid #334155; cursor:pointer; font-size:0.85em; }
        .lesson-item:hover { background:#334155; }
        .lesson-item.active { background:#0ea5e9; color:white; }
        select, input { background:#0f172a; color:white; border:1px solid #334155; padding:8px; border-radius:6px; margin:4px 0; width:100%; }
        .alert { padding:12px; border-radius:8px; margin:10px 0; }
        .alert-success { background:#14532d; border:1px solid #22c55e; color:#bbf7d0; }
        .alert-warning { background:#78350f; border:1px solid #f59e0b; color:#fde68a; }
        .alert-info { background:#0c4a6e; border:1px solid #0ea5e9; color:#bae6fd; }
        .channel-badge { background:linear-gradient(90deg, #0ea5e9, #8b5cf6); padding:5px 15px; border-radius:20px; display:inline-block; margin:5px; }
        pre { white-space:pre-wrap; word-wrap:break-word; background:#0f172a; padding:10px; border-radius:8px; font-size:0.85em; }
        .setup-form { background:#1e293b; padding:15px; border-radius:12px; border:2px solid #0ea5e9; margin:15px 0; }
        .step { background:#0f172a; padding:10px; border-radius:8px; margin:8px 0; border-right:4px solid #22c55e; }
    </style>
</head>
<body>
<div class="container">
    <h1>🦅 لوحة تحكم @Trading_TOB</h1>
    <div style="text-align:center;">
        <span class="channel-badge">📈 التداول الاحترافي</span>
        <span class="channel-badge">201 مشترك</span>
        <span class="channel-badge">🤖 بوت ذكي</span>
    </div>

    {% if not env_exists %}
    <div class="setup-form">
        <h2>⚙️ إعداد البوت لأول مرة (من جوالك)</h2>
        <div class="alert alert-warning">
            البوت يحتاج إعداد بسيط مرة واحدة فقط!
        </div>
        
        <div class="step">
            <strong>الخطوة 1:</strong> جيب ايديك من <a href="https://t.me/userinfobot" target="_blank" style="color:#38bdf8;">@userinfobot</a> في تليجرام
        </div>
        
        <form method="POST" action="/setup">
            <label>🔑 توكن البوت (من @BotFather):</label>
            <input type="text" name="bot_token" placeholder="123456:ABC-DEF..." required>
            
            <label>📢 معرف القناة:</label>
            <input type="text" name="channel_id" value="@Trading_TOB" required>
            
            <label>👤 ايدي حسابك (من @userinfobot):</label>
            <input type="text" name="admin_id" placeholder="123456789" required>
            
            <label>🤖 مفتاح AI (اختياري - اتركه فاضي):</label>
            <input type="text" name="ai_key" placeholder="gsk_... أو اتركه فاضي">
            
            <button type="submit" class="btn btn-success" style="margin-top:10px;">💾 حفظ وتشغيل البوت</button>
        </form>
    </div>
    {% else %}
    <div class="alert alert-success">
        ✅ البوت مُعد وجاهز! القناة: {{channel}} | اليوم: {{progress.day}}/30
    </div>
    {% endif %}

    <div class="grid">
        <div class="card">
            <h3>📊 إحصائيات قناتك</h3>
            <div>إجمالي المنشورات: <span class="stat">{{stats.total_posts}}</span></div>
            <div>تعليمية: {{stats.education_posts}} | أخبار: {{stats.news_posts}}</div>
            <div class="progress-bar"><div class="progress-fill" style="width:{{progress_percent}}%"></div></div>
            <div>التقدم: اليوم {{progress.day}}/30 ({{progress_percent}}%)</div>
            <div>المرحلة: {{phase.emoji}} {{phase.name}}</div>
            <div style="margin-top:8px; font-size:0.9em;">📚 الدرس الحالي: {{lesson.title}}</div>
        </div>
        
        <div class="card">
            <h3>⚙️ تحكم سريع من جوالك</h3>
            <button class="btn btn-success" onclick="postEducation()">📚 نشر درس الآن للقناة</button>
            <button class="btn" onclick="postNews()">📰 نشر أخبار الآن</button>
            <button class="btn btn-warning" onclick="nextDay()">⏭️ اليوم التالي</button>
            <div style="display:flex; gap:5px; margin-top:5px;">
                <input type="number" id="dayInput" min="1" max="30" value="{{progress.day}}" style="flex:1;">
                <button class="btn" onclick="setDay()" style="flex:1;">انتقال ليوم</button>
            </div>
            <button class="btn btn-danger" onclick="resetProgress()" style="margin-top:5px;">🔄 إعادة من الصفر</button>
        </div>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>📚 معاينة الدرس (انسخ وانشر)</h3>
            <textarea id="preview">{{preview_content}}</textarea>
            <div style="display:flex; gap:5px; margin-top:8px;">
                <button class="btn" onclick="refreshPreview()" style="flex:1;">🔄 تحديث</button>
                <button class="btn btn-success" onclick="copyContent()" style="flex:1;">📋 نسخ</button>
            </div>
            <div class="alert alert-info" style="margin-top:10px; font-size:0.85em;">
                💡 انسخ هذا النص والصقه في قناتك @Trading_TOB مباشرة إذا أردت نشر يدوي
            </div>
        </div>
        
        <div class="card">
            <h3>📅 خطة 30 يوم - اضغط لمعاينة</h3>
            <div class="lesson-list">
                {% for day, l in curriculum.items() %}
                <div class="lesson-item {% if day==progress.day %}active{% endif %}" onclick="selectDay({{day}})">
                    <strong>اليوم {{day}}:</strong> {{l.title}}<br>
                    <small>{{phases[l.phase].name}} {{phases[l.phase].emoji}}</small>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <div class="card">
        <h3>📰 أخبار اليوم - جاهزة للنشر</h3>
        <div id="news"><pre>{{news_html}}</pre></div>
        <button class="btn" onclick="loadNews()" style="margin-top:10px;">🔄 تحديث الأخبار</button>
    </div>

    <div class="card">
        <h3>🚀 نشر 24 ساعة مجاناً (من جوالك)</h3>
        <div class="alert alert-info">
            تريد البوت يشتغل 24 ساعة حتى لو قفلت جوالك؟ استخدم واحد من هذول (مجاني):
        </div>
        
        <h4>الخيار 1: Render.com (أنصح به - 24 ساعة)</h4>
        <div class="step">
            1. ادخل <a href="https://render.com" target="_blank" style="color:#38bdf8;">render.com</a> وسجل<br>
            2. New + → Background Worker → اربط GitHub<br>
            3. اختر مشروعك → ضع متغيرات البيئة (BOT_TOKEN, CHANNEL_ID=@Trading_TOB)<br>
            4. Create → سيعمل 24 ساعة 🟢
        </div>

        <h4>الخيار 2: Replit.com (أسهل)</h4>
        <div class="step">
            1. ادخل <a href="https://replit.com" target="_blank" style="color:#38bdf8;">replit.com</a><br>
            2. Import from GitHub → الصق رابط مشروعك<br>
            3. Secrets → أضف BOT_TOKEN و CHANNEL_ID<br>
            4. Run → شغال!
        </div>

        <a href="https://github.com/mohammed772370-web/Repository-name" target="_blank" class="btn">📂 فتح المستودع في GitHub</a>
    </div>

    <div class="card" style="text-align:center; margin-top:20px;">
        <h3>🦅 @Trading_TOB - التداول الاحترافي</h3>
        <p style="font-size:0.9em; margin:10px 0;">
            بوابتك للسيطرة على الأسواق المالية (فوركس | كريبتو | أسهم)<br>
            تحليلات دقيقة • إدارة مخاطر صارمة • فرص عالية الجودة
        </p>
        <a href="https://t.me/Trading_TOB" target="_blank" class="btn btn-success">📢 فتح القناة في تليجرام</a>
    </div>
</div>

<script>
function postEducation() {
    if(confirm('نشر درس اليوم لقناة @Trading_TOB؟')) {
        fetch('/api/post_education', {method:'POST'}).then(r=>r.json()).then(d=>{
            alert(d.message);
            if(d.content) {
                document.getElementById('preview').value = d.content;
            }
        });
    }
}
function postNews() {
    fetch('/api/post_news', {method:'POST'}).then(r=>r.json()).then(d=>{
        alert(d.message);
        if(d.content) {
            document.getElementById('news').innerHTML = '<pre>'+d.content+'</pre>';
        }
    });
}
function nextDay() {
    fetch('/api/next_day', {method:'POST'}).then(r=>r.json()).then(d=>{
        alert(d.message); location.reload();
    });
}
function resetProgress() {
    if(confirm('هل أنت متأكد من إعادة الخطة لليوم 1؟')) {
        fetch('/api/reset', {method:'POST'}).then(r=>r.json()).then(d=>{
            alert(d.message); location.reload();
        });
    }
}
function setDay() {
    let day = document.getElementById('dayInput').value;
    fetch('/api/set_day/'+day, {method:'POST'}).then(r=>r.json()).then(d=>{
        alert(d.message); location.reload();
    });
}
function selectDay(day) {
    document.getElementById('dayInput').value = day;
    fetch('/api/preview/'+day).then(r=>r.json()).then(d=>{
        document.getElementById('preview').value = d.content;
    });
}
function refreshPreview() {
    let day = document.getElementById('dayInput').value;
    selectDay(day);
}
function copyContent() {
    let t = document.getElementById('preview');
    t.select(); 
    t.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(t.value).then(()=>{
        alert('✅ تم النسخ! الصقه الآن في قناتك @Trading_TOB');
    }).catch(()=>{
        document.execCommand('copy');
        alert('✅ تم النسخ!');
    });
}
function loadNews() {
    fetch('/api/news').then(r=>r.json()).then(d=>{
        document.getElementById('news').innerHTML = '<pre>'+d.content+'</pre>';
    });
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    env_exists = os.path.exists(".env")
    
    if BOT_AVAILABLE:
        try:
            progress = db.get_education_progress()
            stats = db.get_stats()
            lesson = get_education_lesson(progress['day'])
            phase = get_phase_info(progress['phase'])
            preview = generator.generate_education_post(progress['day'])
            events = calendar.get_today_high_impact_events()
            news_summary = generator.generate_daily_news_summary(events)
            curriculum = EDUCATION_CURRICULUM
            channel = config.CHANNEL_ID or "@Trading_TOB"
        except:
            progress = {"day": 1, "phase": 1}
            stats = {"total_posts": 0, "education_posts": 0, "news_posts": 0}
            lesson = {"title": "ما هو التداول"}
            phase = {"name": "الأساسيات", "emoji": "🟢"}
            preview = "جاري التحميل..."
            news_summary = "جاري جلب الأخبار..."
            curriculum = {1: {"title": "ما هو التداول", "phase": 1}}
            channel = "@Trading_TOB"
    else:
        progress = {"day": 1, "phase": 1}
        stats = {"total_posts": 0, "education_posts": 0, "news_posts": 0}
        lesson = {"title": "ما هو التداول ولماذا الجميع يتحدث عنه؟"}
        phase = {"name": "الأساسيات", "emoji": "🟢"}
        preview = """🟢 **خطة 30 يوم لاحتراف التداول - اليوم 1**

95% من المتداولين يخسرون... هل تعرف لماذا؟ 🤔

📌 **ما هو التداول ولماذا الجميع يتحدث عنه؟**

• الفرق بين الاستثمار والتداول والمضاربة
• حجم سوق الفوركس: 7.5 تريليون دولار يومياً!
• لماذا يفشل معظم المبتدئين في أول 3 أشهر
• 3 قواعد ذهبية قبل أن تضع أول دولار

🎯 **مثال عملي:**
مبتدئ بدأ بـ 1000$ بدون خطة وخسرها في أسبوع. آخر بدأ بنفس المبلغ مع خطة واضحة وحقق 10% في شهر.

✅ **مهمتك اليوم:**
اكتب في دفترك: لماذا تريد أن تتعلم التداول؟

📚 اليوم 1/30 | 🟢 المرحلة 1: الأساسيات
#البداية #أساسيات_التداول #خطة_30_يوم"""
        news_summary = """📅 **التقويم الاقتصادي اليوم**

🔥 لدينا 3 أخبار مهمة اليوم:

1. 🔴 15:30 - تقرير الوظائف NFP (USD)
2. 🔴 15:30 - التضخم CPI (USD)  
3. 🔴 21:00 - قرار الفائدة الفيدرالي (USD)

⚠️ تنبيه: لا تدخل صفقات قبل الأخبار الحمراء بـ 30 دقيقة"""
        curriculum = {
            1: {"title": "ما هو التداول ولماذا الجميع يتحدث عنه؟", "phase": 1},
            2: {"title": "لغة المتداولين - المصطلحات", "phase": 1},
            3: {"title": "أنواع الأسواق", "phase": 1},
            7: {"title": "إدارة رأس المال", "phase": 1},
            9: {"title": "الدعم والمقاومة - أهم درس", "phase": 2},
            18: {"title": "أسعار الفائدة", "phase": 3},
            20: {"title": "الوظائف NFP", "phase": 3},
        }
        channel = "@Trading_TOB"
    
    phases = {
        1: {"name": "الأساسيات", "emoji": "🟢"},
        2: {"name": "التحليل الفني", "emoji": "🔵"},
        3: {"name": "التحليل الأساسي", "emoji": "🟡"},
        4: {"name": "علم النفس", "emoji": "🔴"},
    }
    
    return render_template_string(HTML_TEMPLATE,
        stats=stats,
        progress=progress,
        progress_percent=int((progress['day']/30)*100),
        lesson=lesson,
        phase=phase,
        preview_content=preview,
        news_html=news_summary,
        curriculum=curriculum,
        phases=phases,
        channel=channel,
        env_exists=env_exists
    )

@app.route('/setup', methods=['POST'])
def setup():
    bot_token = request.form.get('bot_token', '').strip()
    channel_id = request.form.get('channel_id', '').strip() or "@Trading_TOB"
    admin_id = request.form.get('admin_id', '').strip()
    ai_key = request.form.get('ai_key', '').strip()
    
    if not bot_token:
        return "❌ التوكن مطلوب! <a href='/'>رجوع</a>"
    
    env_content = f"""BOT_TOKEN={bot_token}
CHANNEL_ID={channel_id}
ADMIN_IDS={admin_id}

OPENAI_API_KEY={ai_key}
OPENAI_MODEL=llama-3.1-8b-instant
OPENAI_BASE_URL=https://api.groq.com/openai/v1

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
        f.write(env_content)
    
    return """
    <html dir="rtl" style="background:#0f172a; color:white; font-family:sans-serif; text-align:center; padding:50px;">
    <h1 style="color:#22c55e;">✅ تم حفظ الإعدادات!</h1>
    <p>الآن البوت جاهز للعمل مع قناتك @Trading_TOB</p>
    <p>لتشغيل البوت 24 ساعة، استخدم Render أو Replit</p>
    <p>أو شغل: <code>python main.py</code> من جهازك</p>
    <br>
    <a href="/" style="background:#0ea5e9; color:white; padding:12px 25px; border-radius:8px; text-decoration:none;">🏠 رجوع للوحة التحكم</a>
    <br><br>
    <a href="https://t.me/Trading_TOB" target="_blank" style="background:#22c55e; color:white; padding:12px 25px; border-radius:8px; text-decoration:none;">📢 فتح قناتك</a>
    </html>
    """

@app.route('/api/post_education', methods=['POST'])
def api_post_education():
    try:
        if BOT_AVAILABLE:
            progress = db.get_education_progress()
            content = generator.generate_education_post(progress['day'])
            return jsonify({"message": f"✅ تم تجهيز درس اليوم {progress['day']} - انسخه وانشره في @Trading_TOB", "content": content})
        else:
            return jsonify({"message": "البوت غير مُعد بعد، استخدم الإعداد أولاً"})
    except Exception as e:
        return jsonify({"message": f"خطأ: {e}"})

@app.route('/api/post_news', methods=['POST'])
def api_post_news():
    try:
        if BOT_AVAILABLE:
            events = calendar.get_today_high_impact_events()
            content = generator.generate_daily_news_summary(events)
            return jsonify({"message": f"✅ تم تجهيز ملخص {len(events)} خبر", "content": content})
        else:
            return jsonify({"message": "البوت غير مُعد"})
    except Exception as e:
        return jsonify({"message": f"خطأ: {e}"})

@app.route('/api/next_day', methods=['POST'])
def api_next_day():
    try:
        if BOT_AVAILABLE:
            next_day = db.next_education_day()
            return jsonify({"message": f"✅ تم الانتقال لليوم {next_day}"})
        return jsonify({"message": "غير متاح"})
    except Exception as e:
        return jsonify({"message": f"خطأ: {e}"})

@app.route('/api/reset', methods=['POST'])
def api_reset():
    try:
        if BOT_AVAILABLE:
            db.update_education_progress(1, 1)
            return jsonify({"message": "✅ تمت إعادة الخطة لليوم 1"})
        return jsonify({"message": "غير متاح"})
    except Exception as e:
        return jsonify({"message": f"خطأ: {e}"})

@app.route('/api/set_day/<int:day>', methods=['POST'])
def api_set_day(day):
    try:
        if BOT_AVAILABLE and 1 <= day <= 30:
            db.update_education_progress(day)
            return jsonify({"message": f"✅ تم التعيين لليوم {day}"})
        return jsonify({"message": "رقم غير صحيح"})
    except Exception as e:
        return jsonify({"message": f"خطأ: {e}"})

@app.route('/api/preview/<int:day>')
def api_preview(day):
    try:
        if BOT_AVAILABLE:
            content = generator.generate_education_post(day)
            return jsonify({"content": content})
        return jsonify({"content": "البوت غير مُعد"})
    except Exception as e:
        return jsonify({"content": f"خطأ: {e}"})

@app.route('/api/news')
def api_news():
    try:
        if BOT_AVAILABLE:
            events = calendar.get_today_high_impact_events()
            content = generator.generate_daily_news_summary(events)
            return jsonify({"content": content})
        return jsonify({"content": "البوت غير مُعد"})
    except Exception as e:
        return jsonify({"content": f"خطأ: {e}"})

if __name__ == '__main__':
    print("🌐 لوحة تحكم @Trading_TOB: http://localhost:5000")
    print("📱 تعمل من الجوال مباشرة!")
    app.run(host='0.0.0.0', port=5000, debug=False)
