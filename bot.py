import telebot
import requests
import time

# Thay thế bằng token và chat ID của bạn
bot = telebot.TeleBot('8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM')
chat_id = '5166662146'

def get_bitcoin_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
    response = requests.get(url)
    data = response.json()
    return data['bitcoin']['usd']

while True:
    price = get_bitcoin_price()
    message = f"Giá Bitcoin hiện tại: ${price}"
    bot.send_message(chat_id, message)
    time.sleep(3600)  # Cập nhật mỗi giờ
