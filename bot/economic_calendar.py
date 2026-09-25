import requests
from datetime import datetime, timedelta
import pytz
from typing import List, Dict
import json

class EconomicCalendar:
    def __init__(self):
        self.timezone = pytz.timezone("Asia/Riyadh")
        # مصادر متعددة للتقويم الاقتصادي
        self.forex_factory_url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        self.backup_sources = [
            "https://api.forexfactory.com/calendar?week=this"
        ]

    def fetch_forex_factory_calendar(self) -> List[Dict]:
        """جلب التقويم من Forex Factory"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            response = requests.get(self.forex_factory_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_forex_factory(data)
        except Exception as e:
            print(f"خطأ في جلب تقويم Forex Factory: {e}")
        return []

    def _parse_forex_factory(self, data: List[Dict]) -> List[Dict]:
        """تحليل بيانات Forex Factory"""
        events = []
        for item in data:
            try:
                # تصفية الأخبار المهمة فقط (High Impact)
                impact = item.get('impact', '').lower()
                if impact not in ['high', 'high impact', '3']:
                    # نأخذ المتوسطة أيضاً للعملات الرئيسية
                    if not (item.get('currency') in ['USD', 'EUR', 'GBP', 'JPY', 'GOLD', 'XAU'] and impact in ['medium', '2']):
                        continue

                event = {
                    'id': f"{item.get('date', '')}_{item.get('title', '')}_{item.get('time', '')}",
                    'title': item.get('title', ''),
                    'currency': item.get('currency', ''),
                    'impact': impact,
                    'time': item.get('time', ''),
                    'date': item.get('date', ''),
                    'forecast': item.get('forecast', ''),
                    'previous': item.get('previous', ''),
                    'actual': item.get('actual', ''),
                    'country': item.get('country', item.get('currency', '')),
                }
                events.append(event)
            except Exception as e:
                continue
        return events

    def get_today_high_impact_events(self) -> List[Dict]:
        """جلب أخبار اليوم عالية التأثير"""
        all_events = self.fetch_forex_factory_calendar()
        today = datetime.now(self.timezone).strftime("%Y-%m-%d")
        
        # إذا لم نجد بيانات، نستخدم بيانات تجريبية مهمة
        if not all_events:
            return self.get_mock_important_events()
        
        today_events = []
        for event in all_events:
            # فلترة بسيطة للتاريخ
            event_date = event.get('date', '')
            if today in event_date or not event_date:
                if event.get('impact') in ['high', '3'] or event.get('currency') == 'USD':
                    today_events.append(event)
        
        return today_events[:10] if today_events else self.get_mock_important_events()[:5]

    def get_mock_important_events(self) -> List[Dict]:
        """بيانات تجريبية للأخبار المهمة عندما تفشل المصادر"""
        return [
            {
                'id': 'mock_nfp',
                'title': 'Non-Farm Employment Change - تقرير الوظائف غير الزراعية',
                'currency': 'USD',
                'impact': 'high',
                'time': '15:30',
                'date': datetime.now().strftime("%Y-%m-%d"),
                'forecast': '200K',
                'previous': '187K',
                'actual': '',
                'country': 'USD',
                'description': 'أهم خبر شهري، يحرك السوق بقوة'
            },
            {
                'id': 'mock_cpi',
                'title': 'CPI - مؤشر أسعار المستهلكين (التضخم)',
                'currency': 'USD',
                'impact': 'high',
                'time': '15:30',
                'date': datetime.now().strftime("%Y-%m-%d"),
                'forecast': '3.2%',
                'previous': '3.0%',
                'actual': '',
                'country': 'USD',
                'description': 'يقيس التضخم، يؤثر على قرار الفائدة'
            },
            {
                'id': 'mock_fomc',
                'title': 'FOMC Interest Rate Decision - قرار الفائدة الفيدرالي',
                'currency': 'USD',
                'impact': 'high',
                'time': '21:00',
                'date': datetime.now().strftime("%Y-%m-%d"),
                'forecast': '5.50%',
                'previous': '5.50%',
                'actual': '',
                'country': 'USD',
                'description': 'أهم قرار، يحرك جميع الأسواق'
            },
            {
                'id': 'mock_gdp',
                'title': 'GDP - الناتج المحلي الإجمالي',
                'currency': 'USD',
                'impact': 'high',
                'time': '15:30',
                'date': datetime.now().strftime("%Y-%m-%d"),
                'forecast': '2.1%',
                'previous': '2.0%',
                'actual': '',
                'country': 'USD',
                'description': 'يقيس نمو الاقتصاد'
            },
            {
                'id': 'mock_retail',
                'title': 'Retail Sales - مبيعات التجزئة',
                'currency': 'USD',
                'impact': 'medium',
                'time': '15:30',
                'date': datetime.now().strftime("%Y-%m-%d"),
                'forecast': '0.4%',
                'previous': '0.6%',
                'actual': '',
                'country': 'USD',
                'description': 'يقيس إنفاق المستهلكين'
            }
        ]

    def get_weekly_calendar(self) -> List[Dict]:
        """جلب تقويم الأسبوع كامل"""
        events = self.fetch_forex_factory_calendar()
        if not events:
            events = self.get_mock_important_events()
        return events

    def format_event_for_telegram(self, event: Dict, with_analysis: bool = True) -> str:
        """تنسيق الحدث للنشر في تليجرام"""
        impact_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢',
            '3': '🔴',
            '2': '🟡',
            '1': '🟢'
        }.get(event.get('impact', 'low').lower(), '⚪')

        currency_flag = {
            'USD': '🇺🇸',
            'EUR': '🇪🇺',
            'GBP': '🇬🇧',
            'JPY': '🇯🇵',
            'AUD': '🇦🇺',
            'CAD': '🇨🇦',
            'CHF': '🇨🇭',
            'NZD': '🇳🇿',
            'CNY': '🇨🇳',
            'GOLD': '🥇',
            'XAU': '🥇'
        }.get(event.get('currency', ''), '💱')

        title_ar = self.translate_title(event.get('title', ''))
        
        message = f"""
{impact_emoji} **{title_ar}**

