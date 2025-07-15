# LiteBot Lite Mode

This project provides a minimal whale tracking and trading bot designed for
low-cost VPS deployments. Key components include a Telegram bot interface,
lightweight database helpers and a simplified AI module that uses CPU only.

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `DB_POOL_MIN_SIZE` - Minimum database pool connections (default `1`)
- `DB_POOL_MAX_SIZE` - Maximum database pool connections (default `5`)
- `TELEGRAM_BOT_TOKEN` - Telegram bot API token
- `TELEGRAM_CHAT_ID` - Chat ID for sending alerts
- `ALCHEMY_WS_URL` - Ethereum WebSocket provider
- `GMX_VAULT_ADDRESS` - GMX vault address

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
