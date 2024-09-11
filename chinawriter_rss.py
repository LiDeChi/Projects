import requests
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
import datetime
import schedule
import time
import os
from telegram import Bot
from dotenv import load_dotenv
import logging

# Telegram Bot Token和频道ID
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_articles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []
    for article in soup.select('.news-list li'):  # 假设文章列表在class为news-list的ul中
        title = article.select_one('a').text.strip()
        link = 'https://www.chinawriter.com.cn' + article.select_one('a')['href']
        date = article.select_one('.date').text.strip()  # 假设日期在class为date的元素中
        articles.append({'title': title, 'link': link, 'date': date})
    return articles

def generate_rss(articles, feed_title, feed_link, filename):
    feed = Rss201rev2Feed(
        title=feed_title,
        link=feed_link,
        description=f"RSS feed for {feed_title}",
        language="zh-CN",
    )

    for article in articles:
        feed.add_item(
            title=article['title'],
            link=article['link'],
            pubdate=datetime.datetime.strptime(article['date'], '%Y-%m-%d'),
            description=article['title']
        )

    with open(filename, 'w', encoding='utf-8') as f:
        feed.write(f, 'utf-8')

def send_to_telegram(article):
    try:
        token = TELEGRAM_BOT_TOKEN
        chat_id = TELEGRAM_CHANNEL_ID
        text = f"{article['title']}\n\n{article['link']}"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.get(url, params=params)
        result = response.json()
        if result.get("ok"):
            logging.info(f"成功发送消息到 Telegram: {article['title']}")
        else:
            logging.error(f"发送消息到 Telegram 失败: {result}")
    except Exception as e:
        logging.error(f"发送消息到 Telegram 时出错: {str(e)}")

def update_rss():
    sections = [
        {'url': 'https://www.chinawriter.com.cn/news/', 'title': '新闻动态', 'filename': 'news.xml'},
        {'url': 'https://www.chinawriter.com.cn/pinglun/', 'title': '评论争鸣', 'filename': 'comments.xml'},
        {'url': 'https://www.chinawriter.com.cn/zuopin/', 'title': '新作品', 'filename': 'new_works.xml'},
        {'url': 'https://www.chinawriter.com.cn/fangtan/', 'title': '访谈', 'filename': 'interviews.xml'},
        {'url': 'https://www.chinawriter.com.cn/wenshi/', 'title': '文史', 'filename': 'literature_history.xml'},
        {'url': 'https://www.chinawriter.com.cn/yishu/', 'title': '艺术', 'filename': 'arts.xml'},
        {'url': 'https://www.chinawriter.com.cn/wlwx/', 'title': '网络文学', 'filename': 'online_literature.xml'},
        {'url': 'https://www.chinawriter.com.cn/etxx/', 'title': '儿童文学', 'filename': 'children_literature.xml'},
        {'url': 'https://www.chinawriter.com.cn/sjwt/', 'title': '世界文坛', 'filename': 'world_literature.xml'},
    ]

    new_articles_count = 0
    all_articles = []

    for section in sections:
        try:
            articles = fetch_articles(section['url'])
            generate_rss(articles, section['title'], section['url'], section['filename'])
            
            # 收所有文章
            all_articles.extend(articles[:5])
            new_articles_count += len(articles[:5])
            logging.info(f"成功处理 {section['title']}, 获取到 {len(articles[:5])} 篇文章")
        except Exception as e:
            logging.error(f"处理 {section['title']} 时出错: {str(e)}")
    
    # 发送测试消息
    send_to_telegram({'title': '测试消息', 'link': 'https://www.chinawriter.com.cn'})

    # 发送消息到Telegram
    if new_articles_count > 0:
        for article in all_articles:
            send_to_telegram(article)
    else:
        send_to_telegram({'title': '无新更新', 'link': 'https://www.chinawriter.com.cn'})
    
    logging.info(f"RSS更新完成并尝试发送到Telegram: {datetime.datetime.now()}")

if __name__ == "__main__":
    logging.info("脚本开始运行")
    
    # 检查环境变量
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        logging.error("Telegram Bot Token 或 Channel ID 未设置")
        exit(1)

    # 打印环境变量（注意不要在生产环境中这样做）
    logging.info(f"TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:5]}...")
    logging.info(f"TELEGRAM_CHANNEL_ID: {TELEGRAM_CHANNEL_ID}")

    # 立即运行一次
    update_rss()

    # 设置定时任务
    schedule.every(1).hour.do(update_rss)

    # 保持脚本运行，每10秒检查一次
    while True:
        schedule.run_pending()
        logging.info(f"检查更新: {datetime.datetime.now()}")
        time.sleep(300)