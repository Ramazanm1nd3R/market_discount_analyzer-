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
            discount_text = item["discount"]
            # Проверяем, содержит ли скидка числовые данные
            if "Нет" in discount_text or "Цена отсутствует" in discount_text:
                continue
            
            # Извлекаем числовое значение скидки
            discount_value = int(discount_text.replace("%", "").replace("-", "").strip())
            if discount_value >= threshold:
                filtered_discounts.append(item)
        except (ValueError, KeyError) as e:
            logger.warning(f"Некорректная запись для скидки товара: {item.get('name', 'Без названия')}, причина: {e}")
    
    # Логируем общее количество исключённых записей
    if len(filtered_discounts) < len(discounts):
        logger.info(f"Исключено {len(discounts) - len(filtered_discounts)} некорректных записей.")

    return filtered_discounts
