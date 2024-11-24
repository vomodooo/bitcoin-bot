import requests
import telebot
import time

# Thay thế bằng token và chat ID của bạn
bot = telebot.TeleBot('8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM')
chat_id = '5166662146'

def get_bitcoin_price():
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
        response = requests.get(url)
        data = response.json()

        # Check if 'bitcoin' key exists before accessing it
        if 'bitcoin' in data:
            return data['bitcoin']['usd']
        else:
            # Handle the case where 'bitcoin' key is missing
            print("API response structure might have changed. Data doesn't contain 'bitcoin' key.")
            return None
    except requests.exceptions.RequestException as e:
        # Handle network errors
        print(f"Error getting Bitcoin price: {e}")
        return None

@bot.message_handler(commands=['gia_bitcoin'])
def send_current_price(message):
    price = get_bitcoin_price()
    bot.reply_to(message, f"Giá Bitcoin hiện tại: ${price}")

# Phần cập nhật giá định kỳ vẫn giữ nguyên
while True:
    price = get_bitcoin_price()
    message = f"Giá Bitcoin hiện tại: ${price}"
    bot.send_message(chat_id, message)
    time.sleep(3600)  # Cập nhật mỗi giờ

# Bắt đầu bot
bot.polling()
