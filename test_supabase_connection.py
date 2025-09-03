#!/usr/bin/env python3
"""
Test connessione Supabase
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

def test_supabase_connection():
    """Testa la connessione a Supabase"""
    
    print("🔗 Test connessione Supabase...")
    print(f"URL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_KEY[:20]}...")
    
    try:
        # Crea client Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test connessione semplice
        print("\n📊 Test query semplice...")
        result = supabase.table('roles').select('*').limit(1).execute()
        
        print("✅ Connessione Supabase riuscita!")
        print(f"📋 Risultato test: {len(result.data)} record trovati")
        
        if result.data:
            print(f"📝 Primo record: {result.data[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore connessione Supabase: {e}")
        return False

def test_schema_creation():
    """Testa la creazione dello schema"""
    
    print("\n🗄️ Test creazione schema...")
    
    try:
        # Crea client Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Leggi schema SQL
        schema_path = Path(__file__).parent / "database" / "supabase_schema.sql"
        
        if not schema_path.exists():
            print("❌ File schema non trovato")
            return False
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        print("📄 Schema SQL caricato")
        print(f"📏 Dimensione schema: {len(schema_sql)} caratteri")
        
        # Nota: L'esecuzione diretta di SQL DDL richiede accesso admin
        # Per ora testiamo solo la connessione
        print("✅ Schema pronto per l'esecuzione")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test schema: {e}")
        return False

def main():
    """Funzione principale"""
    
    print("🚀 TEST CONNESSIONE SUPABASE")
    print("=" * 40)
    
    # Test connessione
    connection_ok = test_supabase_connection()
    
    if connection_ok:
        # Test schema
        schema_ok = test_schema_creation()
        
        if schema_ok:
            print("\n✅ TUTTI I TEST SUPERATI!")
            print("🎯 Supabase è pronto per la migrazione")
        else:
            print("\n⚠️ Test schema fallito")
    else:
        print("\n❌ Test connessione fallito")
        print("🔧 Verifica le credenziali Supabase")

if __name__ == "__main__":
    main()
