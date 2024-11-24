import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from datetime import datetime, time
import time as t

# Bot API token và Chat ID của bạn
BOT_API = "8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM"
CHAT_ID = "5166662146"

# Hàm lấy giá Bitcoin từ API
def get_bitcoin_price():
    url = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        price = data['bpi']['USD']['rate']
        updated_time = data['time']['updated']
        return f"💰 Giá Bitcoin: ${price}\n🕒 Cập nhật lúc: {updated_time}"
    else:
        return "Không thể lấy giá Bitcoin. Vui lòng thử lại sau."

# Hàm khởi tạo bot với nút bấm
def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("🔄 Cập nhật giá Bitcoin", callback_data='update')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Xin chào! Bấm nút để cập nhật giá Bitcoin.", reply_markup=reply_markup)

# Hàm xử lý khi người dùng nhấn nút
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'update':
        query.edit_message_text(text=get_bitcoin_price())

# Hàm tự động gửi giá Bitcoin theo giờ
def auto_update(context: CallbackContext):
    price_info = get_bitcoin_price()
    context.bot.send_message(chat_id=CHAT_ID, text=price_info)

# Cấu hình bot
def main():
    updater = Updater(BOT_API)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))

    # Cấu hình tự động gửi thông báo từ 8:00 đến 24:00
    job_queue = updater.job_queue
    for hour in range(8, 25):  # 8:00 đến 24:00
        job_queue.run_daily(auto_update, time(hour, 0, 0))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
from flask import Flask
import threading

# Flask web server (Render yêu cầu)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot Telegram đang chạy."

# Hàm khởi chạy bot Telegram
def run_bot():
    from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
    updater = Updater("BOT_API")
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))

    # Cấu hình tự động gửi thông báo từ 8:00 đến 24:00
    job_queue = updater.job_queue
    for hour in range(8, 25):  # 8:00 đến 24:00
        job_queue.run_daily(auto_update, time(hour, 0, 0))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()  # Chạy bot trong luồng riêng
    app.run(host="0.0.0.0", port=5000)       # Chạy Flask