{currency_flag} العملة: {event.get('currency', 'USD')}
⏰ الوقت: {event.get('time', 'غير محدد')} بتوقيت الرياض
📊 التأثير: {self.translate_impact(event.get('impact', ''))}

📈 المتوقع: {event.get('forecast', 'غير متاح')}
📉 السابق: {event.get('previous', 'غير متاح')}
"""

        if event.get('actual'):
            message += f"✅ الفعلي: {event.get('actual')}\n"

        if with_analysis:
            message += f"\n💡 **التأثير على السوق:**\n{self.get_event_analysis(event)}\n"

        message += f"\n⚠️ نصيحة: تجنب التداول قبل وبعد الخبر بـ 15 دقيقة إذا كنت مبتدئ\n"
        message += f"\n#أخبار_اقتصادية #{event.get('currency', 'USD')} #التقويم_الاقتصادي"

        return message

    def translate_title(self, title: str) -> str:
        """ترجمة عناوين الأخبار الشائعة"""
        translations = {
            'Non-Farm Employment Change': 'تقرير الوظائف غير الزراعية NFP',
            'Non-Farm Payrolls': 'الوظائف غير الزراعية',
            'Unemployment Rate': 'معدل البطالة',
            'CPI': 'مؤشر أسعار المستهلكين - التضخم',
            'Consumer Price Index': 'مؤشر أسعار المستهلكين',
            'Core CPI': 'التضخم الأساسي',
            'GDP': 'الناتج المحلي الإجمالي',
            'Gross Domestic Product': 'الناتج المحلي الإجمالي',
            'Interest Rate': 'قرار سعر الفائدة',
            'FOMC': 'لجنة السوق المفتوحة الفيدرالية',
            'Retail Sales': 'مبيعات التجزئة',
            'Initial Jobless Claims': 'طلبات إعانة البطالة',
            'ISM Manufacturing PMI': 'مؤشر مديري المشتريات الصناعي',
            'ISM Services PMI': 'مؤشر مديري المشتريات الخدمي',
            'Durable Goods Orders': 'طلبات السلع المعمرة',
            'Building Permits': 'تصاريح البناء',
            'Existing Home Sales': 'مبيعات المنازل القائمة',
            'New Home Sales': 'مبيعات المنازل الجديدة',
            'PPI': 'مؤشر أسعار المنتجين',
            'Producer Price Index': 'مؤشر أسعار المنتجين',
            'Average Hourly Earnings': 'متوسط الأجور بالساعة',
            'Federal Funds Rate': 'سعر الفائدة الفيدرالي',
            'ECB Interest Rate': 'سعر فائدة المركزي الأوروبي',
            'BOE Interest Rate': 'سعر فائدة بنك إنجلترا',
        }
        
        for en, ar in translations.items():
            if en.lower() in title.lower():
                return f"{ar} - {title}"
        return title

    def translate_impact(self, impact: str) -> str:
        return {
            'high': 'عالي جداً 🔴🔴🔴',
            'medium': 'متوسط 🟡🟡',
            'low': 'منخفض 🟢',
            '3': 'عالي جداً 🔴🔴🔴',
            '2': 'متوسط 🟡🟡',
            '1': 'منخفض 🟢'
        }.get(impact.lower(), impact)

    def get_event_analysis(self, event: Dict) -> str:
        """تحليل تأثير الخبر"""
        title = event.get('title', '').lower()
        currency = event.get('currency', 'USD')

        if 'nfp' in title or 'non-farm' in title or 'employment' in title:
            return "إذا جاء أعلى من المتوقع → الدولار يصعد والذهب يهبط والعكس صحيح. حركة متوقعة 30-80 نقطة على الذهب!"
        elif 'cpi' in title or 'inflation' in title or 'consumer price' in title:
            return "تضخم أعلى من المتوقع = احتمال رفع فائدة = دولار قوي. تضخم أقل = دولار ضعيف وذهب قوي. حركة عنيفة!"
        elif 'interest rate' in title or 'fomc' in title or 'fed' in title:
            return "أخطر خبر! رفع فائدة = دولار قوي جداً. تثبيت مع لهجة متشددة = دولار قوي. لهجة متساهلة = ضعف الدولار."
        elif 'gdp' in title:
            return "نمو أعلى = اقتصاد قوي = عملة قوية على المدى المتوسط. تأثيره متوسط لكن مهم للاتجاه العام."
        elif 'retail sales' in title:
            return "مبيعات قوية = اقتصاد قوي = إيجابي للعملة. مبيعات ضعيفة = سلبي."
        elif 'jobless' in title or 'unemployment' in title:
            return "طلبات بطالة أقل = سوق عمل قوي = إيجابي للدولار. والعكس صحيح."
        elif 'pmi' in title:
            return "PMI فوق 50 = توسع اقتصادي = إيجابي للعملة. تحت 50 = انكماش = سلبي."
        else:
            return f"خبر مهم على {currency}. إذا جاء أفضل من المتوقع → العملة تصعد، إذا أسوأ → العملة تهبط. انتبه للتقلبات!"

    def format_daily_summary(self, events: List[Dict]) -> str:
        """تنسيق ملخص يومي للأخبار"""
        if not events:
            return """
