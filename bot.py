import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Thông tin API Telegram
BOT_TOKEN = "8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM"
CHAT_ID = "5166662146"

# Hàm lấy giá BTC từ Binance
def get_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    try:
        response = requests.get(url, timeout=10)  # Thêm timeout để tránh treo
        response.raise_for_status()  # Gây lỗi nếu trạng thái HTTP không phải 200
        data = response.json()
        price = float(data['price'])
        return f"{price:,.2f}".replace(",", ".")  # Định dạng giá
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi kết nối Binance API: {e}")
        return "Không thể lấy giá BTC."

# Lệnh /gia_btc
def gia_btc(update: Update, context: CallbackContext):
    price = get_btc_price()
    update.message.reply_text(f"Giá Bitcoin hiện tại: {price} USD")

# Nút "Cập nhật giá BTC"
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    price = get_btc_price()
    query.edit_message_text(f"Giá Bitcoin hiện tại: {price} USD")

# Lệnh /start
def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Cập nhật giá BTC", callback_data='update')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Chọn một tùy chọn:", reply_markup=reply_markup)

# Khởi chạy bot
def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Đăng ký các lệnh
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("gia_btc", gia_btc))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    # Chạy bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

import threading
from flask import Flask

# Giữ ứng dụng chạy để Render nhận diện
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()  # Chạy Flask song song với bot
    main()
