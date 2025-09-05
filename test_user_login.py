#!/usr/bin/env python3
"""
Script per testare il login degli utenti e correggere le password
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path
import bcrypt

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import AuthManager

def test_user_passwords():
    """Testa le password degli utenti e le corregge se necessario"""
    
    print("🔍 Test password utenti...")
    
    # Inizializza i manager
    db = DatabaseManager()
    auth_manager = AuthManager()
    
    try:
        # Ottieni tutti gli utenti
        users = db.get_all_users()
        
        if not users:
            print("❌ Nessun utente trovato")
            return
        
        print(f"📊 Trovati {len(users)} utenti")
        
        for user in users:
            username = user['username']
            password_hash = user['password_hash']
            
            print(f"\n👤 Test utente: {username}")
            print(f"   📧 Email: {user['email']}")
            print(f"   🔑 Hash: {password_hash[:20]}...")
            
            # Test con password comuni
            test_passwords = [
                "admin123",  # Password admin
                "password",  # Password generica
                "123456",    # Password semplice
                username,    # Username come password
                "test123"    # Password di test
            ]
            
            password_found = False
            for test_password in test_passwords:
                try:
                    if auth_manager.verify_password(test_password, password_hash):
                        print(f"   ✅ Password trovata: {test_password}")
                        password_found = True
                        break
                except Exception as e:
                    print(f"   ❌ Errore verifica password '{test_password}': {e}")
            
            if not password_found:
                print(f"   ⚠️ Password non riconosciuta")
                
                # Prova a correggere con una password di default
                new_password = "password123"  # Password di default per tutti
                new_hash = auth_manager.hash_password(new_password)
                
                print(f"   🔧 Correzione password con: {new_password}")
                
                # Aggiorna la password nel database
                try:
                    db.supabase.table('users').update({
                        'password_hash': new_hash
                    }).eq('id', user['id']).execute()
                    
                    print(f"   ✅ Password aggiornata per {username}")
                    
                except Exception as e:
                    print(f"   ❌ Errore aggiornamento password: {e}")
        
        print("\n🎯 Test completato!")
        
        # Test finale con le password corrette
        print("\n🧪 Test finale login...")
        for user in users:
            username = user['username']
            test_password = "password123"
            
            try:
                login_result = auth_manager.login(username, test_password)
                if login_result:
                    print(f"✅ Login {username}: SUCCESSO")
                else:
                    print(f"❌ Login {username}: FALLITO")
            except Exception as e:
                print(f"❌ Errore login {username}: {e}")
    
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_passwords()
