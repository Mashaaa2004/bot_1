import os 
import logging 
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton 
from telegram.ext import ( 
    ApplicationBuilder, CommandHandler, MessageHandler,  
    CallbackQueryHandler, ConversationHandler, filters 
)

 
# === LOGGING O'RNATISH === 
logging.basicConfig( 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO 
) 
logger = logging.getLogger(__name__) 
 
# === TOKEN VA ADMIN CHAT ID === 
TOKEN = '7594276073:AAF0LXwlZ8QUrYleljo112oD9L8EzQaBFO8' 
ADMIN_CHAT_ID = 5778681418 
 
# === STATES === 
ASK_NAME, ASK_SURNAME, ASK_PHONE = range(3) 
 
# === FOYDALANUVCHILARNI SAQLASH === 
users_data = {} 
 
# === DARS MA'LUMOTLARI === 
LESSONS = { 
    "html": [
         {
            "lesson": "1️⃣ HTML nima?",
            "video_url": "https://youtu.be/9dUhZq9dkHM?feature=shared",
            "pptx_file": "html_lesson_1.pptx"
        },
        "1️⃣ HTML nima?\n2️⃣ HTML hujjatining tuzilishi.\n3️⃣ Brauzerlar va kod muxarrirlari.", 
        "4️⃣ Teglar va atributlar: <p>, <b>, <img>.\n5️⃣ Rasm va havolalar qo'shish.", 
        "6️⃣ Ro‘yxatlar: <ol>, <ul>.\n7️⃣ Jadvallar bilan ishlash: <table>.", 
        "8️⃣ Formalar: <form>, <input>.\n9️⃣ Multimedia qo‘shish: <video>, <audio>.", 
        "🔟 HTML5: Semantik teglar, <canvas>, <svg>." 
    ], 
    "css": [ 
        "1️⃣ CSS nima?\n2️⃣ CSSni HTML bilan bog'lash.", 
        "3️⃣ Matn va shriftlarni boshqarish.\n4️⃣ Fonga rasm va rang sozlash.", 
        "5️⃣ Chegaralar va bo'shliqlarni sozlash.\n6️⃣ Flexbox va Grid tizimi.", 
        "7️⃣ Animatsiyalar va transformlar.\n8️⃣ Oddiy javob beruvchi dizayn yaratish." 
    ] 
} 
 
# === INLINE TUGMALAR YARATISH === 
def generate_lesson_buttons(category): 
    return [[InlineKeyboardButton(f"Dars {i+1}", callback_data=f'{category}_lesson_{i+1}')] for i in range(len(LESSONS[category]))] 
 
# === START KOMANDASI === 
async def start(update: Update, context): 
    chat_id = update.effective_user.id 
 
    if chat_id in users_data: 
        user_info = users_data[chat_id] 
        progress = user_info.get("progress", {"html": 0, "css": 0}) 
        await update.message.reply_text( 
            f"👋 Xush kelibsiz qaytadan!\n" 
            f"❌ Siz allaqachon ro'yxatdan o'tgansiz.\n" 
            f"👤 Ism: {user_info['name']}\n" 
            f"👤 Familiya: {user_info['surname']}\n" 
            f"📞 Telefon: {user_info['phone']}" 
        ) 
        await offer_lessons(update, progress) 
        return ConversationHandler.END 
 
    await update.message.reply_text("Assalomu alaykum! Avval sizni ro'yxatdan o'tkazamiz.\n" 
                                    "Iltimos, o'zingizning ismingizni kiriting.") 
    return ASK_NAME 
 
# === RO'YXATDAN O'TISH BOSQICHLARI === 
async def ask_name(update: Update, context): 
    context.user_data["name"] = update.message.text.strip() 
    await update.message.reply_text("Rahmat! Endi familiyangizni kiriting.") 
    return ASK_SURNAME 
 
async def ask_surname(update: Update, context): 
    context.user_data["surname"] = update.message.text.strip() 
    await update.message.reply_text("Endi telefon raqamingizni +998********* formatida kiriting.") 
    return ASK_PHONE 
 
