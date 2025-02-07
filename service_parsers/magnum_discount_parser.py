from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os

def parse_magnum_discounts(url):
    """
    Парсер скидок с сайта Magnum с использованием Selenium.
    url: URL страницы со скидками.
    """
    # Настройка пути к ChromeDriver
    chromedriver_path = os.path.join(os.path.dirname(__file__), "../chromedriver-win64/chromedriver.exe")
    service = Service(chromedriver_path)

    # Настройка Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Безголовый режим
    options.add_argument("--disable-gpu")  # Отключение GPU-ускорения
    options.add_argument("--no-sandbox")  # Без песочницы
    options.add_argument("--disable-dev-shm-usage")  # Ограничение использования общей памяти
    options.add_argument("--disable-webgl")  # Отключение WebGL
    options.add_argument("--use-gl=swiftshader")  # Использование программного рендеринга
    options.add_argument("--disable-software-rasterizer")  # Отключение программного растеризатора
    options.add_argument("--log-level=3")  # Сокращение логов

    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Открываем страницу
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "product-block")))

        # Получаем HTML-код
        soup = BeautifulSoup(driver.page_source, "html.parser")
        discounts = []

        # Ищем блоки товаров
        products = soup.select(".product-block")
        for product in products:
            try:
                # Извлекаем полное название товара (включаем все элементы с .product-block__descr)
                name_elements = product.select(".product-block__descr")
                name = " ".join([el.get_text(strip=True) for el in name_elements]) if name_elements else "Название отсутствует"

                # Извлекаем текущую цену
                price_elem = product.select_one(".product-block__price")
                price = price_elem.get_text(strip=True) if price_elem else "Цена отсутствует"

                # Извлекаем старую цену (если она существует)
                old_price_elem = product.select_one(".product-block__old-price")
                old_price = old_price_elem.get_text(strip=True) if old_price_elem else "Нет"

                # Извлекаем скидку, если она есть
                discount_elem = product.select_one(".product-block__stock")
                discount = discount_elem.get_text(strip=True) if discount_elem else "Нет"

                # Формируем запись о товаре
                discounts.append({
                    "name": name,
                    "price": price,
                    "old_price": old_price,
                    "discount": discount
                })
            except Exception as e:
                print(f"Ошибка при обработке товара: {e}")

        return discounts
    finally:
        # Завершаем работу WebDriver
        driver.quit()
