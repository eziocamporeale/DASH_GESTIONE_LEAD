-- Creazione tabella scripts per gestione script testuali
-- Esegui questo SQL nel SQL Editor di Supabase
-- Creato da Ezio Camporeale

-- Tabella principale scripts
CREATE TABLE IF NOT EXISTS scripts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    script_type VARCHAR(100) NOT NULL DEFAULT 'chiamata',
    category VARCHAR(100) NOT NULL DEFAULT 'vendita',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_scripts_title ON scripts(title);
CREATE INDEX IF NOT EXISTS idx_scripts_script_type ON scripts(script_type);
CREATE INDEX IF NOT EXISTS idx_scripts_category ON scripts(category);
CREATE INDEX IF NOT EXISTS idx_scripts_is_active ON scripts(is_active);
CREATE INDEX IF NOT EXISTS idx_scripts_created_at ON scripts(created_at);
CREATE INDEX IF NOT EXISTS idx_scripts_created_by ON scripts(created_by);

-- Trigger per aggiornare updated_at automaticamente
CREATE OR REPLACE FUNCTION update_scripts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_scripts_updated_at
    BEFORE UPDATE ON scripts
    FOR EACH ROW
    EXECUTE FUNCTION update_scripts_updated_at();

-- Politiche RLS (Row Level Security) - Versione Semplificata
ALTER TABLE scripts ENABLE ROW LEVEL SECURITY;

-- Politica per accesso completo (tutti gli utenti autenticati)
CREATE POLICY "Authenticated users full access" ON scripts
    FOR ALL USING (
        auth.uid() IS NOT NULL
    );

-- Commenti per documentazione
COMMENT ON TABLE scripts IS 'Tabella per gestione script testuali per chiamate e comunicazioni';
COMMENT ON COLUMN scripts.title IS 'Titolo dello script';
COMMENT ON COLUMN scripts.content IS 'Contenuto dello script';
COMMENT ON COLUMN scripts.script_type IS 'Tipo di script (chiamata, email, messaggio, presentazione, vendita, supporto)';
COMMENT ON COLUMN scripts.category IS 'Categoria dello script (lead_generation, vendita, follow_up, supporto, marketing)';
COMMENT ON COLUMN scripts.is_active IS 'Stato attivo/inattivo dello script';
COMMENT ON COLUMN scripts.created_by IS 'ID dell''utente che ha creato lo script';
