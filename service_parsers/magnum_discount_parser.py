import requests
from bs4 import BeautifulSoup

def parse_magnum_discounts(url):
    """
    Парсер скидок с веб-страницы Magnum.
    url: URL страницы со скидками.
    """
    # Получаем HTML-код страницы
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Не удалось загрузить страницу: {url}")

    soup = BeautifulSoup(response.text, "html.parser")
    discounts = []

    # Ищем блоки товаров
    products = soup.select(".product-block")  # Убедись, что CSS-селектор соответствует структуре сайта
    for product in products:
        try:
            # Извлекаем название товара
            name = product.select_one(".product-block__descr").text.strip()

            # Извлекаем текущую цену
            price = product.select_one(".product-block__price").text.strip()

            # Извлекаем старую цену (если есть)
            old_price = product.select_one(".product-block__old-price")
            old_price = old_price.text.strip() if old_price else None

            # Извлекаем скидку (если есть)
            discount = product.select_one(".product-block__stock")
            discount = discount.text.strip() if discount else None

            # Извлекаем ссылку на изображение
            image = product.select_one(".product-block__img img")["src"]

            discounts.append({
                "name": name,
                "price": price,
                "old_price": old_price,
                "discount": discount,
                "image": image
            })
        except Exception as e:
            print(f"Ошибка при обработке товара: {e}")

    return discounts
