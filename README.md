# Pulsestream

A simple Python-based news sentiment pipeline that fetches financial news, writes a local JSONL queue, and performs sentiment analysis using the FinBERT model.

## Project structure

- `producer.py`
  - Fetches news from Finnhub API every 60 seconds
  - Writes unique news items to `news_queue.jsonl`

- `consumer.py`
  - Reads newly appended items from `news_queue.jsonl`
  - Runs sentiment analysis on the headline using `ProsusAI/finbert`

- `step1_score.py`
  - Fetches the latest news once from Finnhub
  - Scores the first 10 headlines with FinBERT

- `step2_score.py`
  - Continuously fetches news every 10 seconds
  - Scores new headlines with FinBERT and prints results

- `news_queue.jsonl`
  - Local append-only queue file storing news records

- `docker-compose.yml`
  - Defines a Kafka service (`apache/kafka:3.9.0`)
  - Note: current Python scripts do not use Kafka directly

## Requirements

- Python 3.10+ recommended
- `requests`
- `transformers`

## Installation

1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install requests transformers
```

## Usage

### 1. Run the producer

The producer fetches news and appends it to `news_queue.jsonl`.

```powershell
python producer.py
```

### 2. Run the consumer

The consumer monitors the queue file and prints sentiment analysis results.

```powershell
python consumer.py
```

### 3. Run one-off scoring

- `step1_score.py` fetches the latest 10 headlines and scores them once.
- `step2_score.py` continuously polls Finnhub and scores new headlines every 10 seconds.

```powershell
python step1_score.py
python step2_score.py
```

## Configuration

- The Finnhub API key is hard-coded in `producer.py`, `step1_score.py`, and `step2_score.py`.
- Replace `API_KEY` with your own Finnhub API key before running.

## Notes

- The first run of the `transformers` pipeline will download the `ProsusAI/finbert` model.
- If you want to use Kafka later, the `docker-compose.yml` file defines a local Kafka broker on port `9092`.
- `news_queue.jsonl` is a newline-delimited JSON file, one record per line.

## License

No license specified.
