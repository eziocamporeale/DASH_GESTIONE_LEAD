#!/usr/bin/env python3
"""
Script semplice per creare la tabella broker_links in Supabase
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_broker_links_table_simple():
    """Crea la tabella broker_links usando le API REST"""
    
    print("🏗️ CREAZIONE TABELLA BROKER_LINKS (Metodo Semplice)")
    print("=" * 60)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connessione Supabase stabilita")
        
        # Prova a inserire un record di test per verificare se la tabella esiste
        print("\n🔍 Verifica esistenza tabella...")
        
        try:
            # Prova a leggere dalla tabella
            result = supabase.table('broker_links').select('*').limit(1).execute()
            print("✅ Tabella broker_links già esistente")
            return True
        except Exception as e:
            if "Could not find the table" in str(e):
                print("❌ Tabella broker_links non trovata")
                print("⚠️ La tabella deve essere creata manualmente in Supabase")
                print("\n📋 ISTRUZIONI PER CREARE LA TABELLA:")
                print("1. Vai su https://supabase.com/dashboard")
                print("2. Seleziona il tuo progetto")
                print("3. Vai su 'SQL Editor'")
                print("4. Copia e incolla il seguente SQL:")
                print("\n" + "=" * 50)
                print_sql_instructions()
                print("=" * 50)
                return False
            else:
                print(f"❌ Errore sconosciuto: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        logger.error(f"Errore creazione tabella: {e}")
        return False

def print_sql_instructions():
    """Stampa le istruzioni SQL per creare la tabella"""
    
    sql = """
-- Creazione tabella broker_links per gestione link di affiliate
-- Esegui questo SQL nel SQL Editor di Supabase

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
"""
    
    print(sql)

def test_broker_links_table():
    """Testa la tabella broker_links dopo la creazione"""
    
    print("\n🧪 TEST TABELLA BROKER_LINKS")
    print("=" * 40)
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test lettura
        print("📖 Test lettura tabella...")
        result = supabase.table('broker_links').select('*').execute()
        print(f"✅ Lettura riuscita: {len(result.data)} record trovati")
        
        if result.data:
            for broker in result.data:
                print(f"   - {broker['broker_name']}: {broker['affiliate_link'][:50]}...")
        
        # Test inserimento
        print("\n➕ Test inserimento nuovo record...")
        test_data = {
            'broker_name': 'Test Broker Script',
            'affiliate_link': 'https://test-broker-script.com/affiliate/test',
            'created_by': 1
        }
        
        insert_result = supabase.table('broker_links').insert(test_data).execute()
        
        if insert_result.data:
            test_id = insert_result.data[0]['id']
            print(f"✅ Record inserito con ID: {test_id}")
            
            # Test aggiornamento
            print("✏️ Test aggiornamento record...")
            update_data = {'broker_name': 'Test Broker Script Updated'}
            update_result = supabase.table('broker_links').update(update_data).eq('id', test_id).execute()
            
            if update_result.data:
                print(f"✅ Record aggiornato: {update_result.data[0]['broker_name']}")
            
            # Test eliminazione
            print("🗑️ Test eliminazione record...")
            delete_result = supabase.table('broker_links').delete().eq('id', test_id).execute()
            
            if delete_result.data:
                print(f"✅ Record eliminato correttamente")
            
            print("\n🎉 TUTTI I TEST SUPERATI!")
            print("✅ Tabella broker_links funziona perfettamente")
            return True
        else:
            print("❌ Errore inserimento record di test")
            return False
            
    except Exception as e:
        print(f"❌ Errore test: {e}")
        return False

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script verificherà la tabella broker_links")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        if create_broker_links_table_simple():
            test_broker_links_table()
        else:
            print("\n❌ Tabella non trovata. Segui le istruzioni sopra per crearla manualmente.")
    else:
        print("❌ Operazione annullata")
