import os
import telebot
import requests
import pandas as pd
import matplotlib.pyplot as plt
import schedule
import time
import locale
from flask import Flask

# Thông tin bot và chat
BOT_TOKEN = '8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM'
CHAT_ID = 5166662146
BINANCE_API_URL = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'

# Khởi tạo bot
bot = telebot.TeleBot(BOT_TOKEN)

# Hàm xử lý lệnh /gia_btc
@bot.message_handler(commands=['gia_btc'])
def get_current_price(message):
    price = get_bitcoin_price()
    
    # Định dạng giá với dấu chấm ngăn cách phần nghìn và đơn vị USD
    locale.setlocale(locale.LC_ALL, 'en_US')
    formatted_price = locale.format_string("%#.2f", price, grouping=True)

    bot.reply_to(message, f"Giá Bitcoin hiện tại: {formatted_price} USD")
    
# Hàm lấy giá Bitcoin
def get_bitcoin_price():
    response = requests.get(BINANCE_API_URL)
    data = response.json()
    return float(data['price'])

# Hàm gửi thông báo cập nhật giá
def send_price_update():
    price = get_bitcoin_price()
    bot.send_message(CHAT_ID, f"Giá Bitcoin hiện tại: {price:.2f} USDT")

# Lên lịch gửi thông báo
schedule.every().hour.do(send_price_update)

# Hàm vẽ biểu đồ (bạn có thể tùy chỉnh thời gian và loại biểu đồ)
def plot_price_chart(days=1):
    # ... (Code để lấy dữ liệu lịch sử và vẽ biểu đồ)
    plt.savefig('chart.png')
    bot.send_photo(CHAT_ID, photo=open('chart.png', 'rb'))

# Hàm chính
def main():
    port = int(os.environ.get('PORT', 5000))
    # Khởi chạy ứng dụng Flask
    app = Flask(__name__)
    @app.route('/')
    def hello():
        return 'Bot is running'

    # Khởi chạy cả ứng dụng Flask và scheduler
    app.run(host='0.0.0.0', port=port)
    schedule.run_pending()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
