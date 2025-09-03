#!/usr/bin/env python3
"""
Test login admin
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path
import bcrypt

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

def test_admin_login():
    """Testa il login dell'admin"""
    
    print("🔐 TEST LOGIN ADMIN")
    print("=" * 30)
    
    try:
        # Crea client Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Cerca l'utente admin
        result = supabase.table('users').select('*').eq('username', 'admin').execute()
        
        if result.data:
            admin_user = result.data[0]
            print(f"✅ Utente admin trovato:")
            print(f"   ID: {admin_user['id']}")
            print(f"   Username: {admin_user['username']}")
            print(f"   Email: {admin_user['email']}")
            print(f"   First Name: {admin_user['first_name']}")
            print(f"   Last Name: {admin_user['last_name']}")
            print(f"   Role ID: {admin_user['role_id']}")
            print(f"   Is Active: {admin_user['is_active']}")
            print(f"   Password Hash: {admin_user['password_hash'][:20]}...")
            
            # Test verifica password
            test_password = "test_password"  # Password di test
            hashed_password = admin_user['password_hash']
            
            try:
                is_valid = bcrypt.checkpw(test_password.encode('utf-8'), hashed_password.encode('utf-8'))
                print(f"\n🔑 Test password '{test_password}': {'✅ Valida' if is_valid else '❌ Non valida'}")
                
                if not is_valid:
                    print("\n🔄 Ricreando password hash per admin...")
                    new_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                    # Aggiorna la password
                    result = supabase.table('users').update({
                        'password_hash': new_hash
                    }).eq('id', admin_user['id']).execute()
                    
                    if result.data:
                        print("✅ Password admin aggiornata!")
                    else:
                        print("❌ Errore aggiornamento password")
                        
            except Exception as e:
                print(f"❌ Errore verifica password: {e}")
                
        else:
            print("❌ Utente admin non trovato")
            
    except Exception as e:
        print(f"❌ Errore generale: {e}")

if __name__ == "__main__":
    test_admin_login()
