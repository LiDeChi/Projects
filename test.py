import os
os.system('pip install requests')
import requests
from dotenv import load_dotenv

load_dotenv()

def send_message(text):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHANNEL_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"
    response = requests.get(url)
    return response.json()

# 测试发送消息
result = send_message("Hello from Python!")
print(result)