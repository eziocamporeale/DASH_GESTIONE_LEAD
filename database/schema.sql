-- Schema Database DASH_GESTIONE_LEAD
-- Creato da Ezio Camporeale

-- Tabella utenti
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    role_id INTEGER NOT NULL,
    department_id INTEGER,
    notes TEXT,
    is_active BOOLEAN DEFAULT 1,
    is_admin BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Tabella ruoli
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT, -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella dipartimenti
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    manager_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES users(id)
);

-- Tabella categorie lead
CREATE TABLE IF NOT EXISTS lead_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) NOT NULL, -- Hex color
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella stati lead
CREATE TABLE IF NOT EXISTS lead_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) NOT NULL, -- Hex color
    description TEXT,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella fonti lead
CREATE TABLE IF NOT EXISTS lead_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella lead
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    company VARCHAR(100),
    position VARCHAR(100),
    source_id INTEGER,
    category_id INTEGER,
    state_id INTEGER DEFAULT 1,
    priority_id INTEGER DEFAULT 2,
    assigned_to INTEGER,
    notes TEXT,
    budget DECIMAL(10,2),
    expected_close_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (source_id) REFERENCES lead_sources(id),
    FOREIGN KEY (category_id) REFERENCES lead_categories(id),
    FOREIGN KEY (state_id) REFERENCES lead_states(id),
    FOREIGN KEY (priority_id) REFERENCES lead_priorities(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Tabella priorità lead
CREATE TABLE IF NOT EXISTS lead_priorities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL,
    color VARCHAR(7) NOT NULL, -- Hex color
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella tipi task
CREATE TABLE IF NOT EXISTS task_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7) NOT NULL, -- Hex color
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella stati task
CREATE TABLE IF NOT EXISTS task_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) NOT NULL, -- Hex color
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella task
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    lead_id INTEGER,
    task_type_id INTEGER,
    state_id INTEGER DEFAULT 1,
    priority_id INTEGER DEFAULT 2,
    assigned_to INTEGER,
    created_by INTEGER NOT NULL,
    due_date DATE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id),
    FOREIGN KEY (task_type_id) REFERENCES task_types(id),
    FOREIGN KEY (state_id) REFERENCES task_states(id),
    FOREIGN KEY (priority_id) REFERENCES lead_priorities(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Tabella template contatti
CREATE TABLE IF NOT EXISTS contact_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL, -- Email, SMS, WhatsApp
    category VARCHAR(50) NOT NULL, -- Follow-up, Proposta, Qualificazione, etc.
    subject VARCHAR(200),
    content TEXT NOT NULL,
    delay_hours INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    priority VARCHAR(20) DEFAULT 'Media', -- Bassa, Media, Alta
    notes TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Tabella sequenze di contatto
CREATE TABLE IF NOT EXISTS contact_sequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- Lead Nascita, Follow-up, Qualificazione, etc.
    trigger_event VARCHAR(50) NOT NULL, -- Lead Creato, Lead Qualificato, etc.
    categories TEXT, -- JSON array of category names
    sources TEXT, -- JSON array of source names
    priorities TEXT, -- JSON array of priority names
    min_budget DECIMAL(10,2) DEFAULT 0,
    notes TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Tabella step sequenze
CREATE TABLE IF NOT EXISTS contact_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sequence_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    delay_hours INTEGER DEFAULT 0,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sequence_id) REFERENCES contact_sequences(id),
    FOREIGN KEY (template_id) REFERENCES contact_templates(id)
);

-- Tabella contatti lead
CREATE TABLE IF NOT EXISTS lead_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    template_id INTEGER,
    sequence_id INTEGER,
    step_id INTEGER,
    contact_type VARCHAR(20) NOT NULL, -- Email, SMS, WhatsApp
    subject VARCHAR(200),
    content TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, delivered, failed, success
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    response_received BOOLEAN DEFAULT 0,
    response_content TEXT,
    notes TEXT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id),
    FOREIGN KEY (template_id) REFERENCES contact_templates(id),
    FOREIGN KEY (sequence_id) REFERENCES contact_sequences(id),
    FOREIGN KEY (step_id) REFERENCES contact_steps(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Tabella attività (log)
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50), -- lead, task, user, etc.
    entity_id INTEGER,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabella impostazioni
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_leads_assigned_to ON leads(assigned_to);
CREATE INDEX IF NOT EXISTS idx_leads_state ON leads(state_id);
CREATE INDEX IF NOT EXISTS idx_leads_category ON leads(category_id);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state_id);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_lead_contacts_lead_id ON lead_contacts(lead_id);
CREATE INDEX IF NOT EXISTS idx_lead_contacts_date ON lead_contacts(created_at);
CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at);

-- Trigger per updated_at
CREATE TRIGGER IF NOT EXISTS update_leads_timestamp 
    AFTER UPDATE ON leads
    BEGIN
        UPDATE leads SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_tasks_timestamp 
    AFTER UPDATE ON tasks
    BEGIN
        UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
    AFTER UPDATE ON users
    BEGIN
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
