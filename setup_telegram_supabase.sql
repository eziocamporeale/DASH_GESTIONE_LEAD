-- Setup Telegram per Dashboard Gestione Lead
-- Eseguire questo script nell'interfaccia SQL di Supabase
-- Creato da Ezio Camporeale

-- Tabella configurazione Telegram
CREATE TABLE IF NOT EXISTS telegram_config (
    id TEXT PRIMARY KEY,
    bot_token TEXT NOT NULL,
    chat_id TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella impostazioni notifiche
CREATE TABLE IF NOT EXISTS notification_settings (
    id SERIAL PRIMARY KEY,
    notification_type VARCHAR(100) UNIQUE NOT NULL,
    is_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella log notifiche
CREATE TABLE IF NOT EXISTS notification_logs (
    id TEXT PRIMARY KEY,
    notification_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    retry_count INTEGER DEFAULT 0
);

-- Indici per ottimizzazione
CREATE INDEX IF NOT EXISTS idx_notification_logs_type ON notification_logs(notification_type);
CREATE INDEX IF NOT EXISTS idx_notification_logs_status ON notification_logs(status);
CREATE INDEX IF NOT EXISTS idx_notification_logs_sent_at ON notification_logs(sent_at);
CREATE INDEX IF NOT EXISTS idx_notification_settings_type ON notification_settings(notification_type);

-- Inserisci impostazioni notifiche di default
INSERT INTO notification_settings (notification_type, is_enabled) VALUES
-- Lead
('lead_new_lead', true),
('lead_status_changed', true),
('lead_assigned', true),
('lead_daily_report', false),

-- Task
('task_new_task', true),
('task_completed', true),
('task_due_soon', true),
('task_daily_report', false),

-- Utenti
('user_new_user', true),
('user_login', false),
('user_daily_report', false)
ON CONFLICT (notification_type) DO NOTHING;

-- Abilita RLS (Row Level Security) per le tabelle
ALTER TABLE telegram_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_logs ENABLE ROW LEVEL SECURITY;

-- Crea policy per telegram_config (solo admin possono modificare)
CREATE POLICY "Admin can manage telegram_config" ON telegram_config
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.is_admin = true
        )
    );

-- Crea policy per notification_settings (tutti possono leggere, solo admin possono modificare)
CREATE POLICY "Everyone can read notification_settings" ON notification_settings
    FOR SELECT USING (true);

CREATE POLICY "Admin can manage notification_settings" ON notification_settings
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.is_admin = true
        )
    );

-- Crea policy per notification_logs (solo admin possono vedere i log)
CREATE POLICY "Admin can read notification_logs" ON notification_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.is_admin = true
        )
    );

CREATE POLICY "System can insert notification_logs" ON notification_logs
    FOR INSERT WITH CHECK (true);

-- Commenti per documentazione
COMMENT ON TABLE telegram_config IS 'Configurazione bot Telegram per notifiche';
COMMENT ON TABLE notification_settings IS 'Impostazioni per abilitare/disabilitare notifiche';
COMMENT ON TABLE notification_logs IS 'Log delle notifiche inviate';

COMMENT ON COLUMN telegram_config.bot_token IS 'Token del bot Telegram ottenuto da @BotFather';
COMMENT ON COLUMN telegram_config.chat_id IS 'ID del canale/gruppo dove inviare le notifiche';
COMMENT ON COLUMN notification_logs.status IS 'Stato della notifica: sent, failed, pending';
