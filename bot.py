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

# URL страницы со скидками
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
        "🤖 Бот для поиска скидок в магазинах Казахстана!\n"
        "Автор: Ramazanm1nd3R\n"
        "GitHub: https://github.com/Ramazanm1nd3R"
    )

async def show_discount_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    await update.message.reply_text(
        "📊 Выбери минимальный процент скидки:",
        reply_markup=reply_markup
    )

async def handle_discount_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор скидки через кнопки."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data.startswith("discount_"):
        threshold = int(callback_data.split("_")[1])
        await send_filtered_discounts(update, threshold)
    elif callback_data == "custom_discount":
        await query.message.reply_text("✍ Введите минимальный процент скидки (например, 25):")

async def handle_manual_threshold(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает вручную введённый порог скидки."""
    try:
        threshold = int(float(update.message.text.strip()))
        await send_filtered_discounts(update, threshold)
    except ValueError:
        await update.message.reply_text("🚫 Пожалуйста, введите число.")

async def send_filtered_discounts(update: Update, threshold: int) -> None:
    """Отправляет пользователю отфильтрованные скидки."""
    try:
        discount_data = parse_magnum_discounts(MAGNUM_URL)
        filtered_discounts = filter_discounts_by_threshold(discount_data, threshold)

        if not filtered_discounts:
            if update.callback_query:
                await update.callback_query.message.reply_text(
                    f"📭 Нет скидок от {threshold}% и выше. Попробуйте позже."
                )
            else:
                await update.message.reply_text(
                    f"📭 Нет скидок от {threshold}% и выше. Попробуйте позже."
                )
            return

        file_path = "filtered_discounts.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            for item in filtered_discounts:
                file.write(
                    f"📌 Название: {item['name']}\n"
                    f"💰 Цена: {item['price']}\n"
                    f"💸 Старая цена: {item['old_price']}\n"
                    f"📉 Скидка: {item['discount']}%\n\n"
                )

        with open(file_path, "rb") as file:
            if update.callback_query:
                await update.callback_query.message.reply_document(document=file)
            else:
                await update.message.reply_document(document=file)

        os.remove(file_path)
    except Exception as e:
        logger.error(f"Ошибка при обработке скидок: {e}")
        if update.callback_query:
            await update.callback_query.message.reply_text("🚨 Произошла ошибка при обработке запроса.")
        else:
            await update.message.reply_text("🚨 Произошла ошибка при обработке запроса.")

# ======= 🚀 ОСНОВНОЙ ФУНКЦИОНАЛ БОТА ======== #

def main() -> None:
    """Главная функция для запуска бота."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчики сообщений и кнопок
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("🎉 Скидки"), show_discount_buttons))
    application.add_handler(MessageHandler(filters.Regex("ℹ️ О боте"), info))
    application.add_handler(MessageHandler(filters.Regex("❓ Помощь"), help_command))
    application.add_handler(CallbackQueryHandler(handle_discount_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_threshold))

    logger.info("🚀 Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
