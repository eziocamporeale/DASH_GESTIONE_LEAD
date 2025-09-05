#!/usr/bin/env python3
"""
Script per controllare i ruoli degli utenti
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager

def check_user_roles():
    """Controlla i ruoli di tutti gli utenti"""
    
    print("🔍 Controllo ruoli utenti...")
    
    # Inizializza il database manager
    db = DatabaseManager()
    
    try:
        # Ottieni tutti gli utenti con i loro ruoli
        users = db.get_all_users()
        
        if not users:
            print("❌ Nessun utente trovato")
            return
        
        print(f"📊 Trovati {len(users)} utenti")
        print("\n" + "="*60)
        
        for user in users:
            print(f"\n👤 Utente: {user['username']}")
            print(f"   📧 Email: {user['email']}")
            print(f"   🆔 ID: {user['id']}")
            print(f"   🔑 Role ID: {user['role_id']}")
            print(f"   🏷️ Role Name: {user.get('role_name', 'N/A')}")
            print(f"   🏢 Department ID: {user.get('department_id', 'N/A')}")
            print(f"   🏢 Department Name: {user.get('department_name', 'N/A')}")
            print(f"   ✅ Attivo: {user.get('is_active', 'N/A')}")
            
            # Controlla se è admin
            if user.get('role_name') == 'Admin':
                print(f"   🚨 ⚠️  QUESTO UTENTE È ADMIN!")
            else:
                print(f"   ✅ Utente normale")
        
        print("\n" + "="*60)
        print("🎯 Controllo completato!")
        
        # Controlla specificamente marco
        marco_user = next((u for u in users if u['username'] == 'marco'), None)
        if marco_user:
            print(f"\n🔍 DETTAGLI MARCO:")
            print(f"   Username: {marco_user['username']}")
            print(f"   Role ID: {marco_user['role_id']}")
            print(f"   Role Name: {marco_user.get('role_name', 'N/A')}")
            
            if marco_user.get('role_name') == 'Admin':
                print(f"   🚨 PROBLEMA: Marco è configurato come Admin!")
                print(f"   🔧 SOLUZIONE: Cambiare il role_id di marco da {marco_user['role_id']} a 2 (User)")
            else:
                print(f"   ✅ Marco non è Admin")
    
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_user_roles()
