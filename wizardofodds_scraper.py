import requests
from bs4 import BeautifulSoup
import datetime
import os
from dotenv import load_dotenv
import logging
import json
import time

# 加载环境变量
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_wizardofodds_articles(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = []
        for article in soup.find_all('article', class_='post'):
            title = article.find('h2', class_='entry-title').text.strip()
            link = article.find('a', class_='entry-title-link')['href']
            date = article.find('time', class_='entry-time')['datetime']
            
            articles.append({
                'title': title,
                'link': link,
                'date': date
            })
        
        if not articles:
            logging.warning(f"未在 {url} 找到任何文章")
        else:
            logging.info(f"找到 {len(articles)} 篇文章")
            for article in articles[:5]:  # 只打印前5篇文章的信息
                logging.info(f"Article: {article}")
        
        return articles
    except Exception as e:
        logging.error(f"获取 Wizard of Odds 文章时出错: {str(e)}")
        return []

def send_to_telegram(article):
    try:
        text = f"*{article['title']}*\n\n{article['link']}\n\n发布日期: {article['date']}"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.get(url, params=params)
        result = response.json()
        if result.get("ok"):
            logging.info(f"成功发送文章到 Telegram: {article['title']}")
        else:
            logging.error(f"发送消息到 Telegram 失败: {result}")
    except Exception as e:
        logging.error(f"发送消息到 Telegram 时出错: {str(e)}")

def load_sent_articles():
    try:
        with open('sent_wizardofodds_articles.json', 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_sent_articles(sent_articles):
    with open('sent_wizardofodds_articles.json', 'w') as f:
        json.dump(list(sent_articles), f)

def update_articles():
    sent_articles = load_sent_articles()
    new_sent_articles = set()

    url = 'https://wizardofodds.com/blog/'  # Wizard of Odds 博客页面
    articles = fetch_wizardofodds_articles(url)
    
    for article in articles:
        if article['link'] not in sent_articles:
            send_to_telegram(article)
            new_sent_articles.add(article['link'])
            time.sleep(5)  # 添加延迟以避免触发 Telegram 的速率限制
    
    logging.info(f"获取到 {len(articles)} 篇文章，发送了 {len(new_sent_articles)} 篇新文章到 Telegram")

    sent_articles.update(new_sent_articles)
    save_sent_articles(sent_articles)

if __name__ == "__main__":
    logging.info("脚本开始运行")
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        logging.error("Telegram Bot Token 或 Channel ID 未设置")
        exit(1)

    logging.info(f"TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:5]}...")
    logging.info(f"TELEGRAM_CHANNEL_ID: {TELEGRAM_CHANNEL_ID}")

    update_articles()
    logging.info(f"Wizard of Odds 文章更新完成: {datetime.datetime.now()}")