async def ask_phone(update: Update, context): 
    phone = update.message.text.strip() 
 
    if not phone.startswith('+998') or not phone[1:].isdigit() or len(phone) != 13: 
        await update.message.reply_text( 
            "❌ Iltimos, telefon raqamingizni to'g'ri formatda kiriting: +998*********" 
        ) 
        return ASK_PHONE 
 
    chat_id = update.effective_user.id 
    name = context.user_data.get("name", "Noma'lum") 
    surname = context.user_data.get("surname", "Noma'lum") 
    users_data[chat_id] = { 
        "name": name, 
        "surname": surname, 
        "phone": phone, 
        "progress": {"html": 0, "css": 0} 
    } 
    logger.info(f"Foydalanuvchi qo'shildi: {users_data[chat_id]}") 
 
    admin_message = f"🆕 *Yangi foydalanuvchi ro'yxatdan o'tdi:*\n👤 *Ism:* {name}\n👤 *Familiya:* {surname}\n📞 *Telefon:* {phone}" 
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message, parse_mode="Markdown") 
    await update.message.reply_text("✅ Siz muvaffaqiyatli ro'yxatdan o'tdingiz!") 
    awaitshow_lesson_options(update) 
    return ConversationHandler.END 
 
# === DARSLARNI TANLASH === 
async def show_lesson_options(update: Update): 
    buttons = [ 
        [InlineKeyboardButton("HTML", callback_data='html')], 
        [InlineKeyboardButton("CSS", callback_data='css')] 
    ] 
    await update.message.reply_text("Qaysi bo'limni o'rganishni boshlamoqchisiz?", reply_markup=InlineKeyboardMarkup(buttons)) 
 
async def offer_lessons(update, progress): 
    html_next = progress["html"] + 1 
    css_next = progress["css"] + 1 
 
    buttons = [] 
    if html_next <= len(LESSONS["html"]): 
        buttons.append([InlineKeyboardButton(f"HTML {html_next}-darsni davom ettirish", callback_data=f"html_lesson_{html_next}")]) 
    if css_next <= len(LESSONS["css"]): 
        buttons.append([InlineKeyboardButton(f"CSS {css_next}-darsni davom ettirish", callback_data=f"css_lesson_{css_next}")]) 
 
    if buttons: 
        await update.message.reply_text("Quyidagi darslardan davom eting:", reply_markup=InlineKeyboardMarkup(buttons)) 
    else: 
        await update.message.reply_text("Siz barcha darslarni tugatgansiz!") 

async def lesson_click(update: Update, context):
    query = update.callback_query
    await query.answer()

    category, lesson_id = query.data.split('_lesson_')
    lesson_index = int(lesson_id) - 1
    lessons = LESSONS.get(category, [])

    if 0 <= lesson_index < len(lessons):
        text = lessons[lesson_index]
        users_data[update.effective_user.id]["progress"][category] = lesson_index + 1

        # Savol yoki test qo'shish
        if lesson_index == len(lessons) - 1:  # Dars tugagach savol qo'shish
            text += "\n\n💡 Endi ushbu dars bo'yicha savolni javob bering!"
        
        buttons = []
        if lesson_index + 1 < len(lessons):
            buttons.append(InlineKeyboardButton("➡️ Keyingi dars", callback_data=f"{category}_lesson_{lesson_index + 2}"))

        await query.message.reply_text(
            f"📚 *{category.upper()} darsining {lesson_id}-qismi:*\n\n{text}",
            reply_markup=InlineKeyboardMarkup([buttons]) if buttons else None,
            parse_mode="Markdown"
        )
    else:
        await query.message.reply_text("❌ Ushbu dars mavjud emas!")

 
# === MAIN FUNKSIYA === 
def main(): 
    app = ApplicationBuilder().token(TOKEN).build() 
 
    registration_handler = ConversationHandler( 
        entry_points=[CommandHandler("start", start)], 
        states={ 
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)], 
            ASK_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_surname)], 
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)], 
        }, 
        fallbacks=[] 
    ) 
 
    app.add_handler(registration_handler) 
    app.add_handler(CallbackQueryHandler(show_lesson_options, pattern='^(html|css)$')) 
    app.add_handler(CallbackQueryHandler(lesson_click, pattern='^(html_lesson_|css_lesson_)')) 
 
    app.run_polling() 
if __name__ == '__main__':
    main()
from flask import Flask, request
import telebot

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        json_str = request.get_data().decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        # Xatolikni konsolga yozish va foydalanuvchiga xabar yuborish
        logger.error(f"Error processing webhook: {e}")
        return "Error", 500

