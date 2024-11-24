import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
from time import sleep

# Thay thế bằng token và chat ID của bạn
bot_token = '8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM'
chat_id = 5166662146

def get_btc_price():
    response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
    data = response.json()
    return data['price']

def send_message(text):
    bot.send_message(chat_id=chat_id, text=text)

def get_price_command(update, context):
    btc_price = get_btc_price()
    message = f"Giá Bitcoin hiện tại: ${btc_price}"
    update.message.reply_text(message)

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    btc_price = get_btc_price()
    message = f"Giá Bitcoin hiện tại: ${btc_price}"
    query.edit_message_text(text=message)

def main():
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("gia_btc", get_price_command))

    # Tạo bàn phím inline
    keyboard = [[telegram.InlineKeyboardButton("Cập nhật giá BTC", callback_data='update_price')]]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    # Gửi tin nhắn với bàn phím
    bot.send_message(chat_id=chat_id, text="Nhấn nút để cập nhật giá Bitcoin:", reply_markup=reply_markup)

    # Xử lý các callback từ nút
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
