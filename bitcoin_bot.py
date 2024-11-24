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
