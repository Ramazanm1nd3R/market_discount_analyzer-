import logging

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция для фильтрации скидок по заданному проценту
def filter_discounts_by_threshold(discounts, threshold):
    """
    Фильтрует скидки по заданному минимальному порогу.

    :param discounts: список скидок (list of dicts)
    :param threshold: минимальный процент скидки (int)
    :return: список отфильтрованных скидок
    """
    filtered_discounts = []
    for item in discounts:
        try:
            # Проверяем наличие и корректность поля скидки
            if "discount" not in item or not item["discount"]:
                logger.warning(f"Пропущен товар без скидки: {item.get('name', 'Без имени')}")
                continue

            discount_value = int(item["discount"].replace("%", "").replace("-", "").strip())
            if discount_value >= threshold:
                filtered_discounts.append(item)
        except ValueError:
            logger.warning(f"Не удалось обработать скидку для товара: {item.get('name', 'Без имени')}")
    return filtered_discounts
