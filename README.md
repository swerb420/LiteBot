# LiteBot

This repository contains the code for the lightweight trading bot found in `geminiBOT_LiteModev2`. The project is intended to run on low-cost VPS instances using Docker Compose.

## Prerequisites

- **Docker** and **Docker Compose** installed on the host machine.
- Basic familiarity with creating environment variable files (`.env`).

All Python packages needed by the bot are listed in the
`requirements.txt` file at the repository root. The Dockerfile uses this
file during the build stage, so keep it up to date when adding new
dependencies.
The bot indirectly depends on `pydantic` 2.x via the `web3` package. The
project itself does not use FastAPI, so you can ignore any warnings about
FastAPI requiring an older `pydantic` version.

## Environment Variables

Create a `.env` file in `geminiBOT_LiteModev2` with the following variables:

```
DATABASE_URL=<postgres connection string>
DB_POOL_MIN_SIZE=1
DB_POOL_MAX_SIZE=5
TELEGRAM_BOT_TOKEN=<telegram token>
TELEGRAM_CHAT_ID=<telegram chat id>
ALCHEMY_WS_URL=<alchemy websocket url>
GMX_VAULT_ADDRESS=<gmx vault address>
RISK_CAPITAL=10000
RISK_FRACTION=0.02
ENABLE_MOBILEBERT=1
BERT_MODEL_NAME=textattack/mobilebert-uncased-SST-2
METRICS_PORT=8000
ENABLE_METRICS_SERVER=0
```

Set `ENABLE_METRICS_SERVER=1` to start a Prometheus metrics endpoint on
`METRICS_PORT` (default `8000`). Metrics can then be scraped from
`http://localhost:8000/metrics`.

Adjust the values to match your setup.

## Starting the Services

Run the containers from within `geminiBOT_LiteModev2`:

```bash
cd geminiBOT_LiteModev2
docker-compose up --build
```

Compose limits the trading bot container to about **1.5&nbsp;GB** of memory, so a VPS with at least 2&nbsp;GB of RAM is recommended.

The requirements include `transformers` and `scikit-learn`, which can consume
hundreds of megabytes of RAM when loaded. Loading the MobileBERT model for
sentiment analysis alone adds roughly 150&nbsp;MB. Ensure your VPS has enough
free memory or consider lighter alternatives if those features are not needed.
Set `ENABLE_MOBILEBERT=0` in your `.env` file to disable the model entirely or change
`BERT_MODEL_NAME` to swap in a different transformer.

## VPS Notes

The bot is designed for low-memory environments. Make sure your VPS provides enough RAM for Docker and the database. Running within the memory limit helps keep costs low while still supporting basic whale-watching features.

### News Aggregation

LiteBot now includes a simple `NewsAggregator` that collects headlines from major RSS feeds. The aggregator caches the latest stories in Redis and forwards them to the Telegram bot, allowing you to monitor world events, crypto news and market updates alongside whale trades.


## Development

The test suite uses `pytest` together with `pytest-asyncio`. Install the
requirements and run the tests like so:

```bash
pip install -r requirements.txt
pytest -q
```

These packages are only needed for development and are not required in
production.
