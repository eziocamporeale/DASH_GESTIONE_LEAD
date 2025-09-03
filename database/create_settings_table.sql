-- Creazione tabella settings mancante

-- Tabella settings
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL UNIQUE,
    value TEXT,
    category VARCHAR(100) DEFAULT 'general',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger per updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_settings_updated_at 
    BEFORE UPDATE ON settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);
CREATE INDEX IF NOT EXISTS idx_settings_category ON settings(category);

-- Dati di esempio per settings
INSERT INTO settings (key, value, category, description) VALUES
-- Impostazioni azienda
('company_name', 'La Tua Azienda', 'company', 'Nome dell''azienda'),
('company_email', 'info@tuazienda.com', 'company', 'Email principale dell''azienda'),
('company_phone', '+39 123 456 7890', 'company', 'Telefono principale dell''azienda'),
('company_address', 'Via Roma 123, 00100 Roma', 'company', 'Indirizzo dell''azienda'),

-- Impostazioni notifiche
('notifications_email_enabled', 'true', 'notifications', 'Abilita notifiche email'),
('notifications_smtp_host', 'smtp.gmail.com', 'notifications', 'Host SMTP'),
('notifications_smtp_port', '587', 'notifications', 'Porta SMTP'),
('notifications_smtp_username', 'your-email@gmail.com', 'notifications', 'Username SMTP'),
('notifications_smtp_password', '', 'notifications', 'Password SMTP'),
('notifications_push_enabled', 'false', 'notifications', 'Abilita notifiche push'),

-- Impostazioni sistema
('system_theme', 'light', 'system', 'Tema dell''interfaccia'),
('system_language', 'it', 'system', 'Lingua del sistema'),
('system_timezone', 'Europe/Rome', 'system', 'Fuso orario'),
('system_automations_enabled', 'true', 'system', 'Abilita automazioni'),

-- Impostazioni backup
('backup_frequency', 'daily', 'backup', 'Frequenza backup'),
('backup_path', '/backups', 'backup', 'Percorso backup'),
('backup_retention_days', '30', 'backup', 'Giorni di retention backup'),
('backup_auto_enabled', 'true', 'backup', 'Backup automatico abilitato')
ON CONFLICT (key) DO NOTHING;
