# db.py – Работа с базой данных PostgreSQL
import logging
import asyncpg
import os
from datetime import datetime

# Данные для подключения к PostgreSQL
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


logger = logging.getLogger(__name__)
# Функция подключения к базе данных
async def connect_db():
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT
    )

# ======= Функции для работы с пользователями ======= #
async def add_user(pool, user_id):
    """Добавить пользователя в базу данных, если его нет."""
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (user_id)
            VALUES ($1)
            ON CONFLICT (user_id) DO NOTHING;
        """, user_id)

async def get_user(pool, user_id):
    """Получить информацию о пользователе."""
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
            SELECT * FROM users WHERE user_id = $1;
        """, user_id)

# ======= Функции для работы с сервисами ======= #
async def get_service_id(pool, service_name):
    """Получить ID сервиса по имени."""
    async with pool.acquire() as conn:
        record = await conn.fetchrow("""
            SELECT service_id FROM services WHERE service_name = $1;
        """, service_name)
        return record['service_id'] if record else None

async def add_service(pool, service_name):
    """Добавить сервис, если его нет."""
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO services (service_name)
            VALUES ($1)
            ON CONFLICT (service_name) DO NOTHING;
        """, service_name)

# ======= Функции для работы с подписками ======= #
async def add_subscription(pool, user_id, service_name, discount_threshold, notification_time):
    """Добавить или обновить подписку пользователя."""
    service_id = await get_service_id(pool, service_name)
    if service_id is None:
        await add_service(pool, service_name)
        service_id = await get_service_id(pool, service_name)

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO subscriptions (user_id, service_id, discount_threshold, notification_time)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id, service_id)
            DO UPDATE SET discount_threshold = $3, notification_time = $4;
        """, user_id, service_id, discount_threshold, notification_time)

async def get_subscriptions_for_notifications(pool, current_time):
    """Получить подписки, для которых нужно отправить уведомления в заданное время."""
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT s.user_id, s.service_id, s.discount_threshold, s.notification_time, sv.service_name
            FROM subscriptions s
            JOIN services sv ON s.service_id = sv.service_id
            WHERE s.notification_time = $1;
        """, current_time)

# ======= Функции для работы со скидками ======= #
async def update_parsed_discounts(pool, service_name, discounts):
    """Обновить базу данных новыми скидками после парсинга."""
    service_id = await get_service_id(pool, service_name)
    if service_id is None:
        await add_service(pool, service_name)
        service_id = await get_service_id(pool, service_name)

    async with pool.acquire() as conn:
        for discount in discounts:
            await conn.execute("""
                INSERT INTO parsed_discounts (service_id, product_name, price_new, price_old, discount_percent)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (service_id, product_name)
                DO UPDATE SET 
                    price_new = EXCLUDED.price_new,
                    price_old = EXCLUDED.price_old,
                    discount_percent = EXCLUDED.discount_percent,
                    parsed_at = NOW();
            """, service_id, discount['name'], discount['price'], discount['old_price'], discount['discount'])

async def get_unseen_discounts(pool, user_id, service_id):
    """Получить скидки, которые пользователь ещё не видел."""
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT pd.discount_id, pd.product_name, pd.price_new, pd.price_old, pd.discount_percent
            FROM parsed_discounts pd
            LEFT JOIN sent_discounts sd 
            ON pd.discount_id = sd.discount_id AND sd.user_id = $1
            WHERE pd.service_id = $2
            ORDER BY pd.parsed_at DESC;
        """, user_id, service_id)

async def mark_discounts_as_sent(pool, user_id, service_id, discount_ids):
    """Отметить скидки как отправленные пользователю."""
    async with pool.acquire() as conn:
        for discount_id in discount_ids:
            await conn.execute("""
                INSERT INTO sent_discounts (user_id, service_id, discount_id)
                VALUES ($1, $2, $3)
                ON CONFLICT DO NOTHING;
            """, user_id, service_id, discount_id)

# ======= Функции для статистики ======= #
async def count_users(pool):
    """Подсчитать количество пользователей."""
    async with pool.acquire() as conn:
        record = await conn.fetchval("""
            SELECT COUNT(*) FROM users;
        """)
        return record

async def count_subscriptions(pool):
    """Подсчитать количество подписок."""
    async with pool.acquire() as conn:
        record = await conn.fetchval("""
            SELECT COUNT(*) FROM subscriptions;
        """)
        return record

async def count_sent_discounts(pool):
    """Подсчитать количество отправленных скидок."""
    async with pool.acquire() as conn:
        record = await conn.fetchval("""
            SELECT COUNT(*) FROM sent_discounts;
        """)
        return record

async def get_user_subscriptions(pool, user_id):
    """Получить активные подписки пользователя."""
    async with pool.acquire() as conn:
        try:
            query = """
                SELECT s.service_id, srv.service_name, s.discount_threshold, s.notification_time
                FROM subscriptions s
                JOIN services srv ON s.service_id = srv.service_id
                WHERE s.user_id = $1;
            """
            subscriptions = await conn.fetch(query, user_id)
            return [dict(row) for row in subscriptions]
        except Exception as e:
            logger.error(f"Ошибка при получении подписок для пользователя {user_id}: {e}")
            return []
        
async def remove_subscription(pool, user_id, service_name):
    """Удалить подписку пользователя на указанный сервис."""
    async with pool.acquire() as conn:
        try:
            query = """
                DELETE FROM subscriptions
                USING services
                WHERE subscriptions.user_id = $1 
                AND services.service_name = $2 
                AND subscriptions.service_id = services.service_id;
            """
            result = await conn.execute(query, user_id, service_name)
            if result and "DELETE" in result:
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при удалении подписки пользователя {user_id} на сервис {service_name}: {e}")
            return False
