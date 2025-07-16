# LiteBot Lite Mode

This project provides a minimal whale tracking and trading bot designed for
low-cost VPS deployments. Key components include a Telegram bot interface,
lightweight database helpers and a simplified AI module that uses CPU only.
The TradingSystem starts a single Telegram bot that forwards alerts from the
whale tracker and other components to your configured chat.

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `DB_POOL_MIN_SIZE` - Minimum database pool connections (default `1`)
- `DB_POOL_MAX_SIZE` - Maximum database pool connections (default `5`)
- `TELEGRAM_BOT_TOKEN` - Telegram bot API token
- `TELEGRAM_CHAT_ID` - Chat ID for sending alerts
- `ALCHEMY_WS_URL` - Ethereum WebSocket provider
- `GMX_VAULT_ADDRESS` - GMX vault address
- `RISK_CAPITAL` - Paper trading capital (default `10000`)
- `RISK_FRACTION` - Fraction of capital risked per trade (default `0.02`)
- `ENABLE_MOBILEBERT` - Set to `0` to disable the sentiment model
- `BERT_MODEL_NAME` - Hugging Face model name for sentiment analysis

Disabling MobileBERT reduces memory usage by ~150&nbsp;MB, which can help on very
small VPS instances.

### Tracked Wallet Settings

Each row in the `tracked_wallets` table supports per-wallet alert options:

- `min_trade_size` - Minimum trade size required before an alert is sent
- `alert_direction` - `long`, `short` or `both` (default)
- `alert_interval` - Seconds to wait before sending another alert for that wallet

## Running

Use Docker Compose to start all services. The compose file expects the
`Dockerfile` located at the repository root:

All dependencies are installed from the `requirements.txt` file in the
repository root during the Docker build.

```bash
docker-compose up --build
```

The bot avoids heavy APIs such as Grok4 and uses only lightweight CPU models
to keep resource usage minimal.

### Market News

An optional `NewsAggregator` component pulls headlines from common RSS feeds so you can keep tabs on geopolitical events and crypto regulations that may impact trading signals.
