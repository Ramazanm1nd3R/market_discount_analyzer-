# 🛍️ Discount Hunter Bot

Welcome to the **Discount Hunter Bot** project, your go-to Telegram assistant for finding the best deals and discounts at supermarkets and online stores in Kazakhstan! 🌟

## 🛠️ Project Description
This bot uses **Selenium** 🕵️‍♂️ and **BeautifulSoup** 🍜 to scrape the latest discounts from **Magnum** and **Lamoda** and etc websites in future. 

## 🎯 Features
- **Telegram Commands**
  - `/start` – Greets you and shows the main menu.
  - `/help` – Displays available commands and usage.
  - `/info` – Provides information about the bot and its creator.

- **Store Selection:**  
  🛒 **Magnum:** Find discounts on groceries and household items.  
  🛍️ **Lamoda:** Find deals on fashion items with options for Women, Men, or Kids.  

- **Advanced Parsing:**  
  - **Selenium** handles dynamic web content.  
  - **BeautifulSoup** extracts detailed product information (name, price, old price, discount, sizes, ratings).  
  - Separate logic for different stores, with error handling and filtering.  

## 💻 Installation
Follow these steps to run the bot on your local machine:

1. **Clone this repository:**
   ```bash
   git clone https://github.com/Ramazanm1nd3R/market_discount_analyzer-

2. Navigate to the project directory:
   ```bash
   cd market_discount_analyzer-
   ```

3. Set up a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file and add your Telegram bot token:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   ```

6. Place the appropriate ChromeDriver in the `chromedriver-win64` directory.

7. Run the bot:
   ```bash
   python bot.py
   ```

## 🤖 How It Works
1. Start: The bot shows a store selection: Magnum or Lamoda
2. For Lamoda: You choose between Women's, Men's, or Kids' categories.
3. Discount Selection: You choose a discount threshold (10%, 20%, 30%, 50%, or enter manually).
4. The bot scrapes the selected store’s website, filters discounts, and sends results as a .txt file.

## 📜 Example Output
```
🛍️ Бренд: adidas
📌 Название: Футболка Future Icons 3-Stripes
💰 Цена: 9 990 ₸
💸 Старая цена: 26 990 ₸
📉 Скидка: −62%
⭐ Рейтинг: Нет
📏 Размеры: 40/42, 44/46, 48/50, 52/54, 56/58

🛍️ Бренд: Reebok
📌 Название: Кроссовки GLIDE
💰 Цена: 31 590 ₸
💸 Старая цена: 45 100 ₸
📉 Скидка: −29%
⭐ Рейтинг: 4.6(513)
📏 Размеры: 39, 40, 41, 42, 43, 44, 45
```
## 🛒 Supported Stores
- *Magnum* – Groceries, household items, beverages.
- *Lamoda* – Fashion deals with category selection:
   - 👗 Women's Clothing
   - 👔 Men's Clothing
   - 👶 Kids' Clothing


## 😂 Why Use This Bot?
- Save money 💰 while sipping your tea ☕ with a smile 😁.
- Impress your friends with your Telegram bot wizardry 🧙‍♂️.
- Never miss a deal – unless you're too busy scrolling memes.

## 🔧 Troubleshooting
- **"Element not found"?**
  - Ensure that the CSS selectors in the parser match the current structure of the Magnum website.

- **"SSL certificate error"?**
  - Selenium uses `--headless` and bypasses these issues for you.

- **ChromeDriver issues?**
  - Ensure your ChromeDriver version matches your installed Chrome browser.

## ✨ Credits
Built with ❤️ by **Ramazanm1nd3R**.

- GitHub: [Ramazanm1nd3R](https://github.com/Ramazanm1nd3R)
- Telegram: Where all the magic happens ✨

## 🚀 Future Plans
- Add multi-language support (Kazakh 🇰🇿 and Russian 🇷🇺).
- Add more store options (e.g., Wildberries, Kaspi).
- Schedule automatic discount alerts.
- Implement search filters (brands, categories, price range).
- Develop the application for Andioid/IOS

---

**💸 Save money and shop smarter with Discount Hunter Bot! 🛍️**
