import os
import re
import logging
import openpyxl
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
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


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


(
    NAME,
    PHONE,
    GENDER,
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
    CUSTOM_SKILL,
) = range(14)


SKILL_OPTIONS = [
    "Coding (Programming)",
    "Languages",
    "Graphics Design and Video Editing",
    "Art (Drawing)",
    "Crochet",
    "AutoCAD",
    "Animation and 3D Designing",
    "Essay Writing and College Prep",
    "Other",
]


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "summer_skills_tutors.xlsx")
PORTFOLIO_FOLDER = os.path.join(BASE_DIR, "portfolios")
os.makedirs(PORTFOLIO_FOLDER, exist_ok=True)


HEADERS = [
    "Full Name",
    "Phone Number",
    "Gender",
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


def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[["✅ Start Registration"], ["ℹ️ Help", "🔁 Restart", "❌ Quit"]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def initialize_excel():
    if not os.path.exists(EXCEL_FILE):
        logger.info("🆕 Creating new Excel file...")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(HEADERS)
        wb.save(EXCEL_FILE)
    else:
        logger.info("✅ Excel file already exists.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["in_conversation"] = False
    await update.message.reply_text(
        "👋 Welcome to Summer Tutor Registration!\n\nPlease choose an option below:",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 Help Guide:\n\n"
        "✅ Start Registration - Begin the registration process\n"
        "🔁 Restart - Restart your current registration\n"
        "❌ Quit - Cancel your current registration\n\n"
        "You can use these commands anytime:\n"
        "/start - Begin registration\n"
        "/restart - Restart registration\n"
        "/quit - Cancel registration\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text, reply_markup=main_menu_keyboard())

    if context.user_data.get("in_conversation", False):
        return context.user_data.get("current_state", ConversationHandler.END)
    return ConversationHandler.END


async def handle_restart_outside_conversation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if context.user_data.get("in_conversation", False):

        return await restart_registration(update, context)
    else:

        await update.message.reply_text(
            "ℹ️ You haven't started registration yet. Please use '✅ Start Registration' to begin.",
            reply_markup=main_menu_keyboard(),
        )
        return ConversationHandler.END


async def restart_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function is specifically for when the restart button is clicked during a conversation
    return await restart_registration(update, context)


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    context.user_data["in_conversation"] = True
    context.user_data["current_state"] = NAME
    await update.message.reply_text("✍️ What's your Full Name?")
    return NAME


async def restart_registration(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data.clear()
    context.user_data["in_conversation"] = True
    context.user_data["current_state"] = NAME
    await update.message.reply_text(
        "🔁 Registration restarted. Please enter your Full Name:"
    )
    return NAME


async def quit_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    context.user_data["in_conversation"] = False
    await update.message.reply_text(
        "❌ Registration cancelled.", reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text in ["🔁 Restart", "❌ Quit", "ℹ️ Help"]:
        return await unknown_in_conversation_fallback(update, context)

    context.user_data["current_state"] = NAME
    context.user_data["Full Name"] = update.message.text.strip()
    await update.message.reply_text("📲 Your Phone Number (e.g., 0912345678):")
    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text in ["🔁 Restart", "❌ Quit", "ℹ️ Help"]:
        return await unknown_in_conversation_fallback(update, context)

    phone = update.message.text.strip()
    if not re.match(r"^09\d{8}$", phone):
        await update.message.reply_text("❌ Invalid. Please enter again:")
        return PHONE

    context.user_data["current_state"] = PHONE
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
    context.user_data["current_state"] = GENDER
    context.user_data["Gender"] = update.callback_query.data

    keyboard = [
        [
            InlineKeyboardButton("Graduate", callback_data="Graduate"),
            InlineKeyboardButton("Student", callback_data="Student"),
        ]
    ]
    await update.callback_query.edit_message_text(
        "🎓 Profession:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PROFESSION


async def profession(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    context.user_data["current_state"] = PROFESSION
    context.user_data["Profession"] = update.callback_query.data
    if update.callback_query.data == "Student":
        await update.callback_query.edit_message_text("📘 Year of Study:")
        return YEAR
    context.user_data["Year of Study"] = "-"
    await update.callback_query.edit_message_text(
        "📍 What is your current residential area or neighborhood?"
    )
    return RESIDENCE


async def year(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text in ["🔁 Restart", "❌ Quit", "ℹ️ Help"]:
        return await unknown_in_conversation_fallback(update, context)

    context.user_data["current_state"] = YEAR
    context.user_data["Year of Study"] = update.message.text.strip()
    await update.message.reply_text(
        "📍 What is your current residential area or neighborhood?"
    )
    return RESIDENCE


async def residence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text in ["🔁 Restart", "❌ Quit", "ℹ️ Help"]:
        return await unknown_in_conversation_fallback(update, context)

    context.user_data["current_state"] = RESIDENCE
    context.user_data["Residence Area"] = update.message.text.strip()
    await update.message.reply_text("📌 What are your preferred areas for tutoring?")
    return LOCATIONS


async def locations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text in ["🔁 Restart", "❌ Quit", "ℹ️ Help"]:
        return await unknown_in_conversation_fallback(update, context)

    context.user_data["current_state"] = LOCATIONS
    context.user_data["Preferred Areas"] = update.message.text.strip()
    await update.message.reply_text("📚 What is your field of study?")
    return FIELD


async def field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text in ["🔁 Restart", "❌ Quit", "ℹ️ Help"]:
        return await unknown_in_conversation_fallback(update, context)

    context.user_data["current_state"] = FIELD
    context.user_data["Field of Study"] = update.message.text.strip()
    context.user_data["Skills"] = set()
    keyboard = [
        [InlineKeyboardButton(option, callback_data=option)] for option in SKILL_OPTIONS
    ]
    keyboard.append([InlineKeyboardButton("✅ Done", callback_data="done")])
    await update.message.reply_text(
        "🎯 Select skills you can teach (tap to toggle):",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return SKILLS


async def select_skills(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    selected = context.user_data.get("Skills", set())

    data = query.data
    if data == "done":
        context.user_data["Skills"] = ", ".join(selected)
        await query.edit_message_text("🌍 What other languages do you speak?")
        return LANGUAGES
    elif data == "Other":
        await query.edit_message_text("✍️ Please type your custom skill:")
        return CUSTOM_SKILL

    if data in selected:
        selected.remove(data)
    else:
        selected.add(data)
    context.user_data["Skills"] = selected

    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅ ' if option in selected else ''}{option}", callback_data=option
            )
        ]
        for option in SKILL_OPTIONS
    ]
    keyboard.append([InlineKeyboardButton("✅ Done", callback_data="done")])

    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
    return SKILLS


async def custom_skill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text in ["🔁 Restart", "❌ Quit", "ℹ️ Help"]:
        return await unknown_in_conversation_fallback(update, context)

    custom_skill_text = update.message.text.strip()
    selected_skills = context.user_data.get("Skills", set())
    selected_skills.add(custom_skill_text)
    context.user_data["Skills"] = selected_skills

    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅ ' if option in selected_skills else ''}{option}",
                callback_data=option,
            )
        ]
        for option in SKILL_OPTIONS
    ]
    keyboard.append([InlineKeyboardButton("✅ Done", callback_data="done")])
    await update.message.reply_text(
        f"'{custom_skill_text}' added. You can add more or tap 'Done'.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return SKILLS


async def languages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text in ["🔁 Restart", "❌ Quit", "ℹ️ Help"]:
        return await unknown_in_conversation_fallback(update, context)

    context.user_data["current_state"] = LANGUAGES
    context.user_data["Languages"] = update.message.text.strip()
    await update.message.reply_text(
        "📁 Please upload your portfolio (file or link), or type 'None' if you don't have one:"
    )
    return PORTFOLIO


async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text in ["🔁 Restart", "❌ Quit", "ℹ️ Help"]:
        return await unknown_in_conversation_fallback(update, context)

    context.user_data["current_state"] = PORTFOLIO
    msg = update.message
    if msg.document or msg.photo:
        file = msg.document or msg.photo[-1]
        file_obj = await context.bot.get_file(file.file_id)
        name_for_file = context.user_data["Full Name"].replace(" ", "_")
        ext = ".jpg" if msg.photo else os.path.splitext(file.file_name)[1]
        filename = f"{name_for_file}_{file.file_unique_id}{ext}"
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
        "🧑‍🏫 Have you had any tutoring experience before?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return EXPERIENCE


async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    context.user_data["current_state"] = EXPERIENCE
    context.user_data["Tutoring Experience"] = update.callback_query.data

    summary = "\n".join(
        f"{emoji} {key}: {value}"
        for emoji, key, value in zip(
            [
                "👤",
                "📱",
                "⚧️",
                "🎓",
                "📘",
                "📍",
                "📌",
                "📚",
                "🎯",
                "🌍",
                "📁",
                "🧑‍🏫",
            ],
            HEADERS,
            [context.user_data.get(h, "-") for h in HEADERS],
        )
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Submit", callback_data="submit"),
            InlineKeyboardButton("🔁 Restart", callback_data="restart"),
        ]
    ]
    await update.callback_query.edit_message_text(
        f"✔️ Please review your details:\n\n{summary}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    if update.callback_query.data == "submit":
        try:
            wb = openpyxl.load_workbook(EXCEL_FILE)
            ws = wb.active
            ws.append([context.user_data.get(h, "") for h in HEADERS])
            wb.save(EXCEL_FILE)
            logger.info("✅ Registration saved to Excel.")
        except Exception as e:
            logger.error("❌ Failed to save registration: %s", e)

        context.user_data["in_conversation"] = False
        await update.callback_query.edit_message_text(
            "✅ Thank you! Your registration has been successfully submitted."
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🏠 Returning to the main menu:",
            reply_markup=main_menu_keyboard(),
        )
        return ConversationHandler.END

    return await restart_registration(update, context)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 I didn't understand that. Please use the buttons or type /help.",
        reply_markup=main_menu_keyboard(),
    )


async def unknown_in_conversation_fallback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text
    if text == "🔁 Restart":
        return await restart_registration(update, context)
    elif text == "❌ Quit":
        return await quit_registration(update, context)
    elif text == "ℹ️ Help":
        await help_command(update, context)
        return context.user_data.get("current_state", NAME)
    else:
        await update.message.reply_text(
            "❌ Please provide the requested information or use the command buttons.",
            reply_markup=main_menu_keyboard(),
        )
        return context.user_data.get("current_state", NAME)


def main():
    initialize_excel()

    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        logger.error("BOT_TOKEN environment variable not set.")
        exit(1)

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.TEXT & filters.Regex("^✅ Start Registration$"),
                start_registration,
            ),
            CommandHandler("start", start),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            GENDER: [CallbackQueryHandler(gender)],
            # DOB state removed from here
            PROFESSION: [CallbackQueryHandler(profession)],
            YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, year)],
            RESIDENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, residence)],
            LOCATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, locations)],
            FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, field)],
            SKILLS: [CallbackQueryHandler(select_skills)],
            CUSTOM_SKILL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, custom_skill)
            ],
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
            MessageHandler(
                filters.TEXT & filters.Regex("^🔁 Restart$"), restart_from_text
            ),
            MessageHandler(
                filters.TEXT & filters.Regex("^❌ Quit$"), quit_registration
            ),
            MessageHandler(filters.TEXT & filters.Regex("^ℹ️ Help$"), help_command),
            MessageHandler(filters.ALL, unknown_in_conversation_fallback),
        ],
        persistent=False,
        name="registration_conversation",
    )

    application.add_handler(conv_handler)

    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^✅ Start Registration$"), start_registration
        )
    )
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^ℹ️ Help$"), help_command)
    )
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^❌ Quit$"), quit_registration)
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🔁 Restart$"),
            handle_restart_outside_conversation,
        )
    )

    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        CommandHandler("restart", handle_restart_outside_conversation)
    )
    application.add_handler(CommandHandler("quit", quit_registration))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    application.run_polling()


if __name__ == "__main__":
    main()
