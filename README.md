# 🛍️ Discount Hunter Bot

Welcome to the **Discount Hunter Bot** project, your go-to Telegram assistant for finding the best deals and discounts at supermarkets, marketplaces and etc in Kazakhstan! 🌟

## 🛠️ Project Description
This bot uses **Selenium** 🕵️‍♂️ and **BeautifulSoup** 🍜 to scrape the latest discounts from Magnum's website and delivers them right to your Telegram chat. Whether you're hunting for deals on coffee ☕, pasta 🍝, or laundry detergent 🧺, this bot's got you covered!

## 🎯 Features
- **Telegram Commands**
  - `/start` – Welcomes you with open arms (and maybe a discount).
  - `/help` – Explains everything you need to know.
  - `/info` – Tells you about the bot and its creator.
  - `/discounts` – Fetches the latest discounts and sends them in a handy file.

- **Advanced Parsing**
  - Handles dynamic web content using Selenium.
  - Extracts detailed product information: name, current price, old price, and discount percentage.
  - Flexible logic to adapt to changes in the Magnum website.

## 💻 Installation
Follow these steps to run the bot on your local machine:

1. Clone this repository:
   ```bash
   git clone https://github.com/Ramazanm1nd3R/market_discount_analyzer-
   ```

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
1. The bot listens for your commands in Telegram.
2. It scrapes data from the [Magnum website](https://magnum.kz/) using Selenium.
3. It processes and extracts discounts with BeautifulSoup.
4. Sends the discount data as a handy `.txt` file to your chat.

## 📜 Example Output
```
Название: Чай "Пиала"
Цена: 1,099 тг
Старая цена: 1,659 тг
Скидка: -34%

Название: Макароны "Premium"
Цена: 499 тг
Старая цена: 789 тг
Скидка: -37%
```

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
- Explore new discount sources (we're watching you, other supermarkets 👀).
- Automatically send deals based on your preferences.

---

### Let's save money and have fun while we're at it! 💸🎉
