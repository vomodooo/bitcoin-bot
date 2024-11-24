import requests
import threading
import time
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Bot Token
BOT_TOKEN = '8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM'
CHAT_ID = '5166662146'

# Lưu dữ liệu giá BTC
btc_prices = []
user_schedules = {}  # Lưu lịch báo giá

# Tạo session với retries để đảm bảo lấy giá coin ổn định
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
    except Exception as e:
        return None

# Gửi thông báo giá BTC mỗi giờ
def hourly_btc_notification(bot: Bot):
    while True:
        price = get_coin_price("bitcoin")
        if price:
            message = f"Giá Bitcoin hiện tại: {price} USD"
            bot.send_message(chat_id=CHAT_ID, text=message)
            print(message)
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

# Lệnh vẽ biểu đồ
def btc_chart(update: Update, context: CallbackContext):
    chart = generate_btc_chart()
    if chart:
        update.message.reply_photo(photo=chart, caption="Biểu đồ giá Bitcoin")
    else:
        update.message.reply_text("Không đủ dữ liệu để vẽ biểu đồ.")

# Đặt lịch báo giá BTC
def dat_lich_btc(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Vui lòng nhập giờ và phút để đặt lịch (VD: /datlich_btc 12 30).")
        return
    hour, minute = map(int, args[:2])
    user_schedules[update.message.chat_id] = {"hour": hour, "minute": minute}
    update.message.reply_text(f"Đã đặt lịch báo giá BTC lúc {hour}:{minute:02d} mỗi ngày.")

# Gửi thông báo theo lịch
def schedule_notifications(bot: Bot):
    while True:
        now = datetime.now()
        for chat_id, schedule in user_schedules.items():
            if now.hour == schedule["hour"] and now.minute == schedule["minute"]:
                price = get_coin_price("bitcoin")
                if price:
                    bot.send_message(chat_id=chat_id, text=f"Giá Bitcoin hiện tại: {price} USD")
        time.sleep(60)

# Tra cứu giá coin khác
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

# Xử lý lỗi ngoại lệ
def error_handler(update: Update, context: CallbackContext):
    print(f"Lỗi xảy ra: {context.error}")

# Khởi chạy bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    bot = updater.bot

    # Thêm lệnh
    dispatcher.add_handler(CommandHandler("btc_chart", btc_chart))
    dispatcher.add_handler(CommandHandler("datlich_btc", dat_lich_btc, pass_args=True))
    dispatcher.add_handler(CommandHandler("coin_khac", coin_khac, pass_args=True))

    # Đăng ký xử lý lỗi
    dispatcher.add_error_handler(error_handler)

    # Chạy luồng thông báo giá hàng giờ
    threading.Thread(target=hourly_btc_notification, args=(bot,), daemon=True).start()
    threading.Thread(target=schedule_notifications, args=(bot,), daemon=True).start()

    # Khởi chạy polling
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
