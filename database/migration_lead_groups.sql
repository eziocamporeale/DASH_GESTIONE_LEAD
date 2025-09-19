-- MIGRAZIONE SICURA: Sistema Gruppi Lead per DASH_GESTIONE_LEAD
-- Preserva TUTTI i dati esistenti
-- Creato da Ezio Camporeale
-- Data: 2025-09-19

-- ==================== VERIFICA PRE-MIGRAZIONE ====================

-- Verifica che le tabelle esistenti siano presenti
DO $$ 
BEGIN
    -- Verifica tabella leads
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'leads') THEN
        RAISE EXCEPTION 'Tabella leads non trovata. Eseguire prima lo schema base.';
    END IF;
    
    -- Verifica tabella users
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        RAISE EXCEPTION 'Tabella users non trovata. Eseguire prima lo schema base.';
    END IF;
    
    RAISE NOTICE '✅ Verifica pre-migrazione completata con successo';
END $$;

-- ==================== CREAZIONE TABELLE GRUPPI ====================

-- 1. Creazione tabella lead_groups (solo se non esiste)
CREATE TABLE IF NOT EXISTS lead_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) DEFAULT '#6C757D',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);

-- 2. Creazione tabella user_lead_groups (solo se non esiste)
CREATE TABLE IF NOT EXISTS user_lead_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES lead_groups(id) ON DELETE CASCADE,
    can_manage BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, group_id)
);

-- ==================== AGGIUNTA COLONNE ESISTENTI ====================

-- 3. Aggiunta colonna group_id a leads (solo se non esiste)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'leads' AND column_name = 'group_id'
    ) THEN
        ALTER TABLE leads ADD COLUMN group_id INTEGER REFERENCES lead_groups(id);
        RAISE NOTICE '✅ Colonna group_id aggiunta alla tabella leads';
    ELSE
        RAISE NOTICE 'ℹ️ Colonna group_id già presente nella tabella leads';
    END IF;
END $$;

-- ==================== INDICI E PERFORMANCE ====================

-- Indici per ottimizzare le query sui gruppi
CREATE INDEX IF NOT EXISTS idx_leads_group_id ON leads(group_id);
CREATE INDEX IF NOT EXISTS idx_user_lead_groups_user_id ON user_lead_groups(user_id);
CREATE INDEX IF NOT EXISTS idx_user_lead_groups_group_id ON user_lead_groups(group_id);
CREATE INDEX IF NOT EXISTS idx_lead_groups_active ON lead_groups(is_active);

-- ==================== TRIGGER PER TIMESTAMP ====================

-- Funzione per aggiornare updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger per lead_groups
DROP TRIGGER IF EXISTS update_lead_groups_updated_at ON lead_groups;
CREATE TRIGGER update_lead_groups_updated_at 
    BEFORE UPDATE ON lead_groups 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger per user_lead_groups
DROP TRIGGER IF EXISTS update_user_lead_groups_updated_at ON user_lead_groups;
CREATE TRIGGER update_user_lead_groups_updated_at 
    BEFORE UPDATE ON user_lead_groups 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== ROW LEVEL SECURITY ====================

-- Abilita RLS sulle nuove tabelle
ALTER TABLE lead_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_lead_groups ENABLE ROW LEVEL SECURITY;

-- Politiche RLS per lead_groups
CREATE POLICY "Admin full access lead_groups" ON lead_groups FOR ALL USING (true);
CREATE POLICY "Users read assigned groups" ON lead_groups FOR SELECT USING (
    id IN (
        SELECT group_id FROM user_lead_groups 
        WHERE user_id = auth.uid()
    )
);

-- Politiche RLS per user_lead_groups
CREATE POLICY "Admin full access user_lead_groups" ON user_lead_groups FOR ALL USING (true);
CREATE POLICY "Users read own assignments" ON user_lead_groups FOR SELECT USING (user_id = auth.uid());

-- Politiche RLS per leads con gruppi
CREATE POLICY "Users read leads from assigned groups" ON leads FOR SELECT USING (
    group_id IS NULL OR 
    group_id IN (
        SELECT group_id FROM user_lead_groups 
        WHERE user_id = auth.uid()
    )
);

