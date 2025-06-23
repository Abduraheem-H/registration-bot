import os
import re
import logging
import openpyxl
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# === Logging Setup ===
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# === States ===
(
    NAME,
    PHONE,
    GENDER,
    DOB,
    PROFESSION,
    YEAR,
    RESIDENCE,
    LOCATIONS,
    FIELD,
    SKILLS,
    LANGUAGES,
    PORTFOLIO,
    EXPERIENCE,
    CONFIRM,
) = range(14)

# === File & Folder Setup ===
EXCEL_FILE = "summer_skills_tutors.xlsx"
PORTFOLIO_FOLDER = "portfolios"
os.makedirs(PORTFOLIO_FOLDER, exist_ok=True)

HEADERS = [
    "Full Name",
    "Phone Number",
    "Gender",
    "Date of Birth",
    "Profession",
    "Year of Study",
    "Residence Area",
    "Preferred Areas",
    "Field of Study",
    "Skills",
    "Languages",
    "Portfolio",
    "Tutoring Experience",
]


def initialize_excel():
    if not os.path.exists(EXCEL_FILE):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(HEADERS)
        wb.save(EXCEL_FILE)


# === Handler Functions ===


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("Start Registration ✅", callback_data="start_reg")],
        [InlineKeyboardButton("Help ℹ️", callback_data="help")],
    ]
    await update.message.reply_text(
        "👋 Welcome to Summer Tutor Registration!",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Available commands:\n"
        "/start - Begin registration\n"
        "/restart - Restart registration\n"
        "/quit - Cancel registration\n"
        "/help - Show this help message"
    )


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✍️ What's your Full Name?")
    return NAME


