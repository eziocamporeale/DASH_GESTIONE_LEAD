#!/usr/bin/env python3
"""
Script per testare la creazione di utenti con la struttura corretta
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client
from database.database_manager import DatabaseManager

def test_user_creation():
    """Testa la creazione di utenti con la struttura corretta"""
    
    print("🧪 TEST CREAZIONE UTENTI")
    print("=" * 50)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        db = DatabaseManager()
        
        print("✅ Connessione Supabase stabilita")
        
        # Test con struttura corretta
        print("\n📝 Test creazione utente con struttura corretta...")
        
        test_data = {
            'username': 'test.user',
            'email': 'test.user@example.com',
            'password_hash': 'test_password_hash',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+39 123 456 7890',
            'role_id': 1,
            'is_active': True,
            'is_admin': False,
            'notes': 'Utente di test',
            'department_id': None,
            'created_by': 1
        }
        
        if db.create_user(test_data):
            print("✅ Test creazione utente riuscito")
            
            # Verifica che l'utente sia stato creato
            print("\n🔍 Verifica creazione...")
            result = supabase.table('users').select('*').eq('username', 'test.user').execute()
            
            if result.data:
                user = result.data[0]
                print(f"   ✅ Utente trovato: ID {user['id']}")
                print(f"   Nome: {user['first_name']} {user['last_name']}")
                print(f"   Email: {user['email']}")
                print(f"   Username: {user['username']}")
                
                # Elimina l'utente di test
                supabase.table('users').delete().eq('id', user['id']).execute()
                print("   ✅ Utente di test eliminato")
            else:
                print("   ❌ Utente non trovato")
        else:
            print("❌ Test creazione utente fallito")
            
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_creation()