-- ==================== DATI DI DEFAULT ====================

-- Inserimento gruppi di default (solo se non esistono)
INSERT INTO lead_groups (name, description, color) VALUES
('Team Vendite', 'Gruppo venditori principale', '#28A745'),
('Team Corporate', 'Venditori per clienti aziendali', '#007BFF'),
('Team Retail', 'Venditori per clienti retail', '#FFC107'),
('Team Nord', 'Venditori per clienti del Nord Italia', '#17A2B8'),
('Team Sud', 'Venditori per clienti del Sud Italia', '#FD7E14'),
('Team Centro', 'Venditori per clienti del Centro Italia', '#6F42C1')
ON CONFLICT (name) DO NOTHING;

-- ==================== ASSEGNAZIONE UTENTI AI GRUPPI ====================

-- Assegna automaticamente tutti gli utenti al gruppo "Team Vendite" come default
-- (solo se non hanno già assegnazioni)
INSERT INTO user_lead_groups (user_id, group_id, can_manage)
SELECT 
    u.id,
    lg.id,
    CASE WHEN u.role_id = 1 OR u.is_admin = true THEN true ELSE false END
FROM users u
CROSS JOIN lead_groups lg
WHERE lg.name = 'Team Vendite'
AND NOT EXISTS (
    SELECT 1 FROM user_lead_groups ulg 
    WHERE ulg.user_id = u.id
)
ON CONFLICT (user_id, group_id) DO NOTHING;

-- ==================== VERIFICA POST-MIGRAZIONE ====================

DO $$ 
DECLARE
    groups_count INTEGER;
    assignments_count INTEGER;
    leads_with_groups INTEGER;
BEGIN
    -- Conta gruppi creati
    SELECT COUNT(*) INTO groups_count FROM lead_groups;
    
    -- Conta assegnazioni utenti-gruppi
    SELECT COUNT(*) INTO assignments_count FROM user_lead_groups;
    
    -- Conta lead con gruppi (sarà 0 inizialmente)
    SELECT COUNT(*) INTO leads_with_groups FROM leads WHERE group_id IS NOT NULL;
    
    RAISE NOTICE '✅ Migrazione completata con successo!';
    RAISE NOTICE '📊 Gruppi creati: %', groups_count;
    RAISE NOTICE '👥 Assegnazioni utenti-gruppi: %', assignments_count;
    RAISE NOTICE '🎯 Lead con gruppi: %', leads_with_groups;
    RAISE NOTICE 'ℹ️ I lead esistenti non sono stati modificati (group_id = NULL)';
END $$;

-- ==================== COMMENTI E DOCUMENTAZIONE ====================

COMMENT ON TABLE lead_groups IS 'Gruppi di venditori per organizzare i lead';
COMMENT ON TABLE user_lead_groups IS 'Associazione tra utenti e gruppi di lead con permessi';
COMMENT ON COLUMN leads.group_id IS 'Gruppo di appartenenza del lead (NULL = senza gruppo)';

COMMENT ON COLUMN user_lead_groups.can_manage IS 'Se true, l''utente può gestire il gruppo (assegnare lead, modificare gruppo)';
COMMENT ON COLUMN lead_groups.is_active IS 'Se true, il gruppo è attivo e può essere utilizzato';

-- ==================== FINE MIGRAZIONE ====================

-- Messaggio di completamento
DO $$ 
BEGIN
    RAISE NOTICE '🎉 MIGRAZIONE SISTEMA GRUPPI LEAD COMPLETATA!';
    RAISE NOTICE '📋 Prossimi passi:';
    RAISE NOTICE '   1. Testare il sistema con dati di esempio';
    RAISE NOTICE '   2. Aggiornare l''interfaccia per gestire i gruppi';
    RAISE NOTICE '   3. Assegnare lead esistenti ai gruppi appropriati';
    RAISE NOTICE '   4. Configurare i filtri per utenti e gruppi';
END $$;
