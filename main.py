import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import BOT_TOKEN
from database.db import init_db
from handlers import user, admin
from middlewares.subscription import SubscriptionMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", "")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEB_SERVER_PORT = int(os.getenv("PORT", 8080))


async def on_startup(bot: Bot):
    await init_db()
    logger.info("Ma'lumotlar bazasi tayyor.")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook sozlandi: {WEBHOOK_URL}")


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    logger.info("Webhook o'chirildi.")


async def health_check(request):
    return web.Response(text="OK", status=200)


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN topilmadi!")
    if not WEBHOOK_HOST:
        raise ValueError("RENDER_EXTERNAL_URL topilmadi!")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    dp.include_router(admin.router)
    dp.include_router(user.router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    app.router.add_get("/health", health_check)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    logger.info(f"Server ishga tushdi. Port: {WEB_SERVER_PORT}")
    web.run_app(app, host="0.0.0.0", port=WEB_SERVER_PORT)


if __name__ == "__main__":
    main()
