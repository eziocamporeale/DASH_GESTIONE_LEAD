#!/usr/bin/env python3
"""
Script per verificare la struttura della tabella users in Supabase
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

def check_users_structure():
    """Verifica la struttura della tabella users"""
    
    print("🔍 VERIFICA STRUTTURA TABELLA USERS")
    print("=" * 50)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connessione Supabase stabilita")
        
        # Prova a leggere dalla tabella users
        print("\n📖 Test lettura tabella users...")
        
        try:
            result = supabase.table('users').select('*').limit(1).execute()
            print(f"✅ Lettura riuscita: {len(result.data)} record trovati")
            
            if result.data:
                print("\n📋 Struttura colonne trovate:")
                for key in result.data[0].keys():
                    print(f"   - {key}: {type(result.data[0][key]).__name__}")
                
                # Verifica colonne specifiche
                sample_user = result.data[0]
                print("\n🔍 Verifica colonne specifiche:")
                
                if 'first_name' in sample_user:
                    print("   ✅ Colonna 'first_name' presente")
                else:
                    print("   ❌ Colonna 'first_name' NON presente")
                
                if 'last_name' in sample_user:
                    print("   ✅ Colonna 'last_name' presente")
                else:
                    print("   ❌ Colonna 'last_name' NON presente")
                
                if 'email' in sample_user:
                    print("   ✅ Colonna 'email' presente")
                else:
                    print("   ❌ Colonna 'email' NON presente")
                
                if 'password' in sample_user:
                    print("   ✅ Colonna 'password' presente")
                else:
                    print("   ❌ Colonna 'password' NON presente")
                
                if 'role_id' in sample_user:
                    print("   ✅ Colonna 'role_id' presente")
                else:
                    print("   ❌ Colonna 'role_id' NON presente")
                
            else:
                print("📭 Nessun record trovato nella tabella users")
                
        except Exception as e:
            print(f"❌ Errore lettura tabella users: {e}")
            return False
        
        # Test inserimento con struttura corretta
        print("\n🧪 Test inserimento user...")
        
        # Prova con struttura senza password
        test_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test.user@example.com',
            'role_id': 1,
            'is_active': True
        }
        
        try:
            result = supabase.table('users').insert(test_data).execute()
            if result.data:
                print("✅ Test inserimento riuscito")
                test_id = result.data[0]['id']
                
                # Elimina il record di test
                supabase.table('users').delete().eq('id', test_id).execute()
                print("✅ Record di test eliminato")
            else:
                print("❌ Test inserimento fallito")
                
        except Exception as e:
            print(f"❌ Errore test inserimento: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        logger.error(f"Errore verifica struttura: {e}")
        return False

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script verificherà la struttura della tabella users")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        check_users_structure()
    else:
        print("❌ Operazione annullata")
