import requests
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
import datetime
import schedule
import time
import os
from telegram import Bot
from dotenv import load_dotenv

# Telegram Bot Token和频道ID
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def fetch_articles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []
    for article in soup.select('.news-list li'):  # 假设文章列表在class为news-list的ul中
        title = article.select_one('a').text.strip()
        link = 'https://www.zhihu.com' + article.select_one('a')['href']
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
    message = f"*{article['title']}*\n\n{article['link']}"
    bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode='Markdown')

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

    for section in sections:
        try:
            articles = fetch_articles(section['url'])
            generate_rss(articles, section['title'], section['url'], section['filename'])
            
            # 发送最新的5篇文章到Telegram
            for article in articles[:5]:
                send_to_telegram(article)
        except Exception as e:
            print(f"处理 {section['title']} 时出错: {str(e)}")
    
    print(f"RSS更新完成并发送到Telegram: {datetime.datetime.now()}")

if __name__ == "__main__":
    # 立即运行一次
    update_rss()

    # 设置定时任务
    schedule.every(1).hour.do(update_rss)

    # 保持脚本运行
    while True:
        schedule.run_pending()
        time.sleep(1)