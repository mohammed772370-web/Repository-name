#!/usr/bin/env python3
"""
أداة صغيرة تساعدك تجيب ايدي القناة وايديك
شغلها بعد ما تحط التوكن
"""

import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "")

if not TOKEN:
    TOKEN = input("الصق توكن البوت: ").strip()

print(f"""
🤖 بوت جلب الايديهات

التوكن: {TOKEN[:10]}...

الآن:
1. هذا البوت سيعمل مؤقتاً
2. اذهب لتليجرام وارسل له أي رسالة
3. حول له رسالة من قناتك
4. سيعطيك كل الايديهات

للإيقاف اضغط Ctrl+C
""")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    text = f"""
📋 **معلومات الرسالة:**

👤 **ايدي حسابك:** `{user.id}`
👤 اسمك: {user.first_name}

💬 **ايدي المحادثة الحالية:** `{chat.id}`
💬 نوعها: {chat.type}
"""
    
    if chat.type in ['channel', 'supergroup', 'group']:
        text += f"""
📢 **ايدي القناة/المجموعة:** `{chat.id}`
🔗 يوزر القناة: @{chat.username if chat.username else 'لا يوجد (خاصة)'}

✅ استخدم هذا الايدي في CHANNEL_ID
"""
    
    if update.message.forward_from_chat:
        fwd = update.message.forward_from_chat
        text += f"""
↗️ **رسالة محولة من:**
📢 ايدي القناة الأصلية: `{fwd.id}`
🔗 يوزرها: @{fwd.username if fwd.username else 'خاصة'}
📌 عنوانها: {fwd.title if fwd.title else ''}

✅ هذا هو CHANNEL_ID الصحيح: `{fwd.id}`
"""
    
    text += f"""
━━━━━━━━━━━━━━━
💡 **كيف تستخدم:**
• ايديك ضعه في ADMIN_IDS
• ايدي القناة ضعه في CHANNEL_ID
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    
    print("🚀 البوت يعمل... ارسل له رسالة في تليجرام")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ إيقاف")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
