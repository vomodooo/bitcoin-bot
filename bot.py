import telebot
import requests
import pandas as pd
import matplotlib.pyplot as plt
import schedule
import time
from io import BytesIO

# Thông tin API và chat ID
BOT_TOKEN = '8058083423:AAEdB8bsCgLw1JeSeklG-44sqSmxO45bKRsM'
CHAT_ID = 5166662146
bot = telebot.TeleBot(BOT_TOKEN)

def get_bitcoin_price():
    # Lấy giá BTC từ Binance
    url_btc = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
    response = requests.get(url_btc)
    data = response.json()
    price_btc_usdt = float(data['price'])

    # Lấy tỷ giá USD/USDT
    url_exchange_rate = 'https://api.exchangerate.host/latest?base=USDT&symbols=USD'
    response = requests.get(url_exchange_rate)
    data = response.json()
    usd_to_usdt = data['rates']['USD']

    # Quy đổi và định dạng giá
    price_btc_usd = price_btc_usdt * usd_to_usdt
    formatted_price = f"{price_btc_usd:,.2f}"  # Định dạng với dấu phẩy ngăn cách hàng nghìn
    return formatted_price

def send_price_update():
    price = get_bitcoin_price()
    bot.send_message(CHAT_ID, f"Giá Bitcoin hiện tại: {price} USD")

def plot_price_chart(days=1):
    # Lấy dữ liệu lịch sử giá Bitcoin
    # ...
    # Vẽ biểu đồ
    # ...
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    bot.send_photo(CHAT_ID, photo=buf)

# Lịch gửi thông báo
schedule.every().hour.do(send_price_update)

# Xử lý lệnh /gia_btc
@bot.message_handler(commands=['gia_btc'])
def get_current_price(message):
    price = get_bitcoin_price()
    bot.reply_to(message, f"Giá Bitcoin hiện tại: {price:.2f} USDT")

@bot.message_handler(commands=['chart'])
def send_chart(message):
    plot_price_chart()

# Chạy vòng lặp để xử lý các lệnh
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
