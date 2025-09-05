#!/usr/bin/env python3
"""
Script per cambiare la password dell'admin
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import AuthManager

def change_admin_password():
    """Cambia la password dell'admin"""
    
    print("🔐 Cambio password admin...")
    
    # Inizializza i manager
    db = DatabaseManager()
    auth_manager = AuthManager()
    
    try:
        # Nuova password admin
        new_password = "Vtmarkets12!"
        
        print(f"🔧 Aggiornamento password admin con: {new_password}")
        
        # Hash della nuova password
        new_hash = auth_manager.hash_password(new_password)
        
        # Aggiorna la password nel database
        result = db.supabase.table('users').update({
            'password_hash': new_hash
        }).eq('username', 'admin').execute()
        
        if result.data:
            print("✅ Password admin aggiornata con successo!")
            
            # Test della nuova password
            print("\n🧪 Test login con nuova password...")
            login_result = auth_manager.login('admin', new_password)
            
            if login_result:
                print("✅ Login admin con nuova password: SUCCESSO")
                print(f"   Username: {login_result['username']}")
                print(f"   Role: {login_result['role_name']}")
            else:
                print("❌ Login admin con nuova password: FALLITO")
        else:
            print("❌ Errore nell'aggiornamento della password admin")
    
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    change_admin_password()
