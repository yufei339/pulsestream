import json
import time
from kafka import KafkaConsumer
from transformers import pipeline
import clickhouse_connect

# ===== 关键词 → 股票代码 词典 =====
TICKER_DICT = {
    "apple": "AAPL", "tesla": "TSLA", "microsoft": "MSFT",
    "nvidia": "NVDA", "amazon": "AMZN", "google": "GOOGL",
    "alphabet": "GOOGL", "meta": "META", "facebook": "META",
    "netflix": "NFLX", "fedex": "FDX", "salesforce": "CRM",
    "goldman": "GS", "boeing": "BA", "ford": "F",
}

def find_tickers(headline):
    headline_lower = headline.lower()
    found = []
    for keyword, ticker in TICKER_DICT.items():
        if keyword in headline_lower and ticker not in found:
            found.append(ticker)
    return found

print("正在加载 FinBERT 模型……")
classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
print("模型加载完成！\n")

ch = clickhouse_connect.get_client(
    host="localhost", port=8123,
    username="default", password="pulse123"
)
print("已连接 ClickHouse")

consumer = KafkaConsumer(
    "news",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    group_id="sentiment-smart",   # 新组名，重新读一遍
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

print("消费者启动，开始处理……\n")

for message in consumer:
    news = message.value
    headline = news["headline"]

    # 1. 实体识别：这条新闻关联哪些股票？
    tickers = find_tickers(headline)
    tickers_str = ",".join(tickers)

    # 2. 情感打分
    result = classifier(headline)[0]
    sentiment = result["label"]
    confidence = float(result["score"])

    # 3. 存库（多了 tickers 一列）
    ch.insert(
        "news_sentiment",
        [[news["id"], headline, sentiment, confidence, tickers_str]],
        column_names=["news_id", "headline", "sentiment", "confidence", "tickers"]
    )

    now = time.strftime("%H:%M:%S")
    tag = tickers_str if tickers_str else "—无关—"
    print(f"[{now}] [{tag:8s}] ({sentiment} {confidence:.2f}) {headline}")