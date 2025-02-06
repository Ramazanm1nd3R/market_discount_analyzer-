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

        # Получаем HTML-код в оперативной памяти
        soup = BeautifulSoup(driver.page_source, "html.parser")
        discounts = []

        # Ищем блоки товаров
        products = soup.select(".product-block")
        for product in products:
            try:
                # Извлекаем полное название товара
                name = product.select_one(".product-block__descr").get_text(strip=True)

                # Извлекаем текущую цену
                price = product.select_one(".product-block__price").get_text(strip=True)

                # Извлекаем старую цену (если есть)
                old_price = product.select_one(".product-block__old-price")
                old_price = old_price.get_text(strip=True) if old_price else "Нет"

                # Извлекаем скидку (если есть)
                discount = product.select_one(".product-block__stock")
                discount = discount.get_text(strip=True) if discount else "Нет"

                discounts.append({
                    "name": name,  # Полное название
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
