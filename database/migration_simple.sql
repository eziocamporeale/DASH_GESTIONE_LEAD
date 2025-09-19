-- MIGRAZIONE SEMPLIFICATA: Sistema Gruppi Lead
-- Da eseguire nel SQL Editor di Supabase
-- Preserva TUTTI i dati esistenti

-- 1. Crea tabella lead_groups
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

-- 2. Crea tabella user_lead_groups
CREATE TABLE IF NOT EXISTS user_lead_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES lead_groups(id) ON DELETE CASCADE,
    can_manage BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, group_id)
);

-- 3. Aggiungi colonna group_id a leads
ALTER TABLE leads ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES lead_groups(id);

-- 4. Crea indici per performance
CREATE INDEX IF NOT EXISTS idx_leads_group_id ON leads(group_id);
CREATE INDEX IF NOT EXISTS idx_user_lead_groups_user_id ON user_lead_groups(user_id);
CREATE INDEX IF NOT EXISTS idx_user_lead_groups_group_id ON user_lead_groups(group_id);

-- 5. Inserisci gruppi di default
INSERT INTO lead_groups (name, description, color) VALUES
('Team Vendite', 'Gruppo venditori principale', '#28A745'),
('Team Corporate', 'Venditori per clienti aziendali', '#007BFF'),
('Team Retail', 'Venditori per clienti retail', '#FFC107'),
('Team Nord', 'Venditori per clienti del Nord Italia', '#17A2B8'),
('Team Sud', 'Venditori per clienti del Sud Italia', '#FD7E14'),
('Team Centro', 'Venditori per clienti del Centro Italia', '#6F42C1')
ON CONFLICT (name) DO NOTHING;

-- 6. Assegna tutti gli utenti al Team Vendite
INSERT INTO user_lead_groups (user_id, group_id, can_manage)
SELECT 
    u.id,
    lg.id,
    CASE WHEN u.role_id = 1 OR u.is_admin = true THEN true ELSE false END
FROM users u
CROSS JOIN lead_groups lg
WHERE lg.name = 'Team Vendite'
ON CONFLICT (user_id, group_id) DO NOTHING;

-- Verifica finale
SELECT 'Migrazione completata!' as status;
SELECT COUNT(*) as gruppi_creati FROM lead_groups;
SELECT COUNT(*) as assegnazioni_utenti FROM user_lead_groups;
