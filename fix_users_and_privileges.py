#!/usr/bin/env python3
"""
Script per correggere utenti e privilegi
- Elimina utenti di test
- Rimuove privilegi admin non necessari
- Sistema il meccanismo di creazione
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path
from datetime import datetime

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

def fix_users_and_privileges():
    """Corregge utenti e privilegi nel database"""
    
    print("🔧 CORREZIONE UTENTI E PRIVILEGI")
    print("=" * 50)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Crea client Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 1. Elimina utenti di test
        print("\n🗑️ 1. ELIMINAZIONE UTENTI DI TEST...")
        
        test_users = [
            'testuser',
            'testuser2', 
            'tester',
            'testuser_1758070472',
            'test_1758040678'
        ]
        
        deleted_count = 0
        for username in test_users:
            try:
                # Trova l'utente
                result = supabase.table('users').select('id, username').eq('username', username).execute()
                
                if result.data:
                    user_id = result.data[0]['id']
                    # Elimina l'utente
                    supabase.table('users').delete().eq('id', user_id).execute()
                    print(f"   ✅ Eliminato: {username} (ID: {user_id})")
                    deleted_count += 1
                else:
                    print(f"   ℹ️ Non trovato: {username}")
                    
            except Exception as e:
                print(f"   ❌ Errore eliminazione {username}: {e}")
        
        print(f"✅ Eliminati {deleted_count} utenti di test")
        
        # 2. Elimina utente anonimo
        print("\n🗑️ 2. ELIMINAZIONE UTENTE ANONIMO...")
        try:
            # Trova utente con username vuoto o null
            result = supabase.table('users').select('id, username').or_('username.is.null,username.eq.').execute()
            
            for user in result.data:
                if not user.get('username') or user.get('username').strip() == '':
                    user_id = user['id']
                    supabase.table('users').delete().eq('id', user_id).execute()
                    print(f"   ✅ Eliminato utente anonimo (ID: {user_id})")
                    
        except Exception as e:
            print(f"   ❌ Errore eliminazione utente anonimo: {e}")
        
        # 3. Rimuovi privilegi admin da tutti tranne admin@example.com
        print("\n🔐 3. CORREZIONE PRIVILEGI ADMIN...")
        
        try:
            # Ottieni tutti gli utenti con role_id = 1 (Admin)
            result = supabase.table('users').select('id, username, email, role_id').eq('role_id', 1).execute()
            
            for user in result.data:
                user_id = user['id']
                username = user['username']
                email = user['email']
                
                # Mantieni solo admin@example.com come admin
                if email != 'admin@example.com':
                    # Cambia role_id da 1 (Admin) a 2 (User)
                    supabase.table('users').update({
                        'role_id': 2,
                        'is_admin': False
                    }).eq('id', user_id).execute()
                    
                    print(f"   ✅ Rimosso admin da: {username} ({email}) - ora è User")
                else:
                    print(f"   ✅ Mantenuto admin: {username} ({email})")
                    
        except Exception as e:
            print(f"   ❌ Errore correzione privilegi: {e}")
        
        # 4. Verifica stato finale
        print("\n📊 4. VERIFICA STATO FINALE...")
        
        try:
            # Conta utenti per ruolo
            all_users = supabase.table('users').select('id, username, email, role_id, is_active').execute()
            
            admin_count = 0
            user_count = 0
            tester_count = 0
            
            print(f"\n👥 UTENTI FINALI ({len(all_users.data)} totali):")
            
            for user in all_users.data:
                username = user.get('username', 'N/A')
                email = user.get('email', 'N/A')
                role_id = user.get('role_id', 'N/A')
                is_active = user.get('is_active', False)
                
                if role_id == 1:
                    admin_count += 1
                    role_name = "Admin"
                    print(f"   👑 {username} ({email}) - {role_name}")
                elif role_id == 2:
                    user_count += 1
                    role_name = "User"
                    print(f"   👤 {username} ({email}) - {role_name}")
                elif role_id == 3:
                    tester_count += 1
                    role_name = "Tester"
                    print(f"   🧪 {username} ({email}) - {role_name}")
                else:
                    print(f"   ❓ {username} ({email}) - Role ID: {role_id}")
            
            print(f"\n📈 RIEPILOGO:")
            print(f"   👑 Admin: {admin_count}")
            print(f"   👤 User: {user_count}")
            print(f"   🧪 Tester: {tester_count}")
            
            if admin_count <= 2:
                print("   ✅ Numero admin corretto!")
            else:
                print("   ⚠️ Ancora troppi admin!")
                
        except Exception as e:
            print(f"   ❌ Errore verifica finale: {e}")
        
        print("\n✅ CORREZIONE COMPLETATA!")
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script modificherà il database!")
    print("   - Eliminerà utenti di test")
    print("   - Rimuoverà privilegi admin non necessari")
    print("   - Manterrà solo admin@example.com come admin")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        fix_users_and_privileges()
    else:
        print("❌ Operazione annullata")





