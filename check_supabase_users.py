#!/usr/bin/env python3
"""
Verifica struttura tabella users in Supabase
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

def check_supabase_users():
    """Verifica la struttura della tabella users"""
    
    print("🔍 VERIFICA STRUTTURA TABELLA USERS SUPABASE")
    print("=" * 50)
    
    try:
        # Crea client Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Prova a ottenere un utente per vedere la struttura
        result = supabase.table('users').select('*').limit(1).execute()
        
        if result.data:
            user = result.data[0]
            print("📋 Struttura tabella users:")
            for key, value in user.items():
                print(f"   {key}: {type(value).__name__} = {value}")
        else:
            print("❌ Nessun utente trovato")
            
        # Prova a inserire un utente di test per vedere gli errori
        print("\n🧪 Test inserimento utente...")
        test_user = {
            'username': 'test_user',
            'email': 'test@test.com',
            'password_hash': 'test_hash',
            'role_id': 1,
            'is_active': True
        }
        
        try:
            result = supabase.table('users').insert(test_user).execute()
            print("✅ Inserimento test riuscito")
            
            # Elimina l'utente di test
            supabase.table('users').delete().eq('username', 'test_user').execute()
            print("🗑️ Utente test eliminato")
            
        except Exception as e:
            print(f"❌ Errore inserimento test: {e}")
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")

if __name__ == "__main__":
    check_supabase_users()
