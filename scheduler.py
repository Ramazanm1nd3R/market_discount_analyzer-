# scheduler.py – Планировщик рассылок скидок пользователям
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz
import logging
from db import (
    connect_db,
    get_subscriptions_for_notifications,
    get_unseen_discounts,
    mark_discounts_as_sent,
    update_parsed_discounts
)
from service_parsers.lamoda_discount_parser import parse_lamoda_discounts
from service_parsers.magnum_discount_parser import parse_magnum_discounts
from telegram import Bot
import os

# Загрузка токена для отправки уведомлений
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

# Часовой пояс Алматы (UTC+6)
almaty_timezone = pytz.timezone('Asia/Almaty')

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# URL для парсинга
MAGNUM_URL = "https://magnum.kz/catalog?discountType=all&city=almaty"
LAMODA_URLS = {
    "women": "https://www.lamoda.kz/c/4153/default-women/?is_sale=1",
    "men": "https://www.lamoda.kz/c/4152/default-men/?is_sale=1",
    "kids": "https://www.lamoda.kz/c/4154/default-kids/?is_sale=1"
}

# ======= 🚀 Функции парсинга ======= #
async def parse_and_update_discounts(pool):
    """Парсинг скидок и обновление базы."""
    try:
        logger.info("Начинается плановый парсинг скидок...")
        
        # 1️⃣ Парсинг Lamoda
        for category_name, url in LAMODA_URLS.items():
            lamoda_discounts = parse_lamoda_discounts(url)
            if lamoda_discounts:
                await update_parsed_discounts(pool, "Lamoda", lamoda_discounts)
                logger.info(f"✅ Обновлены скидки для Lamoda ({category_name})")

        # 2️⃣ Парсинг Magnum
        magnum_discounts = parse_magnum_discounts(MAGNUM_URL)
        if magnum_discounts:
            await update_parsed_discounts(pool, "Magnum", magnum_discounts)
            logger.info("✅ Обновлены скидки для Magnum")

        logger.info("✅ Парсинг скидок завершен.")
    except Exception as e:
        logger.error(f"Ошибка при плановом парсинге: {e}")

# ======= 📩 Функции рассылки ======= #
async def send_discount_notifications(pool):
    """Отправка уведомлений пользователям согласно их подпискам."""
    try:
        now = datetime.now(almaty_timezone).strftime("%H:%M")
        logger.info(f"🔔 Начинается рассылка уведомлений для времени {now}")

        subscriptions = await get_subscriptions_for_notifications(pool, now)
        if not subscriptions:
            logger.info("❎ Подписок для текущего времени нет.")
            return

        for sub in subscriptions:
            user_id = sub['user_id']
            service_name = sub['service_name']
            service_id = sub['service_id']

            discounts = await get_unseen_discounts(pool, user_id, service_id)
            if not discounts:
                await bot.send_message(
                    chat_id=user_id,
                    text=f"📭 Сегодня нет новых скидок по сервису {service_name}."
                )
                continue

            # Формируем текст скидок
            message = f"🔥 Новые скидки на {service_name}:\n\n"
            discount_ids = []
            for d in discounts:
                message += (
                    f"🛍️ {d['product_name']}\n"
                    f"💰 Цена: {d['price_new']} (Старая: {d['price_old']})\n"
                    f"📉 Скидка: {d['discount_percent']}%\n"
                    f"------------------------\n"
                )
                discount_ids.append(d['discount_id'])

            await bot.send_message(chat_id=user_id, text=message)

            # Отмечаем отправленные скидки
            await mark_discounts_as_sent(pool, user_id, service_id, discount_ids)
            logger.info(f"✅ Отправлены скидки пользователю {user_id} для сервиса {service_name}")

    except Exception as e:
        logger.error(f"Ошибка при рассылке уведомлений: {e}")

# ======= 🕒 Инициализация планировщика ======= #
async def start_scheduler():
    """Инициализация и запуск планировщика APScheduler."""
    pool = await connect_db()

    scheduler = AsyncIOScheduler()

    # 🟡 Плановый парсинг скидок – каждые сутки в 01:00
    scheduler.add_job(
        parse_and_update_discounts,
        'cron',
        hour=1,
        minute=0,
        timezone=almaty_timezone,
        args=[pool],
        id="daily_parsing"
    )

    # 🔔 Проверка подписок – каждую минуту (для отправки в заданное пользователем время)
    scheduler.add_job(
        send_discount_notifications,
        'cron',
        minute="*",
        timezone=almaty_timezone,
        args=[pool],
        id="notifications"
    )

    logger.info("📅 Планировщик заданий запущен.")
    scheduler.start()

    try:
        # Запускаем бесконечный цикл для работы планировщика
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("⛔ Планировщик остановлен.")
        scheduler.shutdown()

# ======= 🚀 Запуск ======= #
if __name__ == "__main__":
    asyncio.run(start_scheduler())
