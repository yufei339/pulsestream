import requests
import time
from transformers import pipeline

# ====== 填你的 Finnhub API Key ======
API_KEY = "d8o91u9r01qrbffk9h90d8o91u9r01qrbffk9h9g"
# ====================================

print("正在加载 FinBERT 模型……")
classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
print("模型加载完成！开始持续监控新闻流……\n")

# 记录已经处理过的新闻，避免重复打分
seen_ids = set()

def fetch_and_score():
    url = f"https://finnhub.io/api/v1/news?category=general&token={API_KEY}"
    news_list = requests.get(url).json()

    new_count = 0
    for news in news_list:
        news_id = news["id"]          # 每条新闻的唯一ID
        if news_id in seen_ids:
            continue                  # 见过的跳过——这就是"去重"
        seen_ids.add(news_id)
        new_count += 1

        headline = news["headline"]
        result = classifier(headline)[0]
        sentiment = result["label"]
        confidence = result["score"]

        # 打上时间戳，让你看到"流"的实时感
        now = time.strftime("%H:%M:%S")
        print(f"[{now}] ({sentiment:8s} {confidence:.2f}) {headline}")

    if new_count == 0:
        now = time.strftime("%H:%M:%S")
        print(f"[{now}] —— 暂无新新闻 ——")

# 主循环：每 10 秒拉一次
try:
    while True:
        fetch_and_score()
        time.sleep(10)
except KeyboardInterrupt:
    print("\n已停止监控。")