# src/execution/telegram_bot.py

import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from execution.telegram_wallet_manager import WalletManager
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from utils.logger import get_logger

logger = get_logger(__name__)

class TelegramBot:
    def __init__(self):
        if not TELEGRAM_BOT_TOKEN:
            logger.error("Telegram token missing.")
            self.application = None
            return
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
        self.wallet_manager = WalletManager(self)

    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("help", self.help_command))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_html(rf"Hi {user.mention_html()}! Bot online. Use /help.")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ Status: Online | Mode: Paper")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("/start /status /help")

    async def run(self):
        if not self.application:
            return
        logger.info("[TelegramBot] Running...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        while True:
            await asyncio.sleep(3600)

    async def send_alert(self, message: str):
        if not self.application:
            return
        try:
            await self.application.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"[TelegramBot] send_alert error: {e}")
