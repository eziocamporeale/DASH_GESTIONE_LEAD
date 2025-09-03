-- Creazione tabelle per il modulo contatti

-- Tabella contact_templates
CREATE TABLE IF NOT EXISTS contact_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('email', 'sms', 'whatsapp')),
    content TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    category VARCHAR(100) DEFAULT 'general',
    delay_hours INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 3,
    priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella contact_sequences
CREATE TABLE IF NOT EXISTS contact_sequences (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    trigger_event VARCHAR(100) NOT NULL,
    conditions JSONB DEFAULT '{}',
    steps JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella contact_history
CREATE TABLE IF NOT EXISTS contact_history (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES contact_templates(id) ON DELETE SET NULL,
    sequence_id INTEGER REFERENCES contact_sequences(id) ON DELETE SET NULL,
    contact_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger per updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_contact_templates_updated_at 
    BEFORE UPDATE ON contact_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contact_sequences_updated_at 
    BEFORE UPDATE ON contact_sequences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_contact_templates_type ON contact_templates(type);
CREATE INDEX IF NOT EXISTS idx_contact_templates_category ON contact_templates(category);
CREATE INDEX IF NOT EXISTS idx_contact_templates_active ON contact_templates(is_active);

CREATE INDEX IF NOT EXISTS idx_contact_sequences_trigger ON contact_sequences(trigger_event);
CREATE INDEX IF NOT EXISTS idx_contact_sequences_active ON contact_sequences(is_active);

CREATE INDEX IF NOT EXISTS idx_contact_history_lead ON contact_history(lead_id);
CREATE INDEX IF NOT EXISTS idx_contact_history_template ON contact_history(template_id);
CREATE INDEX IF NOT EXISTS idx_contact_history_sequence ON contact_history(sequence_id);
CREATE INDEX IF NOT EXISTS idx_contact_history_status ON contact_history(status);
CREATE INDEX IF NOT EXISTS idx_contact_history_sent ON contact_history(sent_at);

-- Dati di esempio per contact_templates
INSERT INTO contact_templates (name, type, content, variables, category, delay_hours, retry_count, priority) VALUES
('Benvenuto Email', 'email', 'Ciao {{lead_name}}, benvenuto! Siamo felici di averti con noi.', '["lead_name", "company_name"]', 'welcome', 0, 3, 1),
('Follow-up SMS', 'sms', 'Ciao {{lead_name}}, come va? Hai domande sui nostri servizi?', '["lead_name"]', 'follow_up', 24, 2, 2),
('Promozione WhatsApp', 'whatsapp', 'Ciao {{lead_name}}! 🎉 Offerta speciale solo per te: {{offer}}', '["lead_name", "offer"]', 'promotion', 0, 1, 3)
ON CONFLICT DO NOTHING;

-- Dati di esempio per contact_sequences
INSERT INTO contact_sequences (name, trigger_event, conditions, steps, is_active) VALUES
('Sequenza Benvenuto', 'lead_created', '{"lead_source": ["website", "social"]}', '[{"template_id": 1, "delay_hours": 0}, {"template_id": 2, "delay_hours": 24}]', true),
('Sequenza Follow-up', 'lead_contacted', '{"lead_state": "contacted"}', '[{"template_id": 2, "delay_hours": 48}, {"template_id": 3, "delay_hours": 168}]', true)
ON CONFLICT DO NOTHING;
