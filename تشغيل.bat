@echo off
chcp 65001 >nul
title بوت قناة التداول الذكي

echo ==================================================
echo  🤖 بوت قناة التداول الذكي
echo ==================================================
echo.

REM فحص بايثون
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ بايثون غير مثبت!
    echo.
    echo 👉 اذهب لـ https://www.python.org/downloads/
    echo    حمل بايثون وثبته مع تفعيل Add to PATH
    echo.
    pause
    exit /b
)

echo ✅ بايثون موجود
echo.

REM تثبيت المكتبات
echo 📦 تثبيت المكتبات...
pip install -r requirements.txt --quiet

echo.
echo ==================================================
echo  هل هذه أول مرة تشغل البوت؟
echo ==================================================
echo  1 = نعم، أريد الإعداد
echo  2 = لا، شغل البوت مباشرة
echo.

set /p choice="اختر 1 أو 2: "

if "%choice%"=="1" (
    python إعداد_البوت.py
) else (
    echo 🚀 تشغيل البوت...
    python main.py
)

pause
