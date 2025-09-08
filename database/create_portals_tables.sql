-- Tabella per i portali web generati
CREATE TABLE IF NOT EXISTS portals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portal_name VARCHAR(255) NOT NULL,
    portal_type VARCHAR(50) NOT NULL,
    sector VARCHAR(50) NOT NULL,
    company_name VARCHAR(255),
    target_audience TEXT,
    business_goals TEXT,
    color_scheme VARCHAR(100),
    include_contact_form BOOLEAN DEFAULT true,
    include_analytics BOOLEAN DEFAULT true,
    mobile_responsive BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indici per ottimizzare le query
CREATE INDEX IF NOT EXISTS idx_portals_user_id ON portals(user_id);
CREATE INDEX IF NOT EXISTS idx_portals_type ON portals(portal_type);
CREATE INDEX IF NOT EXISTS idx_portals_sector ON portals(sector);
CREATE INDEX IF NOT EXISTS idx_portals_active ON portals(is_active);
CREATE INDEX IF NOT EXISTS idx_portals_created_at ON portals(created_at);

-- Trigger per aggiornare updated_at
CREATE OR REPLACE FUNCTION update_portals_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_portals_updated_at
    BEFORE UPDATE ON portals
    FOR EACH ROW
    EXECUTE FUNCTION update_portals_updated_at();

-- Tabella per i deployment dei portali
CREATE TABLE IF NOT EXISTS portal_deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portal_id UUID REFERENCES portals(id) ON DELETE CASCADE,
    deployment_target VARCHAR(50) NOT NULL,
    deployment_url TEXT,
    deployment_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    deployment_time TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indici per i deployment
CREATE INDEX IF NOT EXISTS idx_deployments_portal_id ON portal_deployments(portal_id);
CREATE INDEX IF NOT EXISTS idx_deployments_target ON portal_deployments(deployment_target);
CREATE INDEX IF NOT EXISTS idx_deployments_status ON portal_deployments(status);

-- Inserisci alcuni portali di esempio
INSERT INTO portals (portal_name, portal_type, sector, company_name, target_audience, business_goals, color_scheme, user_id) VALUES
('Portale Demo Finanza', 'landing_page', 'finanza', 'ABC Finanza SRL', 'PMI e Privati', 'Offrire consulenza finanziaria personalizzata', 'Blu Professionale', (SELECT id FROM users LIMIT 1)),
('Sito Aziendale Tech', 'business_website', 'tech', 'Tech Solutions SpA', 'Aziende innovative', 'Digitalizzazione e automazione processi', 'Verde Finanza', (SELECT id FROM users LIMIT 1)),
('E-commerce Moda', 'ecommerce', 'ecommerce', 'Fashion Store', 'Giovani e adulti', 'Vendita online di abbigliamento', 'Viola Creativo', (SELECT id FROM users LIMIT 1))
ON CONFLICT DO NOTHING;