async def restart_registration(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data.clear()
    message = "🔁 Restarting registration. Please enter your Full Name:"
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(message)
    else:
        await update.message.reply_text(message)
    return NAME


async def quit_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    message = "❌ Registration cancelled."
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(message)
    else:
        await update.message.reply_text(message)
    return ConversationHandler.END


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["Full Name"] = update.message.text.strip()
    await update.message.reply_text("📞 Your Phone Number (e.g., 0912345678):")
    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.text.strip()
    if not re.match(r"^09\d{8}$", phone):
        await update.message.reply_text("❌ Invalid. Please enter again:")
        return PHONE
    context.user_data["Phone Number"] = phone
    keyboard = [
        [
            InlineKeyboardButton("Male", callback_data="Male"),
            InlineKeyboardButton("Female", callback_data="Female"),
        ],
    ]
    await update.message.reply_text(
        "⚧️ Select Gender:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    context.user_data["Gender"] = q.data
    await q.edit_message_text("📅 Date of Birth (dd/mm/yyyy):")
    return DOB


async def dob(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    try:
        datetime.strptime(text, "%d/%m/%Y")
    except ValueError:
        await update.message.reply_text("❌ Invalid. Use dd/mm/yyyy:")
        return DOB
    context.user_data["Date of Birth"] = text
    keyboard = [
        [
            InlineKeyboardButton("Graduate", callback_data="Graduate"),
            InlineKeyboardButton("Student", callback_data="Student"),
        ],
    ]
    await update.message.reply_text(
        "🎓 Profession:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PROFESSION


async def profession(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    context.user_data["Profession"] = q.data
    if q.data == "Student":
        await q.edit_message_text("📘 Year of Study:")
        return YEAR
    context.user_data["Year of Study"] = "-"
    await q.edit_message_text("📍 Residence Area:")
    return RESIDENCE


async def year(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["Year of Study"] = update.message.text.strip()
    await update.message.reply_text("📍 Residence Area:")
    return RESIDENCE


async def residence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["Residence Area"] = update.message.text.strip()
    await update.message.reply_text("📌 Preferred tutoring areas:")
    return LOCATIONS


async def locations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["Preferred Areas"] = update.message.text.strip()
    await update.message.reply_text("📚 Field of Study:")
    return FIELD


async def field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["Field of Study"] = update.message.text.strip()
    await update.message.reply_text("🎯 Skills you teach:")
    return SKILLS


async def skills(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["Skills"] = update.message.text.strip()
    await update.message.reply_text("🌍 Other languages you speak:")
    return LANGUAGES


async def languages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["Languages"] = update.message.text.strip()
    await update.message.reply_text(
        "📁 Upload portfolio (file or link) or type 'None':"
    )
    return PORTFOLIO


async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = update.message
    if msg.document or msg.photo:
        file = msg.document or msg.photo[-1]
        file_obj = await context.bot.get_file(file.file_id)
        name = context.user_data["Full Name"].replace(" ", "_")
        ext = ".jpg" if msg.photo else os.path.splitext(file.file_name)[1]
        filename = f"{name}_{file.file_unique_id}{ext}"
        path = os.path.join(PORTFOLIO_FOLDER, filename)
        await file_obj.download_to_drive(path)
        context.user_data["Portfolio"] = path
    else:
        context.user_data["Portfolio"] = msg.text.strip()
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="Yes"),
            InlineKeyboardButton("No", callback_data="No"),
        ]
    ]
    await update.message.reply_text(
        "🧑‍🏫 Tutored before?", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return EXPERIENCE


async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    context.user_data["Tutoring Experience"] = q.data
    summary = "\n".join(f"{k}: {v}" for k, v in context.user_data.items())
    keyboard = [
        [
            InlineKeyboardButton("✅ Submit", callback_data="submit"),
            InlineKeyboardButton("🔁 Restart", callback_data="restart"),
        ]
    ]
    await q.edit_message_text(
        f"✔️ Review:\n\n{summary}", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    if q.data == "submit":
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        ws.append([context.user_data.get(h, "") for h in HEADERS])
        wb.save(EXCEL_FILE)
        await q.edit_message_text("✅ Thank you! Registration submitted.")
        return ConversationHandler.END
    return await restart_registration(update, context)


# === Main Function ===


import asyncio


# Use your actual bot token here

TOKEN = TOKEN = os.getenv("BOT_TOKEN")


# === Webhook Config ===
WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_PORT = int(os.environ.get("PORT", 10000))  # Render sets this automatically
WEBHOOK_URL = f"https://registration-bot-xhth.onrender.com/{TOKEN}"


import asyncio


def main():
    initialize_excel()

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(start_registration, pattern="^start_reg$"),
            CallbackQueryHandler(restart_registration, pattern="^restart$"),
            CallbackQueryHandler(quit_registration, pattern="^quit$"),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            GENDER: [CallbackQueryHandler(gender)],
            DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, dob)],
            PROFESSION: [CallbackQueryHandler(profession)],
            YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, year)],
            RESIDENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, residence)],
            LOCATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, locations)],
            FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, field)],
            SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, skills)],
            LANGUAGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, languages)],
            PORTFOLIO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, portfolio),
                MessageHandler(filters.Document.ALL | filters.PHOTO, portfolio),
            ],
            EXPERIENCE: [CallbackQueryHandler(experience)],
            CONFIRM: [CallbackQueryHandler(confirm)],
        },
        fallbacks=[
            CommandHandler("restart", restart_registration),
            CommandHandler("quit", quit_registration),
            CommandHandler("help", help_command),
        ],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    async def run():
        await application.bot.set_webhook(WEBHOOK_URL)
        print(f"🌐 Webhook set to: {WEBHOOK_URL}")

        await application.start()
        await application.updater.start_webhook(
            listen="0.0.0.0",
            port=WEBHOOK_PORT,
            url_path=TOKEN,
            webhook_url=WEBHOOK_URL,
        )

        print("🚀 Bot is now running via webhook on Render.")
        await application.updater.idle()

    asyncio.run(run())


if __name__ == "__main__":
    main()
