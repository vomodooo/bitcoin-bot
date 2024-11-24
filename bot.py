import os
import requests
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, Dispatcher

# Thông tin Bot Telegram
BOT_TOKEN = "8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM"
WEBHOOK_URL = "https://bitcoin-bot.onrender.com"  # Thay bằng tên app Render

# Hàm lấy giá BTC từ CoinGecko
def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        print("Đang gửi yêu cầu tới CoinGecko API...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"Dữ liệu trả về từ CoinGecko: {data}")  # Ghi log dữ liệu trả về
        price = int(data['bitcoin']['usd'])  # Lấy giá Bitcoin
        return f"{price:,}".replace(",", ".")  # Định dạng giá trị
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi kết nối CoinGecko API: {e}")
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

# Khởi tạo Flask App và Webhook
def main():
    # Tạo Flask app
    app = Flask(__name__)

    # Tạo đối tượng Updater và Dispatcher
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Đăng ký các handler
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("gia_btc", gia_btc))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    # Định nghĩa route Flask
    @app.route("/", methods=["GET"])
    def index():
        return "Bot is running!", 200

    @app.route(f"/{BOT_TOKEN}", methods=["POST"])
    def webhook():
        update = Update.de_json(request.get_json(force=True), updater.bot)
        dispatcher.process_update(update)
        return "OK", 200

    # Đặt Webhook
    updater.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")
    print(f"Webhook set to {WEBHOOK_URL}/{BOT_TOKEN}")

    # Chạy Flask
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
