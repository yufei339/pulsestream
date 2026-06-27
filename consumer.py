import time
import json
import os
from transformers import pipeline

QUEUE_FILE = "news_queue.jsonl"

print("正在加载 FinBERT 模型……")
classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
print("消费者启动，开始监控队列文件……\n")

last_position = 0   # 记住上次读到文件哪个位置

def consume():
    global last_position

    if not os.path.exists(QUEUE_FILE):
        return   # 文件还没被生产者创建，等下一轮

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        f.seek(last_position)      # 跳到上次读到的位置
        new_lines = f.readlines()  # 只读新增的行
        last_position = f.tell()   # 更新位置

    for line in new_lines:
        line = line.strip()
        if not line:
            continue
        news = json.loads(line)
        headline = news["headline"]
        result = classifier(headline)[0]

        now = time.strftime("%H:%M:%S")
        print(f"[{now}] ({result['label']:8s} {result['score']:.2f}) {headline}")

try:
    while True:
        consume()
        time.sleep(5)   # 每 5 秒检查一次队列有没有新内容
except KeyboardInterrupt:
    print("\n消费者已停止。")