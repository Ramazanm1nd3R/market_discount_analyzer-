from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os

# URL для категорий Lamoda
LAMODA_URLS = {
    "women": "https://www.lamoda.kz/c/4153/default-women/?is_sale=1&display_locations=outlet",
    "men": "https://www.lamoda.kz/c/4152/default-men/?is_sale=1&display_locations=outlet",
    "kids": "https://www.lamoda.kz/c/4154/default-kids/?display_locations=outlet&is_sale=1"
}

def parse_lamoda_discounts(category_url):
    """
    Парсер скидок с сайта Lamoda с использованием Selenium.
    category_url: URL страницы выбранной категории (мужская, женская или детская).
    """
    # Настройка пути к ChromeDriver
    chromedriver_path = os.path.join(os.path.dirname(__file__), "../chromedriver-win64/chromedriver.exe")
    service = Service(chromedriver_path)

    # Настройка Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-webgl")
    options.add_argument("--use-gl=swiftshader")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(category_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "x-product-card__card"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        discounts = []

        products = soup.select(".x-product-card__card")
        for product in products:
            try:
                name = product.select_one(".x-product-card-description__product-name").get_text(strip=True)
                brand = product.select_one(".x-product-card-description__brand-name").get_text(strip=True)
                price_new = product.select_one(".x-product-card-description__price-new").get_text(strip=True)
                price_old = (
                    product.select_one(".x-product-card-description__price-old").get_text(strip=True)
                    if product.select_one(".x-product-card-description__price-old") else "Нет"
                )
                discount = (
                    product.select_one("._badgeContent_1yjde_7 span").get_text(strip=True)
                    if product.select_one("._badgeContent_1yjde_7 span") else "Нет"
                )
                rating = (
                    product.select_one("._rating_1xcfv_13").get_text(strip=True)
                    if product.select_one("._rating_1xcfv_13") else "Нет"
                )
                sizes = [
                    size.get_text(strip=True)
                    for size in product.select(".x-product-card-sizes__size")
                ]

                discounts.append({
                    "brand": brand,
                    "name": name,
                    "price": price_new,
                    "old_price": price_old,
                    "discount": discount,
                    "rating": rating,
                    "sizes": ", ".join(sizes)
                })
            except Exception as e:
                print(f"Ошибка при обработке товара: {e}")

        return discounts
    finally:
        driver.quit()
