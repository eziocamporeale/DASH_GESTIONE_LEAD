-- Creazione tabella broker_links per gestione link di affiliate
-- Esegui questo SQL nel SQL Editor di Supabase
-- Creato da Ezio Camporeale

-- Tabella principale broker_links
CREATE TABLE IF NOT EXISTS broker_links (
    id SERIAL PRIMARY KEY,
    broker_name VARCHAR(255) NOT NULL,
    affiliate_link TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_broker_links_broker_name ON broker_links(broker_name);
CREATE INDEX IF NOT EXISTS idx_broker_links_is_active ON broker_links(is_active);
CREATE INDEX IF NOT EXISTS idx_broker_links_created_at ON broker_links(created_at);
CREATE INDEX IF NOT EXISTS idx_broker_links_created_by ON broker_links(created_by);

-- Trigger per aggiornare updated_at automaticamente
CREATE OR REPLACE FUNCTION update_broker_links_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_broker_links_updated_at
    BEFORE UPDATE ON broker_links
    FOR EACH ROW
    EXECUTE FUNCTION update_broker_links_updated_at();

-- Politiche RLS (Row Level Security)
ALTER TABLE broker_links ENABLE ROW LEVEL SECURITY;

-- Politica per accesso completo (admin e manager)
CREATE POLICY "Admin and Manager full access" ON broker_links
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.id = auth.uid()
            AND r.name IN ('Admin', 'Manager')
        )
    );

-- Politica per lettura (tutti gli utenti autenticati)
CREATE POLICY "Authenticated users read access" ON broker_links
    FOR SELECT USING (
        auth.uid() IS NOT NULL
    );

-- Inserimento dati di esempio
INSERT INTO broker_links (broker_name, affiliate_link, created_by) VALUES
('eToro', 'https://www.etoro.com/affiliate/example', 1),
('Plus500', 'https://www.plus500.com/affiliate/example', 1),
('IG Markets', 'https://www.ig.com/affiliate/example', 1)
ON CONFLICT DO NOTHING;
