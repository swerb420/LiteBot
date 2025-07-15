import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
from database.db_manager import db
from utils.logger import get_logger
from ai_analysis.whale_behavior_analyzer import WhaleBehaviorAnalyzer

logger = get_logger(__name__)

WALLET_ADDRESS, WALLET_LABEL, WALLET_CATEGORY, WALLET_TAGS, CONFIRM_ADD = range(5)
EDIT_FIELD, EDIT_VALUE = range(5, 7)


class WalletManager:
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        self.analyzer = WhaleBehaviorAnalyzer()
        self._setup_handlers()

    def _setup_handlers(self):
        self.bot.application.add_handler(
            CommandHandler("wallets", self.list_wallets_command)
        )
        self.bot.application.add_handler(
            CommandHandler("wallet", self.wallet_details_command)
        )
        self.bot.application.add_handler(
            CommandHandler("analyze", self.analyze_wallet_command)
        )
        self.bot.application.add_handler(
            CommandHandler("patterns", self.patterns_command)
        )
        self.bot.application.add_handler(
            CommandHandler("leaderboard", self.leaderboard_command)
        )

        add_wallet_conv = ConversationHandler(
            entry_points=[CommandHandler("add_wallet", self.add_wallet_start)],
            states={
                WALLET_ADDRESS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.add_wallet_address
                    )
                ],
                WALLET_LABEL: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.add_wallet_label
                    )
                ],
                WALLET_CATEGORY: [CallbackQueryHandler(self.add_wallet_category)],
                WALLET_TAGS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.add_wallet_tags
                    )
                ],
                CONFIRM_ADD: [CallbackQueryHandler(self.confirm_add_wallet)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        self.bot.application.add_handler(add_wallet_conv)

        edit_wallet_conv = ConversationHandler(
            entry_points=[CommandHandler("edit_wallet", self.edit_wallet_start)],
            states={
                EDIT_FIELD: [CallbackQueryHandler(self.edit_wallet_field)],
                EDIT_VALUE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.edit_wallet_value
                    )
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        self.bot.application.add_handler(edit_wallet_conv)

        self.bot.application.add_handler(
            CommandHandler("remove_wallet", self.remove_wallet_command)
        )

    async def list_wallets_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        try:
            query = """
                SELECT
                    tw.wallet_address,
                    tw.label,
                    tw.category,
                    tw.tags,
                    tw.tracking_enabled,
                    wp.total_trades,
                    wp.total_pnl,
                    wp.win_rate,
                    tw.last_activity
                FROM tracked_wallets tw
                LEFT JOIN wallet_performance wp ON tw.wallet_address = wp.wallet_address
                    AND wp.period = 'daily'
                ORDER BY wp.total_pnl DESC NULLS LAST
                LIMIT 20
            """
            wallets = await db.fetch(query)
            if not wallets:
                await update.message.reply_text("No wallets tracked. Use /add_wallet")
                return
            message = "Tracked Wallets\n\n"
            for w in wallets:
                status = "🟢" if w["tracking_enabled"] else "🔴"
                pnl_emoji = "📈" if (w["total_pnl"] or 0) > 0 else "📉"
                message += (
                    f"{status} {w['label'] or 'Unnamed'} ({w['category']})\n"
                    f"`{w['wallet_address'][:6]}...{w['wallet_address'][-4:]}`\n"
                )
                if w["total_trades"]:
                    message += (
                        f"{pnl_emoji} PnL: ${w['total_pnl']:,.2f} | "
                        f"Win Rate: {w['win_rate']:.1f}% | "
                        f"Trades: {w['total_trades']}\n"
                    )
                if w["tags"]:
                    message += f"Tags: {', '.join(w['tags'])}\n"
                message += "\n"
            keyboard = [
                [
                    InlineKeyboardButton("Add Wallet", callback_data="add_wallet"),
                    InlineKeyboardButton("Leaderboard", callback_data="leaderboard"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                message, parse_mode="Markdown", reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"[WalletManager] list_wallets error: {e}")
            await update.message.reply_text("Error fetching wallets")

    async def add_wallet_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await update.message.reply_text(
            "Add New Wallet\n\nEnter wallet address (0x...) or /cancel",
            parse_mode="Markdown",
        )
        return WALLET_ADDRESS

    async def add_wallet_address(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        address = update.message.text.strip()
        if not re.match(r"^0x[a-fA-F0-9]{40}$", address):
            await update.message.reply_text("Invalid address. Try again")
            return WALLET_ADDRESS
        existing = await db.fetchrow(
            "SELECT * FROM tracked_wallets WHERE wallet_address=$1", address
        )
        if existing:
            await update.message.reply_text("Wallet already tracked")
            return ConversationHandler.END
        context.user_data["wallet_address"] = address
        await update.message.reply_text("Wallet label?")
        return WALLET_LABEL

    async def add_wallet_label(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        label = update.message.text.strip()[:100]
        context.user_data["wallet_label"] = label
        keyboard = [
            [
                InlineKeyboardButton("Whale", callback_data="category_whale"),
                InlineKeyboardButton("Smart", callback_data="category_smart_money"),
            ],
            [
                InlineKeyboardButton(
                    "Institution", callback_data="category_institution"
                ),
                InlineKeyboardButton("Custom", callback_data="category_custom"),
            ],
        ]
        await update.message.reply_text(
            "Select category", reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return WALLET_CATEGORY

    async def add_wallet_category(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()
        context.user_data["wallet_category"] = query.data.replace("category_", "")
        await query.edit_message_text(
            "Add tags separated by commas or type 'skip'",
        )
        return WALLET_TAGS

    async def add_wallet_tags(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        tags = (
            []
            if text.lower() == "skip"
            else [t.strip() for t in text.split(",") if t.strip()]
        )
        context.user_data["wallet_tags"] = tags
        keyboard = [
            [
                InlineKeyboardButton("Confirm", callback_data="confirm_yes"),
                InlineKeyboardButton("Cancel", callback_data="confirm_no"),
            ]
        ]
        summary = (
            f"Address: `{context.user_data['wallet_address']}`\n"
            f"Label: {context.user_data['wallet_label']}\n"
            f"Category: {context.user_data['wallet_category']}\n"
            f"Tags: {', '.join(tags) if tags else 'None'}\n"
            "Add this wallet?"
        )
        await update.message.reply_text(
            summary, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CONFIRM_ADD

    async def confirm_add_wallet(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()
        if query.data == "confirm_no":
            await query.edit_message_text("Cancelled")
            return ConversationHandler.END
        try:
            await db.execute(
                """
                INSERT INTO tracked_wallets (wallet_address,label,category,tags,added_by)
                VALUES ($1,$2,$3,$4,$5)
                """,
                context.user_data["wallet_address"],
                context.user_data["wallet_label"],
                context.user_data["wallet_category"],
                context.user_data["wallet_tags"],
                str(update.effective_user.id),
            )
            await self.analyzer.start_tracking(context.user_data["wallet_address"])
            await query.edit_message_text("Wallet added")
        except Exception as e:
            logger.error(f"[WalletManager] add wallet error: {e}")
            await query.edit_message_text("Error adding wallet")
        return ConversationHandler.END

    async def wallet_details_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        if not context.args:
            await update.message.reply_text("Usage: /wallet <address or label>")
            return
        search_term = context.args[0]
        wallet = await db.fetchrow(
            """SELECT * FROM tracked_wallets WHERE wallet_address ILIKE $1||'%' OR label ILIKE $1||'%' LIMIT 1""",
            search_term,
        )
        if not wallet:
            await update.message.reply_text("Wallet not found")
            return
        await update.message.reply_text("Analyzing wallet...")
        analysis = await self.analyzer.deep_analysis(wallet["wallet_address"])
        message = f"Wallet Analysis: {wallet['label']}\nTotal PnL: ${analysis['performance'].get('total_pnl',0):,.2f}"
        await update.message.reply_text(message)

    async def analyze_wallet_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        if not context.args:
            await update.message.reply_text("Usage: /analyze <wallet>")
            return
        search_term = context.args[0]
        wallet = await db.fetchrow(
            "SELECT * FROM tracked_wallets WHERE wallet_address ILIKE $1||'%' OR label ILIKE $1||'%' LIMIT 1",
            search_term,
        )
        if not wallet:
            await update.message.reply_text("Wallet not found")
            return
        await update.message.reply_text("Running AI analysis...")
        analysis = await self.analyzer.comprehensive_ai_analysis(
            wallet["wallet_address"]
        )
        if analysis.get("error"):
            await update.message.reply_text(analysis["error"])
            return
        await update.message.reply_text(
            f"Primary strategy: {analysis['behavior']['primary_strategy']}"
        )

    async def patterns_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = """
            SELECT wp.pattern_name, wp.description,
                   COUNT(DISTINCT wpa.wallet_address) as whale_count,
                   AVG(wpa.confidence) as avg_confidence
            FROM whale_patterns wp
            LEFT JOIN wallet_patterns wpa ON wp.id = wpa.pattern_id
            GROUP BY wp.pattern_name, wp.description
            ORDER BY whale_count DESC
        """
        patterns = await db.fetch(query)
        message = "Whale Trading Patterns\n\n"
        for p in patterns:
            message += f"{p['pattern_name']} - found in {p['whale_count']} whales\n"
        await update.message.reply_text(message)

    async def leaderboard_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        period = context.args[0] if context.args else "daily"
        if period not in ["daily", "weekly", "monthly", "all_time"]:
            period = "daily"
        query = """
            SELECT tw.wallet_address, tw.label, tw.category,
                   wp.total_pnl, wp.total_trades, wp.win_rate,
                   wp.profit_factor, wp.total_volume
            FROM tracked_wallets tw
            JOIN wallet_performance wp ON tw.wallet_address = wp.wallet_address
            WHERE wp.period=$1 AND tw.tracking_enabled=true
            ORDER BY wp.total_pnl DESC
            LIMIT 10
        """
        leaderboard = await db.fetch(query, period)
        message = f"Whale Leaderboard ({period})\n\n"
        for i, whale in enumerate(leaderboard):
            message += f"{i+1}. {whale['label']} PnL ${whale['total_pnl']:,.2f}\n"
        await update.message.reply_text(message)

    async def remove_wallet_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        if not context.args:
            await update.message.reply_text("Usage: /remove_wallet <address or label>")
            return
        search_term = context.args[0]
        result = await db.fetchrow(
            """DELETE FROM tracked_wallets WHERE wallet_address ILIKE $1||'%' OR label ILIKE $1||'%' RETURNING wallet_address,label""",
            search_term,
        )
        if result:
            await update.message.reply_text(f"Removed {result['label']}")
        else:
            await update.message.reply_text("Wallet not found")

    async def edit_wallet_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        if not context.args:
            await update.message.reply_text("Usage: /edit_wallet <address or label>")
            return ConversationHandler.END
        search_term = context.args[0]
        wallet = await db.fetchrow(
            "SELECT * FROM tracked_wallets WHERE wallet_address ILIKE $1||'%' OR label ILIKE $1||'%' LIMIT 1",
            search_term,
        )
        if not wallet:
            await update.message.reply_text("Wallet not found")
            return ConversationHandler.END
        context.user_data["edit_wallet"] = wallet["wallet_address"]
        keyboard = [
            [
                InlineKeyboardButton("Label", callback_data="field_label"),
                InlineKeyboardButton("Category", callback_data="field_category"),
            ],
            [
                InlineKeyboardButton("Tags", callback_data="field_tags"),
                InlineKeyboardButton("Min Size", callback_data="field_min_trade_size"),
            ],
        ]
        await update.message.reply_text(
            "Select field to edit", reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return EDIT_FIELD

    async def edit_wallet_field(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()
        field = query.data.replace("field_", "")
        context.user_data["edit_field"] = field
        await query.edit_message_text(f"Enter new value for {field}")
        return EDIT_VALUE

    async def edit_wallet_value(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        value = update.message.text.strip()
        field = context.user_data.get("edit_field")
        wallet = context.user_data.get("edit_wallet")
        if not field or not wallet:
            await update.message.reply_text("Unexpected error")
            return ConversationHandler.END
        try:
            await db.execute(
                f"UPDATE tracked_wallets SET {field}=$1 WHERE wallet_address=$2",
                value,
                wallet,
            )
            await update.message.reply_text("Updated")
        except Exception as e:
            logger.error(f"[WalletManager] edit error: {e}")
            await update.message.reply_text("Error updating wallet")
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Cancelled")
        return ConversationHandler.END
