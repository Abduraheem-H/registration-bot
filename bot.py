import os
import re
import logging
import openpyxl
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "summer_skills_tutors.xlsx")
PORTFOLIO_FOLDER = os.path.join(BASE_DIR, "portfolios")

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
    logger.info("📄 Checking for Excel file at: %s", EXCEL_FILE)
    if not os.path.exists(EXCEL_FILE):
        logger.info("🆕 Creating new Excel file...")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(HEADERS)
        wb.save(EXCEL_FILE)
    else:
        logger.info("✅ Excel file already exists.")


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
        "/start - Begin registration\n"
        "/restart - Restart registration\n"
        "/quit - Cancel registration\n"
        "/help - Show this help message"
    )


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("✍️ What's your Full Name?")
    return NAME


async def restart_registration(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data.clear()
    message = "🔁 Restarting registration. Please enter your Full Name:"
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(message)
    else:
        await update.message.reply_text(message)
    return NAME


async def quit_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    message = "❌ Registration cancelled."
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(message)
    else:
        await update.message.reply_text(message)
    return ConversationHandler.END


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["Full Name"] = update.message.text.strip()
    await update.message.reply_text("📲 Your Phone Number (e.g., 0912345678):")
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
        ]
    ]
    await update.message.reply_text(
        "⚧️ Select Gender:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    context.user_data["Gender"] = update.callback_query.data
    await update.callback_query.edit_message_text("📅 Date of Birth (dd/mm/yyyy):")
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
        ]
    ]
    await update.message.reply_text(
        "🎓 Profession:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PROFESSION


async def profession(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    context.user_data["Profession"] = update.callback_query.data
    if update.callback_query.data == "Student":
        await update.callback_query.edit_message_text("📘 Year of Study:")
        return YEAR
    context.user_data["Year of Study"] = "-"
    await update.callback_query.edit_message_text("📍 Residence Area:")
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
    await update.callback_query.answer()
    context.user_data["Tutoring Experience"] = update.callback_query.data
    summary = "\n".join(f"{k}: {v}" for k, v in context.user_data.items())
    keyboard = [
        [
            InlineKeyboardButton("✅ Submit", callback_data="submit"),
            InlineKeyboardButton("🔁 Restart", callback_data="restart"),
        ]
    ]
    await update.callback_query.edit_message_text(
        f"✔️ Review:\n\n{summary}", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    if update.callback_query.data == "submit":
        try:
            logger.info("📥 Saving user data: %s", context.user_data)
            wb = openpyxl.load_workbook(EXCEL_FILE)
            ws = wb.active
            ws.append([context.user_data.get(h, "") for h in HEADERS])
            wb.save(EXCEL_FILE)
            logger.info("✅ Excel updated successfully.")
        except Exception as e:
            logger.error("❌ Failed to write to Excel: %s", e)
        await update.callback_query.edit_message_text(
            "✅ Thank you! Registration submitted."
        )
        return ConversationHandler.END
    return await restart_registration(update, context)


# --- Polling-based main function (no Flask) ---

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("BOT_TOKEN environment variable not set.")
    exit(1)

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


def main():
    initialize_excel()
    application.run_polling()


if __name__ == "__main__":
    main()
