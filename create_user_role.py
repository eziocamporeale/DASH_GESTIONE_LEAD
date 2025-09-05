#!/usr/bin/env python3
"""
Script per creare il ruolo User mancante
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path
import json

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager

def create_user_role():
    """Crea il ruolo User mancante"""
    
    print("🔧 Creazione ruolo User...")
    
    # Inizializza il database manager
    db = DatabaseManager()
    
    try:
        # Controlla se il ruolo User esiste già
        existing_roles = db.get_roles()
        print("📋 Ruoli esistenti:")
        for role in existing_roles:
            print(f"   ID {role['id']}: {role['name']}")
        
        # Cerca se esiste già un ruolo User
        user_role_exists = any(role['name'].lower() == 'user' for role in existing_roles)
        
        if user_role_exists:
            print("✅ Ruolo 'User' già esistente!")
        else:
            print("\n🔧 Creazione nuovo ruolo 'User'...")
            
            # Permessi per il ruolo User
            user_permissions = [
                "view_leads",
                "edit_assigned_leads", 
                "view_tasks",
                "edit_assigned_tasks",
                "view_contacts",
                "view_reports"
            ]
            
            # Crea il ruolo User
            try:
                result = db.supabase.table('roles').insert({
                    'name': 'User',
                    'description': 'Utente standard con permessi limitati',
                    'permissions': json.dumps(user_permissions)
                }).execute()
                
                if result.data:
                    print("✅ Ruolo 'User' creato con successo!")
                    print(f"   ID: {result.data[0]['id']}")
                    print(f"   Permessi: {user_permissions}")
                else:
                    print("❌ Errore nella creazione del ruolo 'User'")
                    
            except Exception as e:
                print(f"❌ Errore nella creazione del ruolo: {e}")
        
        # Ora correggi i ruoli degli utenti
        print("\n🔧 Correzione ruoli utenti...")
        
        # Ottieni i ruoli aggiornati
        updated_roles = db.get_roles()
        user_role_id = None
        
        for role in updated_roles:
            if role['name'].lower() == 'user':
                user_role_id = role['id']
                break
        
        if not user_role_id:
            print("❌ Ruolo 'User' non trovato dopo la creazione!")
            return
        
        print(f"✅ Ruolo 'User' trovato con ID: {user_role_id}")
        
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
    create_user_role()
