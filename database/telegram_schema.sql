-- Schema Telegram per Dashboard Gestione Lead
-- Creato da Ezio Camporeale

-- Tabella configurazione Telegram
CREATE TABLE IF NOT EXISTS telegram_config (
    id TEXT PRIMARY KEY,
    bot_token TEXT NOT NULL,
    chat_id TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella impostazioni notifiche
CREATE TABLE IF NOT EXISTS notification_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_type VARCHAR(100) UNIQUE NOT NULL,
    is_enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella log notifiche
CREATE TABLE IF NOT EXISTS notification_logs (
    id TEXT PRIMARY KEY,
    notification_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'sent', 'failed', 'pending'
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retry_count INTEGER DEFAULT 0
);

-- Inserisci impostazioni notifiche di default
INSERT OR IGNORE INTO notification_settings (notification_type, is_enabled) VALUES
-- Lead
('lead_new_lead', 1),
('lead_status_changed', 1),
('lead_assigned', 1),
('lead_daily_report', 0),

-- Task
('task_new_task', 1),
('task_completed', 1),
('task_due_soon', 1),
('task_daily_report', 0),

-- Utenti
('user_new_user', 1),
('user_login', 0),
('user_daily_report', 0);

-- Indici per ottimizzazione
CREATE INDEX IF NOT EXISTS idx_notification_logs_type ON notification_logs(notification_type);
CREATE INDEX IF NOT EXISTS idx_notification_logs_status ON notification_logs(status);
CREATE INDEX IF NOT EXISTS idx_notification_logs_sent_at ON notification_logs(sent_at);
CREATE INDEX IF NOT EXISTS idx_notification_settings_type ON notification_settings(notification_type);
