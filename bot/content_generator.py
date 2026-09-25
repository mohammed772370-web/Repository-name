import os
from typing import Optional, Dict
from .education_plan import get_education_lesson, get_phase_info
from .economic_calendar import calendar

class ContentGenerator:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.enable_ai = os.getenv("ENABLE_AI_GENERATION", "True").lower() == "true" and bool(self.openai_key)
        
        self.client = None
        if self.enable_ai:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.openai_key, base_url=self.base_url)
                print(f"✅ تم تفعيل الذكاء الاصطناعي - النموذج: {self.model}")
            except Exception as e:
                print(f"⚠️ فشل تفعيل OpenAI: {e}")
                self.enable_ai = False

    def _call_ai(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """استدعاء الذكاء الاصطناعي"""
        if not self.enable_ai or not self.client:
            return None
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"خطأ AI: {e}")
            return None

    def generate_education_post(self, day: int) -> str:
        """توليد منشور تعليمي ليوم محدد"""
        lesson = get_education_lesson(day)
        phase_info = get_phase_info(lesson['phase'])

        # إذا كان AI مفعل، نحسن المحتوى
        if self.enable_ai:
            ai_content = self._generate_education_with_ai(lesson, phase_info, day)
            if ai_content:
                return ai_content

        # القالب الأساسي بدون AI
        return self._generate_education_template(lesson, phase_info, day)

    def _generate_education_with_ai(self, lesson: Dict, phase_info: Dict, day: int) -> Optional[str]:
        system_prompt = """
أنت خبير تداول محترف ومدرس مبدع لقناة تليجرام عربية للمبتدئين.
مهمتك كتابة منشور تعليمي جذاب يحافظ على انتباه القارئ.

القواعد:
- اكتب بالعربية الفصحى مع لمسة عامية خفيفة محببة
- استخدم إيموجي باعتدال
- ابدأ بـ Hook قوي يجذب الانتباه
- قسم المحتوى بنقاط واضحة
- أضف مثال عملي
- اختم بمهمة تطبيقية
- اجعل المنشور بين 300-500 كلمة
- استخدم تنسيق تليجرام Markdown
- حافظ على الأسلوب التحفيزي والبسيط
"""

        prompt = f"""
اكتب منشور تعليمي لليوم {day} من خطة تعليم التداول.

المرحلة: {phase_info['name']} {phase_info['emoji']}
عنوان الدرس: {lesson['title']}
الخطاف المقترح: {lesson['hook']}
النقاط الرئيسية: {', '.join(lesson['points'])}
المهمة: {lesson['task']}
الهاشتاقات: {lesson['hashtags']}

اجعله منشور قناة تليجرام احترافي يحافظ على انتباه المبتدئين ويبني أساس قوي.
"""

        ai_result = self._call_ai(prompt, system_prompt)
        if ai_result:
            # إضافة تذييل ثابت
            footer = f"""

━━━━━━━━━━━━━━━
📚 اليوم {day}/30 | {phase_info['emoji']} المرحلة {lesson['phase']}: {phase_info['name']}
📊 التقدم: {int((day/30)*100)}% من الأساسيات

💬 سؤال اليوم: ما أكثر نقطة استفدت منها؟ شاركنا في التعليقات 👇
🔔 فعل التنبيهات حتى لا يفوتك درس الغد

{lesson['hashtags']} #خطة_30_يوم
"""
            return ai_result + footer
        return None

    def _generate_education_template(self, lesson: Dict, phase_info: Dict, day: int) -> str:
        """قالب بدون AI - احترافي وجاهز"""
        progress_bar = self._create_progress_bar(day, 30)
        
        points_text = "\n".join([f"• {point}" for point in lesson['points']])

        post = f"""
{phase_info['emoji']} **خطة 30 يوم لاحتراف التداول - اليوم {day}**

{lesson['hook']}

━━━━━━━━━━━━━━━
📌 **{lesson['title']}**

{points_text}

━━━━━━━━━━━━━━━
🎯 **مثال عملي سريع:**
{self._get_practical_example(day)}

━━━━━━━━━━━━━━━
✅ **مهمتك اليوم:**
{lesson['task']}

━━━━━━━━━━━━━━━
{progress_bar}
📚 اليوم {day}/30 | {phase_info['emoji']} المرحلة {lesson['phase']}: {phase_info['name']}
📊 التقدم: {int((day/30)*100)}% من الأساسيات

💬 سؤال اليوم: ما أكثر نقطة استفدت منها؟ شاركنا 👇
🔔 فعل التنبيهات حتى لا يفوتك درس الغد

{lesson['hashtags']} #خطة_30_يوم #تعليم_تداول
"""
        return post.strip()

    def _create_progress_bar(self, current: int, total: int) -> str:
        percent = int((current/total)*100)
        filled = int(percent/10)
        empty = 10 - filled
        return f"{'█'*filled}{'░'*empty} {percent}%"

    def _get_practical_example(self, day: int) -> str:
        examples = {
            1: "مبتدئ بدأ بـ 1000$ بدون خطة وخسرها في أسبوع. آخر بدأ بنفس المبلغ مع خطة واضحة وحقق 10% في شهر. الفرق؟ الهدف والخطة!",
            2: "سعر EUR/USD = 1.0850، السبريد 1 نقطة، اللوت 0.10، النقطة = 1$. لو ربحت 20 نقطة = 20$ ربح",
            7: "حساب 1000$، مخاطرة 1% = 10$ فقط للصفقة. ستوب 50 نقطة → اللوت = 0.02. حتى لو خسرت 10 صفقات متتالية، تخسر 100$ فقط!",
            9: "الذهب عند 2030 مقاومة قوية، ارتد منها 3 مرات. المرة الرابعة كسرها وصعد 30$! المقاومة القوية إذا انكسرت تصبح دعم قوي.",
            18: "الفيدرالي رفع الفائدة من 5.25% إلى 5.50% → الدولار صعد 100 نقطة والذهب هبط 25$ في ساعتين!",
        }
        return examples.get(day, "افتح الشارت الآن وطبق ما تعلمته. التطبيق العملي أهم من 10 دروس نظرية!")

    def generate_news_post(self, event: Dict) -> str:
        """توليد منشور خبر اقتصادي"""
        if self.enable_ai:
            ai_post = self._generate_news_with_ai(event)
            if ai_post:
                return ai_post
        
        return calendar.format_event_for_telegram(event)

    def _generate_news_with_ai(self, event: Dict) -> Optional[str]:
        system_prompt = """
أنت محلل اقتصادي محترف لقناة تليجرام تداول.
اكتب تحليل سريع للخبر الاقتصادي بأسلوب مبسط للمبتدئين مع الحفاظ على الاحترافية.
استخدم العربية، إيموجي، وتنسيق تليجرام.
"""
        prompt = f"""
حلل هذا الخبر الاقتصادي لمنشور تليجرام:

الخبر: {event.get('title')}
العملة: {event.get('currency')}
التأثير: {event.get('impact')}
الوقت: {event.get('time')}
المتوقع: {event.get('forecast')}
السابق: {event.get('previous')}

اكتب منشور شامل: ترجمة الخبر، أهميته، تأثيره المتوقع على الدولار والذهب، ونصيحة للمتداولين.
اجعله قصير 200-300 كلمة.
"""
        return self._call_ai(prompt, system_prompt)

    def generate_daily_news_summary(self, events) -> str:
        """ملخص يومي للأخبار"""
        if self.enable_ai and events:
            system_prompt = "أنت محلل اقتصادي، اكتب ملخص يومي جذاب للتقويم الاقتصادي بالعربية"
            events_text = "\n".join([f"- {e.get('time')} {e.get('title')} ({e.get('currency')} - {e.get('impact')})" for e in events[:8]])
            prompt = f"اكتب ملخص يومي لهذه الأخبار لقناة تليجرام:\n{events_text}\nاجعله جذاب مع تنبيهات ونصائح، 300 كلمة"
            ai_result = self._call_ai(prompt, system_prompt)
            if ai_result:
                return ai_result
        
        return calendar.format_daily_summary(events)

    def generate_motivational_post(self) -> str:
        """منشور تحفيزي"""
        posts = [
            """
🔥 **تذكير مهم لكل متداول مبتدئ**

❌ لا تبحث عن استراتيجية سحرية
❌ لا تبحث عن مؤشر يربح 100%
❌ لا تدخل صفقات لأن فلان قال

✅ ابحث عن:
• إدارة رأس مال صارمة
• خطة واضحة تلتزم بها
• انضباط نفسي
• تعلم مستمر

💡 **الحقيقة:** 80% من النجاح هو إدارة مخاطر وعلم نفس، 20% فقط تحليل!

📌 اليوم أغلق المنصة بعد 3 صفقات، سواء رابح أو خاسر. الانضباط أهم من الربح.

#تحفيز #انضباط #تداول_ناجح
""",
            """
💭 **قصة قصيرة - العبرة**

متداول مبتدئ سأل محترف:
- كم سنة حتى أصبح محترف؟
- 3 سنوات
- وإذا اجتهدت أكثر؟
- 5 سنوات
- لماذا؟!
- لأنك ستنشغل بالسرعة وتنسى التعلم!

🐢 **التداول ماراثون وليس سباق 100 متر**

• شهر 1-3: تعلم الأساسيات
• شهر 4-6: بناء استراتيجية
• شهر 7-12: انضباط وتطبيق
• بعد سنة: تبدأ ترى نتائج

⏰ لا تستعجل، السوق موجود كل يوم!

#قصة #صبر #رحلة_التداول
""",
            """
📊 **إحصائية صادمة:**

• 70% يخسرون بسبب عدم وضع ستوب لوس
• 20% يخسرون بسبب الطمع ولوت كبير
• 10% فقط يخسرون بسبب تحليل خاطئ

👀 **لاحظ:** التحليل ليس المشكلة الرئيسية!

🔑 **الحل:**
1. لا تدخل صفقة بدون ستوب أبداً
2. لا تخاطر أكثر من 1-2% في الصفقة
3. لا تفتح أكثر من 3 صفقات في اليوم

💰 حافظ على رأس مالك، والربح سيأتي!

#إحصائيات #إدارة_مخاطر
"""
        ]
        import random
        return random.choice(posts)

    def generate_market_open_post(self) -> str:
        return """
🌅 **افتتاح السوق - بداية يوم جديد**

💱 **حالة الأسواق الآن:**
• الفوركس: مفتوح 24 ساعة 🟢
• الذهب: يتداول الآن 🟢
• الأسهم الأمريكية: تفتح 4:30 مساءً بتوقيت الرياض

📌 **خطة اليوم:**
1. راجع التقويم الاقتصادي (ننشره 8 صباحاً)
2. حلل الشارت على الفريم اليومي
3. حدد مناطق الدخول والستوب قبل الدخول
4. لا تدخل إلا إذا توفرت كل شروط استراتيجيتك

☕ خذ قهوتك، حلل بهدوء، وتداول بانضباط

يوم موفق للجميع! 🚀

#افتتاح_السوق #خطة_اليوم
"""

generator = ContentGenerator()
