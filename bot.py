import os
import logging
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CallbackQueryHandler,
    CommandHandler, ContextTypes, MessageHandler, filters
)
from dotenv import load_dotenv
from service_parsers.magnum_discount_parser import parse_magnum_discounts
from service_parsers.lamoda_discount_parser import parse_lamoda_discounts, LAMODA_URLS
from scripts.filter_discounts import filter_discounts_by_threshold

# Загрузка переменных окружения из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# URL страницы со скидками для Magnum
MAGNUM_URL = "https://magnum.kz/catalog?discountType=all&city=almaty"


# ======= 📌 ФУНКЦИИ КНОПОК ======== #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветственное сообщение с кнопками."""
    keyboard = [
        [KeyboardButton("🎉 Скидки"), KeyboardButton("ℹ️ О боте")],
        [KeyboardButton("❓ Помощь")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! 👋\n"
        "Выбери действие из кнопок ниже:",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Выводит справочную информацию."""
    await update.message.reply_text(
        "👋 Вот что я умею:\n\n"
        "🎉 Скидки — найти товары со скидкой.\n"
        "ℹ️ О боте — узнать информацию обо мне.\n"
        "❓ Помощь — показать это сообщение снова."
    )


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Информация о боте."""
    await update.message.reply_text(
        "🤖 Бот для поиска скидок в магазинах Magnum и Lamoda!\n"
        "Автор: Ramazanm1nd3R\n"
        "GitHub: https://github.com/Ramazanm1nd3R"
    )


async def show_store_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Выбор магазина (Magnum или Lamoda)."""
    keyboard = [
        [
            InlineKeyboardButton("🛒 Magnum", callback_data="store_magnum"),
            InlineKeyboardButton("🛍️ Lamoda", callback_data="store_lamoda")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🛒 Выберите магазин для поиска скидок:", reply_markup=reply_markup)


async def handle_store_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор магазина."""
    query = update.callback_query
    await query.answer()

    store = query.data.split("_")[1]
    context.user_data["store"] = store

    if store == "lamoda":
        await show_lamoda_category_selection(query.message)
    elif store == "magnum":
        await show_discount_buttons(query.message)


async def show_lamoda_category_selection(message) -> None:
    """Выбор категории товаров Lamoda."""
    keyboard = [
        [
            InlineKeyboardButton("👗 Женская", callback_data="lamoda_women"),
            InlineKeyboardButton("👔 Мужская", callback_data="lamoda_men"),
            InlineKeyboardButton("👶 Детская", callback_data="lamoda_kids")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("👚 Выберите категорию товаров для Lamoda:", reply_markup=reply_markup)


async def handle_lamoda_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор категории Lamoda."""
    query = update.callback_query
    await query.answer()

    category = query.data.split("_")[1]
    context.user_data["lamoda_category"] = category
    await show_discount_buttons(query.message)


async def show_discount_buttons(message) -> None:
    """Показывает кнопки для выбора порога скидки."""
    keyboard = [
        [
            InlineKeyboardButton("10%", callback_data="discount_10"),
            InlineKeyboardButton("20%", callback_data="discount_20"),
            InlineKeyboardButton("30%", callback_data="discount_30"),
            InlineKeyboardButton("50%", callback_data="discount_50"),
        ],
        [InlineKeyboardButton("✍ Ввести вручную", callback_data="custom_discount")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(
        "📊 Выберите минимальный процент скидки:",
        reply_markup=reply_markup
    )


async def handle_discount_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор скидки через кнопки."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data.startswith("discount_"):
        threshold = int(callback_data.split("_")[1])
        await send_filtered_discounts(update, context, threshold)
    elif callback_data == "custom_discount":
        await query.message.reply_text("✍ Введите минимальный процент скидки (например, 25):")


async def handle_manual_threshold(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает вручную введённый порог скидки."""
    try:
        threshold = int(float(update.message.text.strip()))
        await send_filtered_discounts(update, context, threshold)
    except ValueError:
        await update.message.reply_text("🚫 Пожалуйста, введите число.")


async def send_filtered_discounts(update: Update, context: ContextTypes.DEFAULT_TYPE, threshold: int) -> None:
    """Отправляет пользователю отфильтрованные скидки из выбранного магазина."""
    try:
        store = context.user_data.get("store")
        discount_data = []

        if store == "magnum":
            discount_data = parse_magnum_discounts(MAGNUM_URL)

        elif store == "lamoda":
            category = context.user_data.get("lamoda_category")
            url = LAMODA_URLS.get(category)
            discount_data = parse_lamoda_discounts(url)

        if not discount_data:
            await update.effective_message.reply_text(
                "🚫 Ошибка получения данных или нет доступных товаров. Попробуйте позже."
            )
            return

        filtered_discounts = []
        for item in discount_data:
            try:
                discount_value = int(item["discount"].replace("−", "").replace("%", "").strip())
                if discount_value >= threshold:
                    filtered_discounts.append(item)
            except Exception as e:
                logger.warning(f"Некорректная запись для скидки товара: {item['name']}, ошибка: {e}")

        if not filtered_discounts:
            await update.effective_message.reply_text(
                f"📭 Нет скидок от {threshold}% и выше. Попробуйте позже."
            )
            return

        file_path = "filtered_discounts.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            for item in filtered_discounts:
                file.write(
                    f"🛍️ Бренд: {item['brand']}\n"
                    f"📌 Название: {item['name']}\n"
                    f"💰 Цена: {item['price']}\n"
                    f"💸 Старая цена: {item['old_price']}\n"
                    f"📉 Скидка: {item['discount']}\n"
                    f"⭐ Рейтинг: {item['rating']}\n"
                    f"📏 Размеры: {item['sizes']}\n"
                    "---------------------------\n"
                )

        with open(file_path, "rb") as file:
            await update.effective_message.reply_document(document=file)

        os.remove(file_path)

    except Exception as e:
        logger.error(f"Ошибка при обработке скидок: {e}")
        await update.effective_message.reply_text("🚨 Произошла ошибка при обработке запроса.")


# ======= 🚀 ОСНОВНОЙ ФУНКЦИОНАЛ БОТА ======== #

def main() -> None:
    """Главная функция для запуска бота."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчики сообщений и кнопок
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("🎉 Скидки"), show_store_selection))
    application.add_handler(MessageHandler(filters.Regex("ℹ️ О боте"), info))
    application.add_handler(MessageHandler(filters.Regex("❓ Помощь"), help_command))

    application.add_handler(CallbackQueryHandler(handle_store_callback, pattern="^store_"))
    application.add_handler(CallbackQueryHandler(handle_lamoda_category, pattern="^lamoda_"))
    application.add_handler(CallbackQueryHandler(handle_discount_callback, pattern="^discount_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_threshold))

    logger.info("🚀 Бот запущен!")
    application.run_polling()


if __name__ == "__main__":
    main()
