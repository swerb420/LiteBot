# === scripts/schema.sql ===
-- This is your DB schema for whale trades
CREATE TABLE IF NOT EXISTS wallet_trades (
  id SERIAL PRIMARY KEY,
  wallet_address VARCHAR(64) NOT NULL,
  protocol VARCHAR(32) NOT NULL,
  action VARCHAR(32) NOT NULL,
  symbol VARCHAR(16),
  size_usd DOUBLE PRECISION,
  leverage DOUBLE PRECISION,
  direction VARCHAR(8),
  pnl DOUBLE PRECISION,
  tx_hash VARCHAR(66) UNIQUE,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_wallet_trades_tx_hash ON wallet_trades (tx_hash);
CREATE INDEX IF NOT EXISTS idx_wallet_trades_protocol_address ON wallet_trades (protocol, wallet_address);

