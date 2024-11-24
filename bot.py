import telebot
import requests
import pandas as pd
import matplotlib.pyplot as plt
import schedule
import time

# Thay thế các thông tin sau bằng thông tin của bạn
BOT_TOKEN = '8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM'
CHAT_ID = 5166662146
BINANCE_API_URL = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'

bot = telebot.TeleBot(BOT_TOKEN)

def get_bitcoin_price():
    response = requests.get(BINANCE_API_URL)
    data = response.json()
    return float(data['price'])

def send_price_update():
    price = get_bitcoin_price()
    bot.send_message(CHAT_ID, f"Giá Bitcoin hiện tại: {price:.2f} USDT")

# Lên lịch gửi thông báo mỗi giờ
schedule.every().hour.do(send_price_update)

# Vẽ biểu đồ (bạn có thể tùy chỉnh thời gian và loại biểu đồ)
def plot_price_chart(days=1):
    # ... (Code để lấy dữ liệu lịch sử và vẽ biểu đồ)
    bot.send_photo(CHAT_ID, photo=open('chart.png', 'rb'))

# Hàm chính
def main():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
