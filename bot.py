import telebot
import requests
import schedule
import time
from flask import Flask
import os

app = Flask(__name__)

# Các route và xử lý khác

port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
    
# Thông tin API và chat ID
BOT_TOKEN = '8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM'
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
    formatted_price = f"${price_btc_usd:,.2f}"  # Thêm dấu $ và định dạng số
    return formatted_price

def send_price_update():
    price = get_bitcoin_price()
    bot.send_message(CHAT_ID, f"Giá Bitcoin hiện tại: {price}")

# Lịch gửi thông báo
schedule.every(1).hour.do(send_price_update)

# Xử lý lệnh /gia_btc
@bot.message_handler(commands=['gia_btc'])
def get_current_price(message):
    price = get_bitcoin_price()
    bot.reply_to(message, f"Giá Bitcoin hiện tại: {price}")

# Chạy vòng lặp để xử lý các lệnh
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
