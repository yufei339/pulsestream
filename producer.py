import requests
import time
import json

API_KEY = "d8o91u9r01qrbffk9h90d8o91u9r01qrbffk9h9g"
QUEUE_FILE = "news_queue.jsonl"

seen_ids = set()

def fetch_and_write():
    url = f"https://finnhub.io/api/v1/news?category=general&token={API_KEY}"
    news_list = requests.get(url).json()

    if not isinstance(news_list, list):
        print("API 返回异常，可能是请求过于频繁了。")
        return
    new_count = 0
    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        for news in news_list:
            news_id = news["id"]
            if news_id in seen_ids:
                continue
            seen_ids.add(news_id)
            new_count += 1

            record ={"id": news_id, "headline": news["headline"], "datetime": news["datetime"]}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    now = time.strftime("%H:%M:%S")
    print(f"[{now}] 生产者：写入 {new_count} 条新新闻")

print("生产者启动，每 60 秒拉一次新闻……")
try:
    while True:
        fetch_and_write()
        time.sleep(60)
except KeyboardInterrupt:
    print("\n生产者已停止。")