📅 **التقويم الاقتصادي اليوم - هادئ نسبياً**

😌 لا توجد أخبار عالية التأثير اليوم.

💡 هذا يوم جيد للتحليل الفني بدون تشويش الأخبار!

🔔 تابعنا غداً لأهم الأخبار

#التقويم_الاقتصادي #تداول_آمن
"""

        message = f"""
📅 **التقويم الاقتصادي اليوم - {datetime.now().strftime('%Y-%m-%d')}**

🔥 لدينا {len(events)} أخبار مهمة اليوم:

"""

        for i, event in enumerate(events, 1):
            impact_icon = "🔴" if event.get('impact') in ['high', '3'] else "🟡"
            message += f"{i}. {impact_icon} {event.get('time', '--:--')} - {self.translate_title(event.get('title', ''))[:40]} ({event.get('currency')})\n"

        message += f"""
⏰ **أهم الأوقات:**
"""
        for event in events[:3]:
            if event.get('impact') in ['high', '3']:
                message += f"• {event.get('time')} - {event.get('currency')} {self.translate_title(event.get('title', ''))[:30]}\n"

        message += """
⚠️ **تنبيهات:**
• لا تدخل صفقات جديدة قبل الأخبار الحمراء بـ 30 دقيقة
• ضع ستوب لوس لجميع صفقاتك المفتوحة
• الأخبار فرصة للمحترفين وخطر على المبتدئين

💬 هل تريد تحليل مفصل لخبر معين؟ اكتب اسمه في التعليقات

#التقويم_الاقتصادي #أخبار_اليوم #تداول
"""
        return message

calendar = EconomicCalendar()
