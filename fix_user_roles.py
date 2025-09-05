#!/usr/bin/env python3
"""
Script per correggere i ruoli degli utenti
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager

def fix_user_roles():
    """Corregge i ruoli degli utenti"""
    
    print("🔧 Correzione ruoli utenti...")
    
    # Inizializza il database manager
    db = DatabaseManager()
    
    try:
        # Ottieni tutti i ruoli disponibili
        roles = db.get_roles()
        print("📋 Ruoli disponibili:")
        for role in roles:
            print(f"   ID {role['id']}: {role['name']}")
        
        # Trova l'ID del ruolo "User"
        user_role_id = None
        for role in roles:
            if role['name'].lower() == 'user':
                user_role_id = role['id']
                break
        
        if not user_role_id:
            print("❌ Ruolo 'User' non trovato!")
            return
        
        print(f"\n✅ Ruolo 'User' trovato con ID: {user_role_id}")
        
        # Correggi i ruoli degli utenti non-admin
        users_to_fix = ['simone', 'marco']
        
        for username in users_to_fix:
            print(f"\n🔧 Correzione ruolo per {username}...")
            
            try:
                # Aggiorna il ruolo nel database
                result = db.supabase.table('users').update({
                    'role_id': user_role_id
                }).eq('username', username).execute()
                
                if result.data:
                    print(f"   ✅ Ruolo aggiornato per {username}: Admin → User")
                else:
                    print(f"   ❌ Errore aggiornamento ruolo per {username}")
                    
            except Exception as e:
                print(f"   ❌ Errore aggiornamento ruolo per {username}: {e}")
        
        print("\n🎯 Correzione completata!")
        
        # Verifica finale
        print("\n🔍 Verifica finale ruoli...")
        users = db.get_all_users()
        
        for user in users:
            role_name = user.get('role_name', 'N/A')
            if user['username'] == 'admin':
                expected_role = 'Admin'
            else:
                expected_role = 'User'
            
            status = "✅" if role_name == expected_role else "❌"
            print(f"   {status} {user['username']}: {role_name} (atteso: {expected_role})")
    
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_user_roles()
