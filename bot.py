import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from service_parsers.magnum_discount_parser import parse_magnum_discounts
from scripts.filter_discounts import filter_discounts_by_threshold

# Загрузка переменных окружения из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# URL страницы со скидками
MAGNUM_URL = "https://magnum.kz/catalog?discountType=all&city=almaty"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! 👋\n"
        "Я помогу найти скидки, которые ты задашь. Напиши /help, чтобы узнать больше!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = (
        "/start - Начать работу с ботом\n"
        "/help - Список доступных команд\n"
        "/info - Информация о боте\n"
        "/discounts - Найти скидки с минимальным порогом"
    )
    await update.message.reply_text(f"Вот что я умею:\n\n{commands}")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Этот бот создан для поиска скидок в Казахстане! 🇰🇿\n"
        "Автор: Ramazanm1nd3R\n"
        "GitHub: https://github.com/Ramazanm1nd3R\n"
        "Вопросы и предложения: /help"
    )

async def handle_threshold_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        threshold = int(float(update.message.text.strip()))
        discount_data = parse_magnum_discounts(MAGNUM_URL)
        filtered_discounts = filter_discounts_by_threshold(discount_data, threshold)

        if not filtered_discounts:
            await update.message.reply_text(f"Нет скидок больше или равных {threshold}%. Попробуйте позже.")
            return

        file_path = "filtered_discounts.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            for item in filtered_discounts:
                file.write(
                    f"Название: {item['name']}\n"
                    f"Цена: {item['price']}\n"
                    f"Старая цена: {item['old_price']}\n"
                    f"Скидка: {item['discount']}%\n\n"
                )

        with open(file_path, "rb") as file:
            await update.message.reply_document(document=file)

        os.remove(file_path)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число.")
    except Exception as e:
        logger.error(f"Ошибка при обработке скидок: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса. Попробуйте позже.")

async def discounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Введите минимальный процент скидки (например, 20):")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("discounts", discounts))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_threshold_response))

    logger.info("Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
