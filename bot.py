import requests
import time
import threading
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Thông tin API và token
BOT_TOKEN = '8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM'
CHAT_ID = '5166662146'

# Cơ sở dữ liệu tạm (sử dụng Python Dictionary) cho việc đặt lịch
user_schedules = {}
btc_prices = []

# Tạo session với retry để lấy giá coin
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
        print(f"Lỗi khi lấy giá {coin_id}: {e}")
        return "Không thể lấy giá."

# Đặt lịch thông báo giá BTC
def dat_lich_btc(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    args = context.args  # Nhận tham số từ người dùng: ['giờ', 'ngày']
    if len(args) < 2:
        update.message.reply_text("Vui lòng nhập thời gian báo giá (VD: 12 30 để báo lúc 12:30 mỗi ngày).")
        return
    hour, minute = map(int, args)
    user_schedules[chat_id] = {"hour": hour, "minute": minute}
    update.message.reply_text(f"Đã đặt lịch báo giá BTC lúc {hour}:{minute:02d} mỗi ngày.")

# Hàm gửi thông báo giá BTC theo lịch
def schedule_notifications():
    while True:
        now = time.localtime()
        for chat_id, schedule in user_schedules.items():
            if now.tm_hour == schedule["hour"] and now.tm_min == schedule["minute"]:
                price = get_coin_price()
                context.bot.send_message(chat_id=chat_id, text=f"Giá Bitcoin hiện tại: {price} USD")
        time.sleep(60)

# Hàm vẽ biểu đồ giá BTC
def generate_btc_chart():
    if len(btc_prices) < 2:
        return "Không đủ dữ liệu để vẽ biểu đồ."
    plt.figure(figsize=(16, 9))  # FullHD resolution
    plt.plot(btc_prices, marker="o", color="blue")
    plt.title("Biểu đồ giá Bitcoin")
    plt.xlabel("Thời gian (giờ)")
    plt.ylabel("Giá (USD)")
    plt.grid()
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=300)  # Độ phân giải FullHD
    buf.seek(0)
    plt.close()
    return buf

# Theo dõi giá BTC và cập nhật vào danh sách
def track_btc_price():
    while True:
        price = get_coin_price("bitcoin")
        if price.isdigit():  # Kiểm tra giá trị hợp lệ
            btc_prices.append(int(price.replace(".", "")))
        time.sleep(3600)  # Cập nhật mỗi giờ

# Lệnh theo dõi coin khác
def coin_khac(update: Update, context: CallbackContext):
    args = context.args
    if len(args) == 0:
        update.message.reply_text("Vui lòng nhập ký hiệu coin bạn muốn theo dõi (VD: /coin_khac eth).")
        return
    coin_id = args[0].lower()
    price = get_coin_price(coin_id)
    update.message.reply_text(f"Giá {coin_id.upper()} hiện tại: {price} USD")

# Khởi tạo Updater và Dispatcher
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Thêm handler cho các lệnh
    dispatcher.add_handler(CommandHandler("datlich_btc", dat_lich_btc, pass_args=True))
    dispatcher.add_handler(CommandHandler("coin_khac", coin_khac, pass_args=True))

    # Chạy luồng để theo dõi lịch thông báo
    notification_thread = threading.Thread(target=schedule_notifications, daemon=True)
    notification_thread.start()

    # Bắt đầu bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    # Bắt đầu theo dõi giá BTC
    tracking_thread = threading.Thread(target=track_btc_price, daemon=True)
    tracking_thread.start()

    # Chạy bot
    main()
