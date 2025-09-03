#!/usr/bin/env python3
"""
Script per verificare la struttura della tabella leads in Supabase
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

def check_leads_structure():
    """Verifica la struttura della tabella leads"""
    
    print("🔍 VERIFICA STRUTTURA TABELLA LEADS")
    print("=" * 50)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connessione Supabase stabilita")
        
        # Prova a leggere dalla tabella leads
        print("\n📖 Test lettura tabella leads...")
        
        try:
            result = supabase.table('leads').select('*').limit(1).execute()
            print(f"✅ Lettura riuscita: {len(result.data)} record trovati")
            
            if result.data:
                print("\n📋 Struttura colonne trovate:")
                for key in result.data[0].keys():
                    print(f"   - {key}: {type(result.data[0][key]).__name__}")
                
                # Verifica colonne specifiche
                sample_lead = result.data[0]
                print("\n🔍 Verifica colonne specifiche:")
                
                if 'name' in sample_lead:
                    print("   ✅ Colonna 'name' presente")
                else:
                    print("   ❌ Colonna 'name' NON presente")
                
                if 'first_name' in sample_lead:
                    print("   ✅ Colonna 'first_name' presente")
                else:
                    print("   ❌ Colonna 'first_name' NON presente")
                
                if 'last_name' in sample_lead:
                    print("   ✅ Colonna 'last_name' presente")
                else:
                    print("   ❌ Colonna 'last_name' NON presente")
                
                if 'email' in sample_lead:
                    print("   ✅ Colonna 'email' presente")
                else:
                    print("   ❌ Colonna 'email' NON presente")
                
                if 'phone' in sample_lead:
                    print("   ✅ Colonna 'phone' presente")
                else:
                    print("   ❌ Colonna 'phone' NON presente")
                
            else:
                print("📭 Nessun record trovato nella tabella leads")
                
        except Exception as e:
            print(f"❌ Errore lettura tabella leads: {e}")
            return False
        
        # Test inserimento con struttura corretta
        print("\n🧪 Test inserimento lead...")
        
        # Prova con struttura 'name'
        test_data_name = {
            'name': 'Test Lead Name',
            'email': 'test@example.com',
            'phone': '+39 123 456 7890',
            'company': 'Test Company',
            'lead_state_id': 1,
            'lead_priority_id': 1,
            'lead_category_id': 1,
            'lead_source_id': 1,
            'assigned_to': 1,
            'created_by': 1
        }
        
        try:
            result = supabase.table('leads').insert(test_data_name).execute()
            if result.data:
                print("✅ Test inserimento con 'name' riuscito")
                test_id = result.data[0]['id']
                
                # Elimina il record di test
                supabase.table('leads').delete().eq('id', test_id).execute()
                print("✅ Record di test eliminato")
            else:
                print("❌ Test inserimento con 'name' fallito")
                
        except Exception as e:
            print(f"❌ Errore test inserimento con 'name': {e}")
            
            # Prova con struttura 'first_name' + 'last_name'
            test_data_first_last = {
                'first_name': 'Test',
                'last_name': 'Lead',
                'email': 'test@example.com',
                'phone': '+39 123 456 7890',
                'company': 'Test Company',
                'lead_state_id': 1,
                'lead_priority_id': 1,
                'lead_category_id': 1,
                'lead_source_id': 1,
                'assigned_to': 1,
                'created_by': 1
            }
            
            try:
                result = supabase.table('leads').insert(test_data_first_last).execute()
                if result.data:
                    print("✅ Test inserimento con 'first_name'/'last_name' riuscito")
                    test_id = result.data[0]['id']
                    
                    # Elimina il record di test
                    supabase.table('leads').delete().eq('id', test_id).execute()
                    print("✅ Record di test eliminato")
                else:
                    print("❌ Test inserimento con 'first_name'/'last_name' fallito")
                    
            except Exception as e2:
                print(f"❌ Errore test inserimento con 'first_name'/'last_name': {e2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        logger.error(f"Errore verifica struttura: {e}")
        return False

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script verificherà la struttura della tabella leads")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        check_leads_structure()
    else:
        print("❌ Operazione annullata")
