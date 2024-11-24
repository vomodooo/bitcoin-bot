import requests
import threading
import time
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext, Updater, Dispatcher
from flask import Flask, request

# Thông tin Bot
BOT_TOKEN = '8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM'
WEBHOOK_URL = "https://bitcoin-bot.onrender.com"
CHAT_ID = '5166662146'

# Flask app và bot setup
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

# Lấy giá coin từ API CoinGecko
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

# Xử lý nút bấm
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == "update_btc":
        price = get_coin_price("bitcoin")
        if price:
            query.edit_message_text(text=f"Giá Bitcoin hiện tại: {price} USD")
        else:
            query.edit_message_text(text="Không thể lấy giá Bitcoin.")
    elif data == "btc_chart":
        chart = generate_btc_chart()
        if chart:
            query.message.reply_photo(photo=chart, caption="Biểu đồ giá Bitcoin")
        else:
            query.edit_message_text(text="Không đủ dữ liệu để vẽ biểu đồ.")
    elif data == "schedule_btc":
        query.edit_message_text(text="Vui lòng sử dụng lệnh /datlich_btc [giờ phút] để đặt lịch.")
    elif data == "other_coin":
        query.edit_message_text(text="Vui lòng sử dụng lệnh /coin_khac [ký hiệu coin].")

# Lệnh start
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Cập nhật giá BTC", callback_data="update_btc")],
        [InlineKeyboardButton("Biểu đồ giá BTC", callback_data="btc_chart")],
        [InlineKeyboardButton("Đặt lịch báo", callback_data="schedule_btc")],
        [InlineKeyboardButton("Theo dõi đồng khác", callback_data="other_coin")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Chọn một tính năng:", reply_markup=reply_markup)

# Đặt lịch báo giá BTC
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

# Tìm giá coin khác
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

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

if __name__ == "__main__":
    # Đăng ký lệnh
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("datlich_btc", dat_lich_btc, pass_args=True))
    dispatcher.add_handler(CommandHandler("coin_khac", coin_khac, pass_args=True))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    # Đặt webhook
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    # Chạy tác vụ nền
    threading.Thread(target=hourly_btc_notification, daemon=True).start()
    threading.Thread(target=schedule_notifications, daemon=True).start()

    # Chạy Flask server
    app.run(host="0.0.0.0", port=5000)
