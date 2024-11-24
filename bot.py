import telegram
from telegram.ext import Updater, CommandHandler
import requests

# Thay thế các thông tin sau bằng thông tin của bạn
BOT_TOKEN = '8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM'
CHAT_ID = 5166662146

def get_bitcoin_price():
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
    response = requests.get(url)
    data = response.json()
    return float(data['price'])

def start(update, context):
    context.bot.send_message(chat_id=CHAT_ID, text="Bot đã sẵn sàng!")

def gia_btc(update, context):
    price = get_bitcoin_price()
    context.bot.send_message(chat_id=CHAT_ID, text=f"Giá Bitcoin hiện tại: ${price}")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('gia_btc', gia_btc))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
