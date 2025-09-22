import sys
import asyncio
import os
from dotenv import load_dotenv

from database import Portfolio
from scrapers.etoro import scrape_public_positions
from services.order_service import OrderService
from services.telegram_service import TelegramService

load_dotenv()

async def main():
    try:
        if len(sys.argv) > 1:
            display_name = sys.argv[1]
        elif os.getenv('ETORO_USERNAME'):
            display_name = os.getenv('ETORO_USERNAME')
        else:
            display_name = input("Enter eToro portfolio URL: ").strip()

        portfolio, created = Portfolio.get_or_create(display_name=display_name)
        telegram_bot = TelegramService(os.getenv('TELEGRAM_BOT_TOKEN'), os.getenv('TELEGRAM_CHAT_ID'), portfolio=portfolio)
        orders = scrape_public_positions(portfolio)
        orders_opened, orders_closed = OrderService.sync_orders(orders, portfolio)

        await telegram_bot.send_order_sync_notification(orders_opened, orders_closed)
        print(f"\nSync completed: {len(orders_opened)} created, {len(orders_closed)} deleted")
    except Exception as e:
        error_type = type(e).__name__
        error_message = f"❌ eToro Scraper Error ({error_type}): {str(e)}"
        print(f"Error occurred: {error_message}")

        try:
            await telegram_bot.send_message(error_message)
            print("Error notification sent to Telegram")
        except Exception as telegram_error:
            print(f"Failed to send Telegram notification: {telegram_error}")

        print("Exiting due to scraper error...")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())