import os
from service_parsers.lamoda_discount_parser import parse_lamoda_discounts

# URL для теста (например, мужская одежда)
LAMODA_URL = "https://www.lamoda.kz/c/4152/default-men/?is_sale=1&display_locations=outlet"

def test_lamoda_parser(url):
    print("\nНачинается парсинг Lamoda...")
    try:
        discounts = parse_lamoda_discounts(url)
        
        if not discounts:
            print("\n❌ Нет данных о скидках.")
            return
        
        print(f"\n✅ Найдено товаров: {len(discounts)}")
        
        for item in discounts[:10]:  # Выводим первые 10 товаров для проверки
            print(f"\n🔹 Бренд: {item['brand']}")
            print(f"   📌 Название: {item['name']}")
            print(f"   💰 Цена: {item['price']}")
            print(f"   💸 Старая цена: {item['old_price']}")
            print(f"   📉 Скидка: {item['discount']}")
            print(f"   ⭐ Рейтинг: {item['rating']}")
            print(f"   📏 Размеры: {item['sizes']}")
            print("---------------------------")
    except Exception as e:
        print(f"Ошибка при выполнении парсинга: {e}")

if __name__ == "__main__":
    test_lamoda_parser(LAMODA_URL)