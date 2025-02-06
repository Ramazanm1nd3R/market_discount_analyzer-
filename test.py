from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# URL страницы со скидками
MAGNUM_URL = "https://magnum.kz/catalog?discountType=all&city=almaty"

def fetch_magnum_page(url):
    """
    Использует Selenium для загрузки страницы и сохранения полного HTML-кода в файл.
    """
    # Настройка пути к ChromeDriver
    chromedriver_path = os.path.join(os.path.dirname(__file__), "chromedriver-win64/chromedriver.exe")
    service = Service(chromedriver_path)

    # Настройка Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-webgl")  # Отключение WebGL
    options.add_argument("--use-gl=swiftshader")  # Использование SwiftShader
    options.add_argument("--log-level=3")  # Уменьшение логов

    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Открываем страницу
        driver.get(url)
        print("Ожидание загрузки страницы...")

        # Ожидаем, пока появится элемент с товарами
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "product-block")))

        # Получаем HTML-код страницы
        html = driver.page_source

        # Сохраняем HTML-код в файл
        with open("magnum_test_selenium.html", "w", encoding="utf-8") as file:
            file.write(html)
        
        print("HTML-код страницы сохранен в 'magnum_test_selenium.html'.")
        print(f"Длина содержимого: {len(html)} символов.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_magnum_page(MAGNUM_URL)
