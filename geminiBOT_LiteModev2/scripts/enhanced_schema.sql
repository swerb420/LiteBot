-- Enhanced wallet tracking schema
CREATE TABLE IF NOT EXISTS tracked_wallets (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR(42) UNIQUE NOT NULL,
    label VARCHAR(100),
    category VARCHAR(50), -- 'whale', 'smart_money', 'institution', 'custom'
    tags TEXT[], -- Array of tags for filtering
    tracking_enabled BOOLEAN DEFAULT true,
    min_trade_size DECIMAL(20,2) DEFAULT 10000,
    added_by VARCHAR(100),
    added_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ,
    metadata JSONB,
    CONSTRAINT valid_address CHECK (wallet_address ~* '^0x[a-fA-F0-9]{40}$')
);

CREATE TABLE IF NOT EXISTS wallet_performance (
    id BIGSERIAL PRIMARY KEY,
    wallet_address VARCHAR(42) NOT NULL,
    period VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly', 'all_time'
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    total_volume DECIMAL(20,2) DEFAULT 0,
    total_pnl DECIMAL(20,2) DEFAULT 0,
    avg_trade_size DECIMAL(20,2) DEFAULT 0,
    best_trade DECIMAL(20,2) DEFAULT 0,
    worst_trade DECIMAL(20,2) DEFAULT 0,
    sharpe_ratio DECIMAL(10,4),
    win_rate DECIMAL(5,2),
    profit_factor DECIMAL(10,2),
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (wallet_address) REFERENCES tracked_wallets(wallet_address) ON DELETE CASCADE,
    UNIQUE(wallet_address, period)
);

CREATE TABLE IF NOT EXISTS whale_patterns (
    id SERIAL PRIMARY KEY,
    pattern_name VARCHAR(100) NOT NULL,
    description TEXT,
    detection_criteria JSONB,
    confidence_threshold DECIMAL(3,2) DEFAULT 0.7,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS wallet_patterns (
    id BIGSERIAL PRIMARY KEY,
    wallet_address VARCHAR(42) NOT NULL,
    pattern_id INTEGER NOT NULL,
    confidence DECIMAL(3,2),
    first_detected TIMESTAMPTZ DEFAULT NOW(),
    last_detected TIMESTAMPTZ DEFAULT NOW(),
    occurrence_count INTEGER DEFAULT 1,
    metadata JSONB,
    FOREIGN KEY (wallet_address) REFERENCES tracked_wallets(wallet_address) ON DELETE CASCADE,
    FOREIGN KEY (pattern_id) REFERENCES whale_patterns(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ai_analysis (
    id BIGSERIAL PRIMARY KEY,
    wallet_address VARCHAR(42),
    analysis_type VARCHAR(50),
    model_version VARCHAR(20),
    sentiment_score DECIMAL(3,2),
    risk_score DECIMAL(3,2),
    strategy_classification VARCHAR(100),
    key_insights TEXT[],
    recommendations TEXT[],
    confidence DECIMAL(3,2),
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

INSERT INTO whale_patterns (pattern_name, description, detection_criteria) VALUES
('Accumulation', 'Consistent buying with increasing position sizes', '{"min_trades": 5, "direction": "long", "size_trend": "increasing"}'),
('Distribution', 'Gradual selling of large positions', '{"min_trades": 5, "direction": "close", "size_trend": "decreasing"}'),
('Momentum Trading', 'Quick entries and exits following trends', '{"avg_hold_time": "< 1 hour", "follows_trend": true}'),
('Contrarian', 'Trading against market sentiment', '{"correlation_with_market": "< -0.5"}'),
('Scalping', 'High frequency small trades', '{"trades_per_day": "> 10", "avg_pnl_per_trade": "< 1%"}'),
('Position Building', 'Gradually building large positions', '{"consecutive_same_direction": "> 3", "total_size": "increasing"}'),
('Stop Hunt', 'Large trades near key levels', '{"near_support_resistance": true, "size": "> 95th_percentile"}'),
('Smart Money', 'Consistently profitable with good timing', '{"win_rate": "> 0.65", "profit_factor": "> 2.0"}');

CREATE INDEX idx_tracked_wallets_category ON tracked_wallets(category) WHERE tracking_enabled = true;
CREATE INDEX idx_tracked_wallets_tags ON tracked_wallets USING GIN(tags);
CREATE INDEX idx_wallet_performance_period ON wallet_performance(wallet_address, period);
CREATE INDEX idx_wallet_patterns_detected ON wallet_patterns(wallet_address, last_detected DESC);
CREATE INDEX idx_ai_analysis_wallet_type ON ai_analysis(wallet_address, analysis_type, analyzed_at DESC);

CREATE OR REPLACE FUNCTION update_wallet_performance()
RETURNS void AS $$
BEGIN
    INSERT INTO wallet_performance (wallet_address, period, total_trades, winning_trades, total_volume, total_pnl, avg_trade_size, best_trade, worst_trade, win_rate, profit_factor)
    SELECT 
        w.wallet_address,
        'daily' as period,
        COUNT(*) as total_trades,
        SUM(CASE WHEN wt.pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
        SUM(wt.size_usd) as total_volume,
        SUM(wt.pnl) as total_pnl,
        AVG(wt.size_usd) as avg_trade_size,
        MAX(wt.pnl) as best_trade,
        MIN(wt.pnl) as worst_trade,
        CASE WHEN COUNT(*) > 0 THEN (SUM(CASE WHEN wt.pnl > 0 THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100 ELSE 0 END as win_rate,
        CASE WHEN SUM(CASE WHEN wt.pnl < 0 THEN ABS(wt.pnl) ELSE 0 END) > 0 
             THEN SUM(CASE WHEN wt.pnl > 0 THEN wt.pnl ELSE 0 END) / SUM(CASE WHEN wt.pnl < 0 THEN ABS(wt.pnl) ELSE 0 END)
             ELSE 0 END as profit_factor
    FROM tracked_wallets w
    LEFT JOIN wallet_trades wt ON w.wallet_address = wt.wallet_address
    WHERE wt.timestamp > NOW() - INTERVAL '1 day'
    GROUP BY w.wallet_address
    ON CONFLICT (wallet_address, period) 
    DO UPDATE SET
        total_trades = EXCLUDED.total_trades,
        winning_trades = EXCLUDED.winning_trades,
        total_volume = EXCLUDED.total_volume,
        total_pnl = EXCLUDED.total_pnl,
        avg_trade_size = EXCLUDED.avg_trade_size,
        best_trade = EXCLUDED.best_trade,
        worst_trade = EXCLUDED.worst_trade,
        win_rate = EXCLUDED.win_rate,
        profit_factor = EXCLUDED.profit_factor,
        calculated_at = NOW();
END;
$$ LANGUAGE plpgsql;
