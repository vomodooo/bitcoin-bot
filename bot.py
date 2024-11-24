import requests
import telebot
import schedule
import time
import json
import matplotlib.pyplot as plt
import io
from datetime import datetime

# Thay thế bằng token và chat ID của bạn
bot = telebot.TeleBot('8058083423:AAEdB8bsCgLw1JeSeklG-4sqSmxO45bKRsM')
chat_id = '5166662146'

# Biến toàn cục để lưu giá Bitcoin trước đó và danh sách giá để vẽ biểu đồ
previous_price = 0
price_history = []

def get_bitcoin_price_binance():
    """Lấy giá Bitcoin hiện tại từ sàn Binance.

    Returns:
        float: Giá Bitcoin hiện tại theo USD.
    """

    url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
    response = requests.get(url)
    data = json.loads(response.text)
    return float(data['price'])

def send_price_update():
    global previous_price, price_history
    current_price = get_bitcoin_price_binance()

    # Định dạng giá với dấu chấm phân cách hàng nghìn
    formatted_price = "{:,}".format(current_price)

    # Kiểm tra sự thay đổi giá
    if abs(current_price - previous_price) > 50:  # Thay đổi 50 USD
        bot.send_message(chat_id, f"Giá Bitcoin đã thay đổi đáng kể! Giá hiện tại: ${formatted_price}")

    # Cập nhật giá trước đó và lịch sử giá
    previous_price = current_price
    price_history.append((datetime.now(), current_price))

    # Gửi thông báo cập nhật
    bot.send_message(chat_id, f"Giá Bitcoin hiện tại trên Binance: ${formatted_price}")

    # Gửi biểu đồ (mỗi 12 lần cập nhật)
    if len(price_history) % 12 == 0:
        plot_and_send_chart()

def plot_and_send_chart():
    """Vẽ biểu đồ giá Bitcoin và gửi qua Telegram."""
    times, prices = zip(*price_history)
    plt.plot(times, prices)
    plt.xlabel("Thời gian")
    plt.ylabel("Giá Bitcoin")
    plt.title("Biểu đồ giá Bitcoin")

    # Lưu biểu đồ vào buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Gửi biểu đồ
    bot.send_photo(chat_id, photo=buf)
    plt.clf()  # Xóa biểu đồ để chuẩn bị cho lần vẽ tiếp theo

# Lên lịch gửi tin nhắn mỗi giờ (mặc định)
schedule.every().hour.do(send_price_update)

# Hàm để người dùng đặt lịch cập nhật
# ... (giữ nguyên)

# Xử lý các lệnh
# ... (giữ nguyên)

# Bắt đầu bot
bot.polling()
