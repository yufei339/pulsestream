import requests
import time
import json
from kafka import KafkaProducer

API_KEY = "d8o91u9r01qrbffk9h90d8o91u9r01qrbffk9h9g"

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8")
)

seen_ids = set()

def fetch_and_send():
    url = f"https://finnhub.io/api/v1/news?category=general&token={API_KEY}"
    news_list = requests.get(url).json()

    if not isinstance(news_list, list):
        print("API 返回异常，可能是请求过于频繁了。")
        return

    new_count = 0
    for news in news_list:
        news_id = news["id"]
        if news_id in seen_ids:
            continue
        seen_ids.add(news_id)
        new_count += 1
        record = {"id": news_id, "headline": news["headline"], "datetime": news["datetime"]}
        producer.send("news", value=record)   # 发到 Kafka，不再写文件

    producer.flush()
    now = time.strftime("%H:%M:%S")
    print(f"[{now}] 生产者：发送 {new_count} 条到 Kafka")

print("生产者启动（Kafka 版），每 60 秒拉一次……")
try:
    while True:
        fetch_and_send()
        time.sleep(60)
except KeyboardInterrupt:
    print("\n生产者已停止。")
    producer.close()