import os
import logging
from dotenv import load_dotenv

load_dotenv()

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from orchestrator import Orchestrator

# --- לוגים בסיסיים ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ⚠️ שער הרשאה — בלעדיו כל אחד בעולם יוכל להשתמש בבוט ולצרוך את מכסת ה-API שלך.
AUTHORIZED_CHAT_ID = int(os.getenv("TELEGRAM_AUTHORIZED_CHAT_ID", "0"))

# יוצר את ה-orchestrator פעם אחת, כשה-process עולה — לא בכל הודעה מחדש
orch = Orchestrator()

# state פשוט בזיכרון: איזה task_type פעיל לכל chat_id כרגע
active_task = {}


def is_authorized(update: Update) -> bool:
    """שער הרשאה — בודק שההודעה מגיעה מה-chat_id המורשה בלבד."""
    return update.effective_chat.id == AUTHORIZED_CHAT_ID


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        "🤖 RepoRadar Bot\n\n"
        "פקודות:\n"
        "/review — ביקורת קוד כללית\n"
        "/architecture — ביקורת ארכיטקטורה\n"
        "/debug — אבחון שגיאה (קוד --- שגיאה, בהודעה אחת)\n\n"
        "אחרי שתבחר מצב, שלח לי קוד בהודעת טקסט רגילה."
    )


async def set_mode(update: Update, ctx: ContextTypes.DEFAULT_TYPE, mode: str):
    if not is_authorized(update):
        return
    active_task[update.effective_chat.id] = mode
    await update.message.reply_text(f"✅ מצב פעיל: {mode}. שלח לי קוד.")


async def cmd_review(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await set_mode(update, ctx, "review")


async def cmd_architecture(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await set_mode(update, ctx, "architecture")


async def cmd_debug(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await set_mode(update, ctx, "debug")


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    mode = active_task.get(chat_id)
    if mode is None:
        await update.message.reply_text("קודם תבחר מצב: /review /architecture /debug")
        return

    await update.message.reply_text("⏳ מריץ...")

    try:
        if mode == "debug":
            if "---" not in text:
                await update.message.reply_text(
                    "למצב debug: שלח קוד ואז --- ואז את השגיאה, הכל בהודעה אחת."
                )
                return
            code_part, error_part = text.split("---", 1)
            result = orch.route("debug", {"code": code_part.strip(), "error": error_part.strip()})
        else:
            result = orch.route(mode, {"code": text})

        await update.message.reply_text(result)

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await update.message.reply_text(f"❌ שגיאה: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("review", cmd_review))
    app.add_handler(CommandHandler("architecture", cmd_architecture))
    app.add_handler(CommandHandler("debug", cmd_debug))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("RepoRadar bot is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()