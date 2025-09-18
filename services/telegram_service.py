import os
from typing import List
from telegram import Bot
from telegram.error import TelegramError
from models import Portfolio, Position


class TelegramService:
    def __init__(self, token: str, chat_id: str, portfolio: Portfolio):
        """
        Initialize Telegram service.

        Args:
            token: Bot token from @BotFather
            chat_id: Chat ID (can be group chat ID)
        """
        self.bot = Bot(token=token)
        self.chat_id = chat_id
        self.portfolio = portfolio

    async def send_message(self, message: str) -> bool:
        """
        Send a message to the configured chat.

        Args:
            message: Message text to send

        Returns:
            bool: True if message was sent successfully
        """
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            return True
        except TelegramError as e:
            print(f"Failed to send Telegram message: {e}")
            return False

    async def send_order_sync_notification(self, positions_created: List[Position], positions_deleted: List[Position]) -> bool:
        """
        Send notification about order synchronization changes.

        Args:
            positions_created: List of orders that were created
            positions_deleted: List of orders that were deleted

        Returns:
            bool: True if message was sent successfully
        """
        if not positions_created and not positions_deleted:
            message = "[INFO] Portfolio sync completed - No changes detected"
        else:
            message = f"[{self.portfolio.display_name} SYNC UPDATE]\n\n"

            if positions_created:
                message += f"[+] Opened {len(positions_created)} orders:\n"
                for order in positions_created:
                    message += f"  - {order.display_name}: {order.amount}% (x{order.leverage})\n"
                message += "\n"

            if positions_deleted:
                message += f"[-] Closed {len(positions_deleted)} orders:\n"
                for order in positions_deleted:
                    message += f"  - {order.display_name}: {order.amount}% (x{order.leverage})\n"
                message += "\n"

            message += f"Total changes: {len(positions_created)} added, {len(positions_deleted)} removed"

        return await self.send_message(message)

    @classmethod
    def from_env(cls) -> 'TelegramService':
        """
        Create TelegramService instance from environment variables.
        Expects TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.
        """
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        if not chat_id:
            raise ValueError("TELEGRAM_CHAT_ID environment variable is required")

        return cls(token=token, chat_id=chat_id)