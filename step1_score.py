import requests
from transformers import pipeline

API_KEY = "d8o91u9r01qrbffk9h90d8o91u9r01qrbffk9h9g"

print("正在加载 FinBERT 模型……第一次会下载，请耐心等待")
classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
print("模型加载完成！\n")

print("正在拉取财经新闻……")
url = f"https://finnhub.io/api/v1/news?category=general&token={API_KEY}"
response = requests.get(url)
news_list = response.json()


news_list = news_list[:10]
print(f"拿到 {len(news_list)} 条新闻\n")
print("=" * 60)

for i, news in enumerate(news_list, 1):
    headline = news["headline"]
    result = classifier(headline)[0]
    sentiment = result["label"]      # positive / negative / neutral
    confidence = result["score"]     # 置信度 0~1

    print(f"\n【{i}】{headline}")
    print(f"     情感: {sentiment}  |  置信度: {confidence:.2f}")

print("\n" + "=" * 60)
print("完成！")