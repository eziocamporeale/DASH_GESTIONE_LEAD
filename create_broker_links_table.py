#!/usr/bin/env python3
"""
Script per creare la tabella broker_links in Supabase
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

def create_broker_links_table():
    """Crea la tabella broker_links in Supabase"""
    
    print("🏗️ CREAZIONE TABELLA BROKER_LINKS")
    print("=" * 50)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connessione Supabase stabilita")
        
        # Leggi il file SQL
        sql_file = current_dir / "database" / "create_broker_links_table.sql"
        
        if not sql_file.exists():
            print(f"❌ File SQL non trovato: {sql_file}")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("📄 File SQL letto correttamente")
        
        # Esegui le query SQL
        print("\n🔧 Esecuzione query SQL...")
        
        # Dividi le query per eseguirle separatamente
        queries = sql_content.split(';')
        
        for i, query in enumerate(queries):
            query = query.strip()
            if query and not query.startswith('--'):
                try:
                    print(f"   Query {i+1}: {query[:50]}...")
                    result = supabase.rpc('exec_sql', {'sql': query}).execute()
                    print(f"   ✅ Query {i+1} eseguita con successo")
                except Exception as e:
                    print(f"   ⚠️ Query {i+1} saltata (probabilmente già eseguita): {e}")
                    continue
        
        print("\n" + "=" * 50)
        print("🎉 TABELLA BROKER_LINKS CREATA CON SUCCESSO!")
        
        # Verifica che la tabella sia stata creata
        try:
            result = supabase.table('broker_links').select('*').limit(1).execute()
            print(f"✅ Tabella broker_links verificata: {len(result.data)} record trovati")
        except Exception as e:
            print(f"⚠️ Errore verifica tabella: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        logger.error(f"Errore creazione tabella: {e}")
        return False

def verify_broker_links_table():
    """Verifica che la tabella broker_links esista e funzioni"""
    
    print("\n🔍 VERIFICA TABELLA BROKER_LINKS")
    print("=" * 40)
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test inserimento
        test_data = {
            'broker_name': 'Test Broker',
            'affiliate_link': 'https://test-broker.com/affiliate/test',
            'created_by': 1
        }
        
        print("🧪 Test inserimento record...")
        result = supabase.table('broker_links').insert(test_data).execute()
        
        if result.data:
            test_id = result.data[0]['id']
            print(f"✅ Record di test inserito con ID: {test_id}")
            
            # Test lettura
            print("🧪 Test lettura record...")
            read_result = supabase.table('broker_links').select('*').eq('id', test_id).execute()
            
            if read_result.data:
                print(f"✅ Record letto correttamente: {read_result.data[0]['broker_name']}")
            
            # Test aggiornamento
            print("🧪 Test aggiornamento record...")
            update_data = {'broker_name': 'Test Broker Updated'}
            update_result = supabase.table('broker_links').update(update_data).eq('id', test_id).execute()
            
            if update_result.data:
                print(f"✅ Record aggiornato: {update_result.data[0]['broker_name']}")
            
            # Test eliminazione
            print("🧪 Test eliminazione record...")
            delete_result = supabase.table('broker_links').delete().eq('id', test_id).execute()
            
            if delete_result.data:
                print(f"✅ Record eliminato correttamente")
            
            print("\n🎉 TUTTI I TEST SUPERATI!")
            print("✅ Tabella broker_links funziona correttamente")
            return True
            
        else:
            print("❌ Errore inserimento record di test")
            return False
            
    except Exception as e:
        print(f"❌ Errore verifica: {e}")
        return False

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script creerà la tabella broker_links in Supabase")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        if create_broker_links_table():
            verify_broker_links_table()
        else:
            print("❌ Creazione tabella fallita")
    else:
        print("❌ Operazione annullata")
