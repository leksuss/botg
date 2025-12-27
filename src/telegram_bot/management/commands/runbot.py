import asyncio
import logging

from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config.env_settings import env_settings

logger = logging.getLogger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = (
        "Привет! Это шаблон бота. "
        "Команда /ping вернёт pong. "
        "Замените обработчики на свою логику."
    )
    await update.message.reply_text(text)  # type: ignore[union-attr]
    logger.info("Start command from %s", user.id if user else "unknown")


async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("pong")  # type: ignore[union-attr]


class Command(BaseCommand):
    help = "Запускает Telegram-бота (python-telegram-bot v21, asyncio)."

    def handle(self, *args, **options):
        asyncio.run(self.run_bot())

    async def run_bot(self) -> None:
        token = env_settings.TELEGRAM.BOT_TOKEN.get_secret_value()
        application = Application.builder().token(token).build()

        application.add_handler(CommandHandler("start", cmd_start))
        application.add_handler(CommandHandler("ping", cmd_ping))

        logger.info("Starting Telegram bot polling...")
        await application.run_polling(allowed_updates=Update.ALL_TYPES)
