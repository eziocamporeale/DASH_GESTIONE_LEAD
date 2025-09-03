-- Schema Supabase per DASH_GESTIONE_LEAD
-- Creato da Ezio Camporeale

-- Abilita estensioni necessarie
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== TABELLE BASE ====================

-- Tabella ruoli utenti
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella dipartimenti
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella utenti
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    role_id INTEGER REFERENCES roles(id),
    department_id INTEGER REFERENCES departments(id),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    notes TEXT,
    last_login TIMESTAMP WITH TIME ZONE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== TABELLE LEAD ====================

-- Tabella categorie lead
CREATE TABLE IF NOT EXISTS lead_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(7) DEFAULT '#6C757D',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella stati lead
CREATE TABLE IF NOT EXISTS lead_states (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(7) DEFAULT '#6C757D',
    order_index INTEGER DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella priorità lead
CREATE TABLE IF NOT EXISTS lead_priorities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(7) DEFAULT '#6C757D',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella fonti lead
CREATE TABLE IF NOT EXISTS lead_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella lead principali
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    company VARCHAR(100),
    position VARCHAR(100),
    budget DECIMAL(10,2),
    expected_close_date DATE,
    category_id INTEGER REFERENCES lead_categories(id),
    state_id INTEGER REFERENCES lead_states(id),
    priority_id INTEGER REFERENCES lead_priorities(id),
    source_id INTEGER REFERENCES lead_sources(id),
    assigned_to INTEGER REFERENCES users(id),
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== TABELLE TASK ====================

-- Tabella tipi task
CREATE TABLE IF NOT EXISTS task_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella stati task
CREATE TABLE IF NOT EXISTS task_states (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(7) DEFAULT '#6C757D',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella task principali
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    task_type_id INTEGER REFERENCES task_types(id),
    state_id INTEGER REFERENCES task_states(id),
    priority_id INTEGER REFERENCES lead_priorities(id),
    lead_id INTEGER REFERENCES leads(id),
    assigned_to INTEGER REFERENCES users(id),
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== TABELLE CONTATTI ====================

-- Tabella template contatti
CREATE TABLE IF NOT EXISTS contact_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('email', 'sms', 'whatsapp')),
    subject VARCHAR(200),
    content TEXT NOT NULL,
    category VARCHAR(50),
    delay_hours INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella sequenze contatti
CREATE TABLE IF NOT EXISTS contact_sequences (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    trigger_event VARCHAR(50),
    categories JSONB DEFAULT '[]',
    sources JSONB DEFAULT '[]',
    priorities JSONB DEFAULT '[]',
    min_budget DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella step sequenze
CREATE TABLE IF NOT EXISTS contact_steps (
    id SERIAL PRIMARY KEY,
    sequence_id INTEGER REFERENCES contact_sequences(id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES contact_templates(id),
    step_order INTEGER NOT NULL,
    delay_hours INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella cronologia contatti
CREATE TABLE IF NOT EXISTS lead_contacts (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES contact_templates(id),
    sequence_id INTEGER REFERENCES contact_sequences(id),
    type VARCHAR(20) NOT NULL CHECK (type IN ('email', 'sms', 'whatsapp')),
    subject VARCHAR(200),
    content TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'opened', 'clicked', 'failed')),
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    response_received BOOLEAN DEFAULT FALSE,
    response_content TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== TABELLE SISTEMA ====================

-- Tabella log attività
CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella impostazioni
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== INDICI ====================

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_leads_assigned_to ON leads(assigned_to);
CREATE INDEX IF NOT EXISTS idx_leads_state_id ON leads(state_id);
CREATE INDEX IF NOT EXISTS idx_leads_category_id ON leads(category_id);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_leads_expected_close_date ON leads(expected_close_date);

CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_state_id ON tasks(state_id);
CREATE INDEX IF NOT EXISTS idx_tasks_lead_id ON tasks(lead_id);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);

CREATE INDEX IF NOT EXISTS idx_lead_contacts_lead_id ON lead_contacts(lead_id);
CREATE INDEX IF NOT EXISTS idx_lead_contacts_template_id ON lead_contacts(template_id);
CREATE INDEX IF NOT EXISTS idx_lead_contacts_sequence_id ON lead_contacts(sequence_id);
CREATE INDEX IF NOT EXISTS idx_lead_contacts_status ON lead_contacts(status);
CREATE INDEX IF NOT EXISTS idx_lead_contacts_created_at ON lead_contacts(created_at);

CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_action ON activity_log(action);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at);

-- ==================== TRIGGER PER UPDATED_AT ====================

-- Funzione per aggiornare updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger per tutte le tabelle con updated_at
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lead_categories_updated_at BEFORE UPDATE ON lead_categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lead_states_updated_at BEFORE UPDATE ON lead_states FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lead_priorities_updated_at BEFORE UPDATE ON lead_priorities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lead_sources_updated_at BEFORE UPDATE ON lead_sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_task_types_updated_at BEFORE UPDATE ON task_types FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_task_states_updated_at BEFORE UPDATE ON task_states FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_contact_templates_updated_at BEFORE UPDATE ON contact_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_contact_sequences_updated_at BEFORE UPDATE ON contact_sequences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lead_contacts_updated_at BEFORE UPDATE ON lead_contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== ROW LEVEL SECURITY (RLS) ====================

-- Abilita RLS su tutte le tabelle
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_priorities ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_sequences ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

-- Politiche RLS per accesso completo (admin)
CREATE POLICY "Admin full access" ON roles FOR ALL USING (true);
CREATE POLICY "Admin full access" ON departments FOR ALL USING (true);
CREATE POLICY "Admin full access" ON users FOR ALL USING (true);
CREATE POLICY "Admin full access" ON lead_categories FOR ALL USING (true);
CREATE POLICY "Admin full access" ON lead_states FOR ALL USING (true);
CREATE POLICY "Admin full access" ON lead_priorities FOR ALL USING (true);
CREATE POLICY "Admin full access" ON lead_sources FOR ALL USING (true);
CREATE POLICY "Admin full access" ON leads FOR ALL USING (true);
CREATE POLICY "Admin full access" ON task_types FOR ALL USING (true);
CREATE POLICY "Admin full access" ON task_states FOR ALL USING (true);
CREATE POLICY "Admin full access" ON tasks FOR ALL USING (true);
CREATE POLICY "Admin full access" ON contact_templates FOR ALL USING (true);
CREATE POLICY "Admin full access" ON contact_sequences FOR ALL USING (true);
CREATE POLICY "Admin full access" ON contact_steps FOR ALL USING (true);
CREATE POLICY "Admin full access" ON lead_contacts FOR ALL USING (true);
CREATE POLICY "Admin full access" ON activity_log FOR ALL USING (true);
CREATE POLICY "Admin full access" ON settings FOR ALL USING (true);

-- Politiche RLS per utenti normali (leggono solo i loro dati)
CREATE POLICY "Users read own data" ON leads FOR SELECT USING (assigned_to = auth.uid() OR created_by = auth.uid());
CREATE POLICY "Users read own tasks" ON tasks FOR SELECT USING (assigned_to = auth.uid() OR created_by = auth.uid());
CREATE POLICY "Users read own contacts" ON lead_contacts FOR SELECT USING (created_by = auth.uid());

-- ==================== DATI DI DEFAULT ====================

-- Inserimento ruoli di default
INSERT INTO roles (name, description, permissions) VALUES
('Admin', 'Amministratore completo del sistema', '["all"]'),
('Manager', 'Manager con permessi di gestione team', '["manage_leads", "manage_team", "view_reports"]'),
('Setter', 'Setter per creazione e gestione lead', '["create_leads", "edit_leads", "view_assigned"]'),
('Closer', 'Closer per chiusura deal', '["edit_leads", "view_assigned", "close_deals"]'),
('Viewer', 'Visualizzatore con permessi limitati', '["view_leads", "view_reports"]')
ON CONFLICT (name) DO NOTHING;

-- Inserimento dipartimenti di default
INSERT INTO departments (name, description) VALUES
('Vendite', 'Dipartimento vendite'),
('Marketing', 'Dipartimento marketing'),
('Supporto', 'Dipartimento supporto clienti')
ON CONFLICT (name) DO NOTHING;

-- Inserimento stati lead di default
INSERT INTO lead_states (name, color, order_index, description) VALUES
('Nuovo', '#17A2B8', 1, 'Lead appena creato'),
('Contattato', '#FFC107', 2, 'Lead contattato'),
('Qualificato', '#28A745', 3, 'Lead qualificato'),
('Proposta', '#FD7E14', 4, 'Proposta inviata'),
('Chiuso', '#6C757D', 5, 'Deal chiuso'),
('Perso', '#DC3545', 6, 'Lead perso')
ON CONFLICT (name) DO NOTHING;

-- Inserimento priorità lead di default
INSERT INTO lead_priorities (name, color, description) VALUES
('Alta', '#DC3545', 'Priorità alta'),
('Media', '#FFC107', 'Priorità media'),
('Bassa', '#28A745', 'Priorità bassa')
ON CONFLICT (name) DO NOTHING;

-- Inserimento categorie lead di default
INSERT INTO lead_categories (name, color, description) VALUES
('Caldo', '#DC3545', 'Lead molto interessato'),
('Tiepido', '#FFC107', 'Lead moderatamente interessato'),
('Freddo', '#6C757D', 'Lead poco interessato')
ON CONFLICT (name) DO NOTHING;

-- Inserimento fonti lead di default
INSERT INTO lead_sources (name, description) VALUES
('Sito Web', 'Lead dal sito web'),
('Social Media', 'Lead dai social media'),
('Email Marketing', 'Lead da email marketing'),
('Referral', 'Lead da referral'),
('Eventi', 'Lead da eventi'),
('Cold Call', 'Lead da cold call')
ON CONFLICT (name) DO NOTHING;

-- Inserimento stati task di default
INSERT INTO task_states (name, color, description) VALUES
('Da Fare', '#17A2B8', 'Task da completare'),
('In Corso', '#FFC107', 'Task in corso'),
('Completato', '#28A745', 'Task completato'),
('Annullato', '#DC3545', 'Task annullato')
ON CONFLICT (name) DO NOTHING;

-- Inserimento tipi task di default
INSERT INTO task_types (name, description) VALUES
('Chiamata', 'Task di chiamata'),
('Email', 'Task di invio email'),
('Meeting', 'Task di meeting'),
('Follow-up', 'Task di follow-up'),
('Proposta', 'Task di invio proposta'),
('Demo', 'Task di demo prodotto')
ON CONFLICT (name) DO NOTHING;

-- Inserimento utente admin di default
INSERT INTO users (username, email, password_hash, first_name, last_name, role_id, is_admin, is_active) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.gSJhqG', 'Admin', 'User', 1, TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;

-- Inserimento impostazioni di default
INSERT INTO settings (key, value, description) VALUES
('company_name', 'La Mia Azienda', 'Nome dell''azienda'),
('company_email', 'info@miaazienda.com', 'Email principale dell''azienda'),
('items_per_page', '20', 'Numero di elementi per pagina'),
('theme', 'Light', 'Tema dell''interfaccia'),
('language', 'Italiano', 'Lingua dell''interfaccia'),
('backup_enabled', 'true', 'Abilita backup automatico'),
('backup_frequency', 'Daily', 'Frequenza backup'),
('email_notifications', 'true', 'Abilita notifiche email')
ON CONFLICT (key) DO NOTHING;
