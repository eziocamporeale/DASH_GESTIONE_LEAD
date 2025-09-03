#!/usr/bin/env python3
"""
Script per verificare la tabella scripts in Supabase
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

def check_scripts_table():
    """Verifica se la tabella scripts esiste"""
    
    print("📝 VERIFICA TABELLA SCRIPTS")
    print("=" * 50)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connessione Supabase stabilita")
        
        # Prova a leggere dalla tabella
        print("\n🔍 Verifica esistenza tabella...")
        
        try:
            result = supabase.table('scripts').select('*').limit(1).execute()
            print("✅ Tabella scripts già esistente")
            return True
        except Exception as e:
            if "Could not find the table" in str(e):
                print("❌ Tabella scripts non trovata")
                print("⚠️ La tabella deve essere creata manualmente in Supabase")
                print("\n📋 ISTRUZIONI PER CREARE LA TABELLA:")
                print("1. Vai su https://supabase.com/dashboard")
                print("2. Seleziona il tuo progetto")
                print("3. Vai su 'SQL Editor'")
                print("4. Copia e incolla il seguente SQL:")
                print("\n" + "=" * 60)
                print_sql_instructions()
                print("=" * 60)
                return False
            else:
                print(f"❌ Errore sconosciuto: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        logger.error(f"Errore verifica tabella: {e}")
        return False

def print_sql_instructions():
    """Stampa le istruzioni SQL per creare la tabella"""
    
    sql = """
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
"""
    
    print(sql)

def test_scripts_table():
    """Testa la tabella scripts dopo la creazione"""
    
    print("\n🧪 TEST TABELLA SCRIPTS")
    print("=" * 40)
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test lettura
        print("📖 Test lettura tabella...")
        result = supabase.table('scripts').select('*').execute()
        print(f"✅ Lettura riuscita: {len(result.data)} record trovati")
        
        if result.data:
            for script in result.data:
                print(f"   - {script['title']}: {script['script_type']} ({script['category']})")
        
        print("✅ Test di lettura completato con successo!")
        print("✅ Tabella scripts funziona correttamente")
        return True
            
    except Exception as e:
        print(f"❌ Errore test: {e}")
        return False

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script verificherà la tabella scripts")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        if check_scripts_table():
            test_scripts_table()
        else:
            print("\n❌ Tabella non trovata. Segui le istruzioni sopra per crearla manualmente.")
    else:
        print("❌ Operazione annullata")
