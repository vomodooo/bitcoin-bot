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

        if 'bitcoin' in data:
            return data['bitcoin']['usd']
        else:
            print("API response structure might have changed. Data doesn't contain 'bitcoin' key.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting Bitcoin price: {e}")
        return None

@bot.message_handler(commands=['gia_bitcoin', 'check_price'])
def send_current_price(message):
    price = get_bitcoin_price()
    if price is not None:  # Check if price was retrieved successfully
        bot.reply_to(message, f"Giá Bitcoin hiện tại: ${price}")
    else:
        bot.reply_to(message, "Không thể lấy giá Bitcoin. Vui lòng thử lại sau.")

# Bắt đầu bot (Render might require different handling)
bot.polling()
