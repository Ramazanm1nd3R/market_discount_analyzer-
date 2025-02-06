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
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

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
                name = product.select_one(".product-block__descr").text.strip()
                price = product.select_one(".product-block__price").text.strip()
                old_price = product.select_one(".product-block__old-price")
                old_price = old_price.text.strip() if old_price else "Нет"
                discount = product.select_one(".product-block__stock")
                discount = discount.text.strip() if discount else "Нет"
                image = product.select_one(".product-block__img img")
                image = image["src"] if image and "src" in image.attrs else "Нет изображения"

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
    finally:
        driver.quit()
