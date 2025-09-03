#!/usr/bin/env python3
"""
Script per ottenere lo schema della tabella leads in Supabase
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

def get_leads_schema():
    """Ottiene lo schema della tabella leads"""
    
    print("🔍 OTTIENI SCHEMA TABELLA LEADS")
    print("=" * 50)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connessione Supabase stabilita")
        
        # Prova a ottenere informazioni sulla tabella
        print("\n📖 Informazioni tabella leads...")
        
        try:
            # Prova a inserire un record minimo per vedere la struttura
            minimal_data = {
                'name': 'Test',
                'email': 'test@test.com'
            }
            
            result = supabase.table('leads').insert(minimal_data).execute()
            if result.data:
                print("✅ Inserimento minimo riuscito")
                print("\n📋 Struttura colonne trovate:")
                for key in result.data[0].keys():
                    print(f"   - {key}: {type(result.data[0][key]).__name__}")
                
                # Elimina il record di test
                test_id = result.data[0]['id']
                supabase.table('leads').delete().eq('id', test_id).execute()
                print("✅ Record di test eliminato")
                
            else:
                print("❌ Inserimento minimo fallito")
                
        except Exception as e:
            print(f"❌ Errore inserimento minimo: {e}")
            
            # Prova a leggere la struttura da un record esistente
            try:
                result = supabase.table('leads').select('*').limit(1).execute()
                if result.data:
                    print("\n📋 Struttura da record esistente:")
                    for key in result.data[0].keys():
                        print(f"   - {key}: {type(result.data[0][key]).__name__}")
                else:
                    print("📭 Nessun record esistente per analizzare la struttura")
                    
            except Exception as e2:
                print(f"❌ Errore lettura struttura: {e2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        logger.error(f"Errore ottenimento schema: {e}")
        return False

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script analizzerà la struttura della tabella leads")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        get_leads_schema()
    else:
        print("❌ Operazione annullata")
