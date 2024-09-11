import time
import hashlib
from urllib.request import urlopen, Request
from telegram.ext import Updater

# Telegram bot设置
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

def send_telegram_message(message):
    updater = Updater(TOKEN, use_context=True)
    updater.bot.send_message(chat_id=CHAT_ID, text=message)

# 设置要监控的URL
url = Request('https://www.geeksforgeeks.org', headers={'User-Agent': 'Mozilla/5.0'})

# 获取初始网页内容的哈希值
response = urlopen(url).read()
current_hash = hashlib.sha224(response).hexdigest()

print("开始监控...")
send_telegram_message("开始监控网站变化...")

while True:
    try:
        # 每30秒检查一次
        time.sleep(30)
        response = urlopen(url).read()
        new_hash = hashlib.sha224(response).hexdigest()

        if new_hash != current_hash:
            print("检测到网站变化!")
            send_telegram_message("检测到网站变化!")
            current_hash = new_hash

    except Exception as e:
        print(f"发生错误: {str(e)}")
        send_telegram_message(f"监控过程中发生错误: {str(e)}")

    time.sleep(30)