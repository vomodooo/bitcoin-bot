import requests
import telebot
import schedule
import time

# Thay thế bằng token và chat ID của bạn
bot = telebot.TeleBot('8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM')
chat_id = '8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM'

def get_bitcoin_price_binance():
    """Lấy giá Bitcoin hiện tại từ sàn Binance.

    Returns:
        float: Giá Bitcoin hiện tại theo USD.
    """

    url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
    response = requests.get(url)
    data = json.loads(response.text)
    return float(data['price'])

def send_price_update():
    price = get_bitcoin_price_binance()
    bot.send_message(chat_id, f"Giá Bitcoin hiện tại trên Binance: ${price}")

# Lên lịch gửi tin nhắn mỗi giờ
schedule.every().hour.do(send_price_update)

while True:
    schedule.run_pending()
    time.sleep(1)
