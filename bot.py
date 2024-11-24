import requests
import threading
import time
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Dispatcher
from flask import Flask, request

# Bot Token
BOT_TOKEN = '8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM'
WEBHOOK_URL = "https://bitcoin-bot.onrender.com"
CHAT_ID = '5166662146'

# Flask App
app = Flask(__name__)
bot = Bot(BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=4)

btc_prices = []
user_schedules = {}

# Tạo session ổn định
def create_session_with_retries():
    session = requests.Session()
    retries = requests.adapters.Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
    return session

session = create_session_with_retries()

# Lấy giá BTC từ API CoinGecko
def get_coin_price(coin_id="bitcoin"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = int(data[coin_id]['usd'])
        return f"{price:,}".replace(",", ".")
    except Exception:
        return None

# Gửi thông báo giá BTC mỗi giờ
def hourly_btc_notification():
    while True:
        price = get_coin_price("bitcoin")
        if price:
            message = f"Giá Bitcoin hiện tại: {price} USD"
            bot.send_message(chat_id=CHAT_ID, text=message)
            btc_prices.append(int(price.replace('.', '')))
        time.sleep(3600)

# Vẽ biểu đồ giá BTC
def generate_btc_chart():
    if len(btc_prices) < 2:
        return None
    plt.figure(figsize=(16, 9))
    plt.plot(btc_prices, marker="o", color="blue")
    plt.title("Biểu đồ giá Bitcoin")
    plt.xlabel("Thời gian (giờ)")
    plt.ylabel("Giá (USD)")
    plt.grid()
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=300)
    buf.seek(0)
    plt.close()
    return buf

def btc_chart(update: Update, context: CallbackContext):
    chart = generate_btc_chart()
    if chart:
        update.message.reply_photo(photo=chart, caption="Biểu đồ giá Bitcoin")
    else:
        update.message.reply_text("Không đủ dữ liệu để vẽ biểu đồ.")

def dat_lich_btc(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Vui lòng nhập giờ và phút để đặt lịch (VD: /datlich_btc 12 30).")
        return
    hour, minute = map(int, args[:2])
    user_schedules[update.message.chat_id] = {"hour": hour, "minute": minute}
    update.message.reply_text(f"Đã đặt lịch báo giá BTC lúc {hour}:{minute:02d} mỗi ngày.")

def schedule_notifications():
    while True:
        now = datetime.now()
        for chat_id, schedule in user_schedules.items():
            if now.hour == schedule["hour"] and now.minute == schedule["minute"]:
                price = get_coin_price("bitcoin")
                if price:
                    bot.send_message(chat_id=chat_id, text=f"Giá Bitcoin hiện tại: {price} USD")
        time.sleep(60)

def coin_khac(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        update.message.reply_text("Vui lòng nhập ký hiệu coin cần tra cứu (VD: /coin_khac eth).")
        return
    coin_id = args[0].lower()
    price = get_coin_price(coin_id)
    if price:
        update.message.reply_text(f"Giá {coin_id.upper()} hiện tại: {price} USD")
    else:
        update.message.reply_text(f"Không thể lấy giá của {coin_id.upper()}.")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Bot đã sẵn sàng! Hãy sử dụng các lệnh như /btc_chart, /datlich_btc, /coin_khac.")

def webhook_handler():
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, bot)
    dispatcher.process_update(update)
    return "ok"

# Đăng ký webhook và lệnh
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    return webhook_handler()

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

if __name__ == "__main__":
    # Đăng ký lệnh
    dispatcher.add_handler(CommandHandler("btc_chart", btc_chart))
    dispatcher.add_handler(CommandHandler("datlich_btc", dat_lich_btc, pass_args=True))
    dispatcher.add_handler(CommandHandler("coin_khac", coin_khac, pass_args=True))
    dispatcher.add_handler(CommandHandler("start", start))

    # Đặt webhook
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    # Chạy các tác vụ nền
    threading.Thread(target=hourly_btc_notification, daemon=True).start()
    threading.Thread(target=schedule_notifications, daemon=True).start()

    # Chạy Flask server
    app.run(host="0.0.0.0", port=5000)
