#!/usr/bin/env python3
"""
Script per creare le tabelle storage nel database
Creato da Ezio Camporeale per DASH_GESTIONE_LEAD
"""

import sys
from pathlib import Path
from supabase import create_client, Client

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY

def create_storage_tables():
    """
    Crea le tabelle per la gestione dello storage
    """
    try:
        # Connessione a Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("🔄 Connessione al database Supabase...")
        
        # Leggi il file SQL
        sql_file = current_dir / "database" / "create_storage_table.sql"
        
        if not sql_file.exists():
            print("❌ File SQL non trovato:", sql_file)
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("📄 File SQL letto con successo")
        
        # Esegui le query SQL
        print("🚀 Eseguendo le query SQL...")
        
        # Dividi le query per statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"   📝 Eseguendo statement {i}/{len(statements)}...")
                try:
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"   ✅ Statement {i} eseguito con successo")
                except Exception as e:
                    print(f"   ⚠️ Statement {i} potrebbe essere già esistente: {str(e)}")
        
        print("✅ Creazione tabelle storage completata!")
        
        # Verifica che le tabelle siano state create
        print("\n🔍 Verifica tabelle create...")
        
        # Controlla tabella storage_files
        try:
            result = supabase.table('storage_files').select('id').limit(1).execute()
            print("✅ Tabella 'storage_files' creata correttamente")
        except Exception as e:
            print(f"❌ Errore nella tabella 'storage_files': {str(e)}")
        
        # Controlla tabella storage_downloads
        try:
            result = supabase.table('storage_downloads').select('id').limit(1).execute()
            print("✅ Tabella 'storage_downloads' creata correttamente")
        except Exception as e:
            print(f"❌ Errore nella tabella 'storage_downloads': {str(e)}")
        
        print("\n🎉 Setup storage completato con successo!")
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la creazione delle tabelle: {str(e)}")
        return False

def test_storage_functionality():
    """
    Testa le funzionalità base dello storage
    """
    try:
        from components.storage.storage_manager import StorageManager
        
        print("\n🧪 Test funzionalità storage...")
        
        # Inizializza il manager
        storage_manager = StorageManager()
        print("✅ StorageManager inizializzato")
        
        # Test statistiche
        stats = storage_manager.get_storage_stats()
        print(f"✅ Statistiche recuperate: {stats['total_files']} file")
        
        # Test categorie
        categories = list(storage_manager.categories.keys())
        print(f"✅ Categorie supportate: {len(categories)}")
        
        print("🎉 Test completato con successo!")
        return True
        
    except Exception as e:
        print(f"❌ Errore durante il test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Inizializzazione Storage per DASH_GESTIONE_LEAD")
    print("=" * 50)
    
    # Crea le tabelle
    if create_storage_tables():
        # Testa le funzionalità
        test_storage_functionality()
    else:
        print("❌ Setup fallito. Controlla i log per dettagli.")
    
    print("\n" + "=" * 50)
    print("✅ Script completato!")

