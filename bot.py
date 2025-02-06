import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from service_parsers.magnum_discount_parser import parse_magnum_discounts

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

# Команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n"
        "Я помогу найти скидки, которые ты задашь. Напиши /help, чтобы узнать больше!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /help"""
    commands = (
        "/start - Начать работу с ботом\n"
        "/help - Список доступных команд\n"
        "/info - Информация о боте\n"
        "/discounts - Показать текущие скидки в файле"
    )
    await update.message.reply_text(f"Вот что я умею:\n\n{commands}")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /info"""
    await update.message.reply_text(
        "Этот бот создан для поиска скидок в Казахстане! 🇰🇿\n"
        "Автор: Ramazanm1nd3R\n"
        "GitHub: https://github.com/Ramazanm1nd3R\n"
        "Вопросы и предложения: /help"
    )


async def discounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /discounts - сохранение и отправка скидок в файл"""
    try:
        # Парсим данные о скидках
        discount_data = parse_magnum_discounts(MAGNUM_URL)
        if not discount_data:
            await update.message.reply_text("Скидок не найдено. Попробуйте позже.")
            return

        # Создаем текстовый файл с информацией о скидках
        file_path = "magnum_discounts.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            for item in discount_data:
                file.write(
                    f"Название: {item['name']}\n"
                    f"Цена: {item['price']}\n"
                    f"Старая цена: {item['old_price']}\n"
                    f"Скидка: {item['discount']}\n\n"
                )

        # Отправляем файл пользователю
        with open(file_path, "rb") as file:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=file)

        # Удаляем файл после отправки
        os.remove(file_path)

        # Уведомление об успешной отправке
        logger.info("Файл со скидками успешно отправлен пользователю.")
    except Exception as e:
        logger.error(f"Ошибка при получении скидок: {e}")
        await update.message.reply_text("Произошла ошибка при получении скидок. Попробуйте позже.")


def main() -> None:
    """Главная функция для запуска бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрация команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("discounts", discounts))

    # Запуск бота
    logger.info("Бот запущен!")
    application.run_polling()


if __name__ == "__main__":
    main()
