#!/bin/bash
echo "=================================================="
echo " 🤖 بوت قناة التداول الذكي"
echo "=================================================="

# فحص بايثون
if ! command -v python3 &> /dev/null; then
    echo "❌ بايثون غير مثبت!"
    echo "ثبته: sudo apt install python3 python3-pip"
    exit 1
fi

echo "✅ بايثون موجود"
echo "📦 تثبيت المكتبات..."
pip3 install -r requirements.txt --quiet --break-system-packages 2>/dev/null || pip3 install -r requirements.txt --quiet

echo ""
echo "هل هذه أول مرة؟ (y/n)"
read -r choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    python3 إعداد_البوت.py
else
    echo "🚀 تشغيل البوت..."
    python3 main.py
fi
