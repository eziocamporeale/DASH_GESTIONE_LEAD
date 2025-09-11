#!/usr/bin/env python3
"""
Script per creare le tabelle storage usando l'interfaccia SQL di Supabase
Creato da Ezio Camporeale per DASH_GESTIONE_LEAD
"""

import sys
from pathlib import Path
from supabase import create_client, Client
import requests
import json

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY

def create_storage_tables_via_sql():
    """
    Crea le tabelle usando l'interfaccia SQL di Supabase
    """
    try:
        print("🔄 Connessione a Supabase...")
        
        # Connessione a Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Leggi il file SQL
        sql_file = current_dir / "database" / "create_storage_table.sql"
        
        if not sql_file.exists():
            print("❌ File SQL non trovato:", sql_file)
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("📄 File SQL letto con successo")
        
        # Dividi le query per statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        print(f"🚀 Eseguendo {len(statements)} statement SQL...")
        
        # Esegui le query una per una usando l'API REST di Supabase
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            if statement and not statement.startswith('--'):
                print(f"   📝 Eseguendo statement {i}/{len(statements)}...")
                
                try:
                    # Usa l'endpoint SQL di Supabase
                    response = requests.post(
                        f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                        headers={
                            "apikey": SUPABASE_KEY,
                            "Authorization": f"Bearer {SUPABASE_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={"sql": statement}
                    )
                    
                    if response.status_code == 200:
                        print(f"   ✅ Statement {i} eseguito con successo")
                        success_count += 1
                    else:
                        print(f"   ⚠️ Statement {i} - Status: {response.status_code}")
                        if response.status_code == 404:
                            print(f"      Funzione exec_sql non disponibile, provo approccio alternativo...")
                            # Prova a eseguire direttamente le query DDL
                            if "CREATE TABLE" in statement.upper():
                                print(f"      ⚠️ Statement {i} richiede esecuzione manuale nel dashboard Supabase")
                        error_count += 1
                        
                except Exception as e:
                    print(f"   ❌ Statement {i} errore: {str(e)}")
                    error_count += 1
        
        print(f"\n📊 Risultati:")
        print(f"   ✅ Statement eseguiti: {success_count}")
        print(f"   ❌ Statement con errori: {error_count}")
        
        if error_count > 0:
            print("\n⚠️ Alcuni statement potrebbero richiedere esecuzione manuale")
            print("   Vai al dashboard Supabase > SQL Editor e esegui il file:")
            print(f"   {sql_file}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Errore durante la creazione delle tabelle: {str(e)}")
        return False

def create_tables_manually():
    """
    Crea le tabelle usando operazioni dirette di Supabase
    """
    try:
        print("\n🔄 Tentativo di creazione tabelle tramite API Supabase...")
        
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Prova a creare la tabella storage_files usando l'API
        print("📝 Creando tabella storage_files...")
        
        # Prima verifica se la tabella esiste già
        try:
            result = supabase.table('storage_files').select('id').limit(1).execute()
            print("✅ Tabella storage_files già esistente")
            return True
        except:
            print("📝 Tabella storage_files non trovata, creazione necessaria...")
        
        # Crea la tabella usando una query SQL semplificata
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS storage_files (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_size BIGINT NOT NULL,
            file_type VARCHAR(100) NOT NULL,
            category VARCHAR(50) DEFAULT 'Documenti',
            description TEXT,
            uploaded_by INTEGER NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            download_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Prova a eseguire la query
        try:
            # Usa l'endpoint SQL di Supabase
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={"sql": create_table_sql}
            )
            
            if response.status_code == 200:
                print("✅ Tabella storage_files creata con successo")
            else:
                print(f"❌ Errore creazione tabella: {response.status_code}")
                print("   Esegui manualmente nel dashboard Supabase:")
                print("   Dashboard > SQL Editor > New Query")
                print("   Incolla il contenuto di database/create_storage_table.sql")
                return False
                
        except Exception as e:
            print(f"❌ Errore API: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la creazione manuale: {str(e)}")
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

def print_manual_instructions():
    """
    Stampa le istruzioni per la creazione manuale delle tabelle
    """
    print("\n" + "="*60)
    print("📋 ISTRUZIONI PER CREAZIONE MANUALE DELLE TABELLE")
    print("="*60)
    print()
    print("1. Vai al dashboard Supabase:")
    print("   https://supabase.com/dashboard")
    print()
    print("2. Seleziona il tuo progetto")
    print()
    print("3. Vai a SQL Editor (icona </> nella sidebar)")
    print()
    print("4. Clicca su 'New Query'")
    print()
    print("5. Copia e incolla il contenuto del file:")
    print(f"   {current_dir}/database/create_storage_table.sql")
    print()
    print("6. Clicca su 'Run' per eseguire le query")
    print()
    print("7. Verifica che le tabelle siano state create:")
    print("   - storage_files")
    print("   - storage_downloads")
    print()
    print("8. Una volta create le tabelle, riprova lo script:")
    print("   python create_storage_tables_supabase.py")
    print()
    print("="*60)

if __name__ == "__main__":
    print("🚀 Inizializzazione Storage per DASH_GESTIONE_LEAD")
    print("=" * 50)
    
    # Prova prima con l'API
    if create_tables_manually():
        print("✅ Tabelle create con successo!")
        test_storage_functionality()
    else:
        print("❌ Creazione automatica fallita")
        print_manual_instructions()
    
    print("\n" + "=" * 50)
    print("✅ Script completato!")
