# LiteBot

This repository contains the code for the lightweight trading bot found in `geminiBOT_LiteModev2`. The project is intended to run on low-cost VPS instances using Docker Compose.

## Prerequisites

- **Docker** and **Docker Compose** installed on the host machine.
- Basic familiarity with creating environment variable files (`.env`).

All Python packages needed by the bot are listed in the
`requirements.txt` file at the repository root. The Dockerfile uses this
file during the build stage, so keep it up to date when adding new
dependencies.

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
```

Adjust the values to match your setup.

## Starting the Services

Run the containers from within `geminiBOT_LiteModev2`:

```bash
cd geminiBOT_LiteModev2
docker-compose up --build
```

Compose limits the trading bot container to about **1.5&nbsp;GB** of memory, so a VPS with at least 2&nbsp;GB of RAM is recommended.

## VPS Notes

The bot is designed for low-memory environments. Make sure your VPS provides enough RAM for Docker and the database. Running within the memory limit helps keep costs low while still supporting basic whale-watching features.

