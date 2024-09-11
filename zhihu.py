import os
import requests
from bs4 import BeautifulSoup
import time
from telegram import Bot
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 从 .env 文件获取 Telegram 配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def fetch_zhihu_updates():
    url = 'https://www.zhihu.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    updates = []
    for item in soup.select('.ContentItem'):
        title = item.select_one('.ContentItem-title').text.strip()
        link = item.select_one('a')['href']
        if not link.startswith('http'):
            link = 'https://www.zhihu.com' + link
        updates.append({'title': title, 'link': link})
    
    return updates

def send_to_telegram(update):
    message = f"*{update['title']}*\n\n{update['link']}"
    bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode='Markdown')

def main():
    last_updates = set()
    while True:
        try:
            current_updates = fetch_zhihu_updates()
            for update in current_updates:
                update_key = f"{update['title']}|{update['link']}"
                if update_key not in last_updates:
                    send_to_telegram(update)
                    last_updates.add(update_key)
            
            # 保持最近100条更新
            if len(last_updates) > 100:
                last_updates = set(list(last_updates)[-100:])
            
            time.sleep(10)  # 每5分钟检查一次
        except Exception as e:
            print(f"发生错误: {str(e)}")
            time.sleep(10)  # 发生错误时等待1分钟后重试

if __name__ == "__main__":
    main()