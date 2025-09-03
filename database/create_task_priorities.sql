-- Creazione tabella task_priorities mancante

-- Tabella task_priorities
CREATE TABLE IF NOT EXISTS task_priorities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(7) DEFAULT '#6C757D',
    sort_order INTEGER DEFAULT 0,
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

CREATE TRIGGER update_task_priorities_updated_at 
    BEFORE UPDATE ON task_priorities 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Indice per performance
CREATE INDEX IF NOT EXISTS idx_task_priorities_sort ON task_priorities(sort_order);

-- Dati di esempio per task_priorities
INSERT INTO task_priorities (name, color, sort_order) VALUES
('Bassa', '#28A745', 1),
('Media', '#FFC107', 2),
('Alta', '#DC3545', 3)
ON CONFLICT (name) DO NOTHING;
