import requests
from bs4 import BeautifulSoup
import datetime
import os
from dotenv import load_dotenv
import logging
import json
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 加载环境变量
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_tgstat_info(url):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://tgstat.com/',
        'X-Requested-With': 'XMLHttpRequest',
        # 添加任何其他必要的头部
    }
    
    try:
        # 使用您在开发者工具中找到的实际API URL
        api_url = 'https://bam.eu01.nr-data.net/1/NRJS-7149647f3b067b4123f?a=319587756&v=1.265.1&to=MhBSZQoZWBJYUkNaXQtac0QLDFkMFlBHQx8DB19fDB1YBRZcVlpcShxeVR0A&rst=11704&ck=0&s=d462bef89f875f18&ref=https://tgstat.com/&ptid=68a98d531cd1701e&af=err,spa,xhr,stn,ins&ap=150&be=7922&fe=3291&dc=2584&at=HldRE0IDSxw%3D&fsh=0&perf=%7B%22timing%22:%7B%22of%22:1726105823044,%22n%22:0,%22u%22:7965,%22ue%22:7965,%22f%22:369,%22dn%22:369,%22dne%22:369,%22c%22:369,%22s%22:369,%22ce%22:369,%22rq%22:6890,%22rp%22:7922,%22rpe%22:7950,%22di%22:10436,%22ds%22:10437,%22de%22:10506,%22dc%22:11033,%22l%22:11033,%22le%22:11214%7D,%22navigation%22:%7B%22ty%22:1%7D%7D&timestamp=1726105835273'  # 这只是一个示例，请使用实际的URL
        
        # 如果需要POST请求，使用以下代码：
        response = session.post(api_url, headers=headers, json=payload, timeout=30)
        # 如果是GET请求，使用以下代码：
        # response = session.get(api_url, headers=headers, timeout=30)
        
        response.raise_for_status()
        logging.info(f"Successfully fetched data from {api_url}")
        
        data = response.json()
        logging.info(f"API response: {json.dumps(data, indent=2)}")
        
        countries = []
        # 根据实际的JSON结构调整以下代码
        for country_data in data.get('items', []):
            countries.append({
                'name': country_data.get('name'),
                'channels': country_data.get('channels_count'),
                'groups': country_data.get('groups_count'),
                'audience': country_data.get('audience')
            })
        
        if not countries:
            logging.warning("No country data found in the API response")
        else:
            logging.info(f"Found data for {len(countries)} countries")
            for country in countries[:3]:  # 只打印前3个国家的数据
                logging.info(f"Country data: {country}")
        
        return countries
    except requests.exceptions.RequestException as e:
        logging.error(f"获取 TGStat 信息时出错: {str(e)}")
        return []

def send_to_telegram(info):
    try:
        text = "TGStat 最新统计信息:\n\n"
        for country in info:
            text += f"{country['name']}:\n"
            text += f"频道数: {country['channels']}\n"
            text += f"群组数: {country['groups']}\n"
            text += f"总受众: {country['audience']}\n\n"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.get(url, params=params)
        result = response.json()
        if result.get("ok"):
            logging.info("成功发送 TGStat 信息到 Telegram")
        else:
            logging.error(f"发送消息到 Telegram 失败: {result}")
    except Exception as e:
        logging.error(f"发送消息到 Telegram 时出错: {str(e)}")

def load_last_update():
    try:
        with open('last_update.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_last_update(info):
    with open('last_update.json', 'w') as f:
        json.dump(info, f)

def update_tgstat_info():
    url = 'https://tgstat.com/'
    info = fetch_tgstat_info(url)
    
    if not info:
        logging.warning("未获取到 TGStat 信息")
        return
    
    last_update = load_last_update()
    if info != last_update:
        send_to_telegram(info)
        save_last_update(info)
        logging.info("TGStat 信息已更新并发送到 Telegram")
    else:
        logging.info("TGStat 信息未发生变化")

if __name__ == "__main__":
    logging.info("脚本开始运行")
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        logging.error("Telegram Bot Token 或 Channel ID 未设置")
        exit(1)

    logging.info(f"TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:5]}...")
    logging.info(f"TELEGRAM_CHANNEL_ID: {TELEGRAM_CHANNEL_ID}")

    update_tgstat_info()
    logging.info(f"TGStat 信息更新完成: {datetime.datetime.now()}")