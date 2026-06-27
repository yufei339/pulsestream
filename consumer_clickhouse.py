import json
import time
from kafka import KafkaConsumer
from transformers import pipeline
import clickhouse_connect

print("正在加载 FinBERT 模型……")
classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
print("模型加载完成！\n")

# 连接 ClickHouse
ch = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username="default",
    password="pulse123"
)
print("已连接 ClickHouse")

# 连接 Kafka
consumer = KafkaConsumer(
    "news",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    group_id="sentiment-scorer-ch",   # 换个新组名，从头读一遍存进库
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

print("消费者启动，开始打分并写入 ClickHouse……\n")

for message in consumer:
    news = message.value
    headline = news["headline"]
    result = classifier(headline)[0]
    sentiment = result["label"]
    confidence = float(result["score"])

    # 写入 ClickHouse：一行一条
    ch.insert(
        "news_sentiment",
        [[news["id"], headline, sentiment, confidence]],
        column_names=["news_id", "headline", "sentiment", "confidence"]
    )

    now = time.strftime("%H:%M:%S")
    print(f"[{now}] 已存库 ({sentiment} {confidence:.2f}) {headline}")