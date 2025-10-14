#!/usr/bin/env python3
"""
Script finale per pulire gli utenti di test
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

def clean_test_users_final():
    """Elimina gli utenti di test creati per il test"""
    
    print("🧹 PULIZIA FINALE UTENTI DI TEST")
    print("=" * 50)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Crea client Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Utenti di test da eliminare (email che finiscono con @test.com)
        print("\n🗑️ Eliminazione utenti di test...")
        
        try:
            # Trova tutti gli utenti con email @test.com
            result = supabase.table('users').select('id, username, email').ilike('email', '%@test.com').execute()
            
            if result.data:
                print(f"   📋 Trovati {len(result.data)} utenti di test:")
                
                for user in result.data:
                    user_id = user['id']
                    username = user['username']
                    email = user['email']
                    
                    print(f"   🗑️ Eliminando: {username} ({email})")
                    
                    # Elimina l'utente
                    try:
                        delete_result = supabase.table('users').delete().eq('id', user_id).execute()
                        print(f"   ✅ Eliminato: {username}")
                    except Exception as e:
                        print(f"   ❌ Errore eliminazione {username}: {e}")
            else:
                print("   ℹ️ Nessun utente di test trovato")
                
        except Exception as e:
            print(f"   ❌ Errore ricerca utenti di test: {e}")
        
        # Elimina anche utenti con username che contengono "test"
        print("\n🗑️ Eliminazione utenti con username test...")
        
        test_usernames = [
            'testuser2',
            'tester', 
            'testuser_1758070472',
            'test_1758040678'
        ]
        
        for username in test_usernames:
            try:
                # Trova l'utente
                user_result = supabase.table('users').select('id, username, email').eq('username', username).execute()
                
                if user_result.data:
                    user = user_result.data[0]
                    user_id = user['id']
                    email = user['email']
                    
                    print(f"   🗑️ Eliminando: {username} ({email})")
                    
                    # Elimina l'utente
                    delete_result = supabase.table('users').delete().eq('id', user_id).execute()
                    print(f"   ✅ Eliminato: {username}")
                else:
                    print(f"   ℹ️ {username} non trovato")
                    
            except Exception as e:
                print(f"   ❌ Errore eliminazione {username}: {e}")
        
        # Elimina utente anonimo
        print("\n🗑️ Eliminazione utente anonimo...")
        try:
            # Trova utente con username vuoto o null
            user_result = supabase.table('users').select('id, username, email').or_('username.is.null,username.eq.').execute()
            
            for user in user_result.data:
                if not user.get('username') or user.get('username').strip() == '':
                    user_id = user['id']
                    email = user.get('email', 'N/A')
                    
                    print(f"   🗑️ Eliminando utente anonimo (ID: {user_id}, Email: {email})")
                    
                    # Elimina l'utente
                    delete_result = supabase.table('users').delete().eq('id', user_id).execute()
                    print(f"   ✅ Utente anonimo eliminato")
                    
        except Exception as e:
            print(f"   ❌ Errore eliminazione utente anonimo: {e}")
        
        # Verifica finale
        print(f"\n📊 VERIFICA FINALE...")
        try:
            all_users = supabase.table('users').select('id, username, email, role_id, is_admin').execute()
            
            admin_count = 0
            user_count = 0
            tester_count = 0
            
            print(f"\n👥 UTENTI FINALI ({len(all_users.data)} totali):")
            
            for user in all_users.data:
                username = user.get('username', 'N/A')
                email = user.get('email', 'N/A')
                role_id = user.get('role_id', 'N/A')
                is_admin = user.get('is_admin', False)
                
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
            
            print(f"\n📈 RIEPILOGO FINALE:")
            print(f"   👑 Admin: {admin_count}")
            print(f"   👤 User: {user_count}")
            print(f"   🧪 Tester: {tester_count}")
            
            if admin_count <= 2:
                print("   ✅ Numero admin corretto!")
            else:
                print("   ⚠️ Ancora troppi admin!")
                
        except Exception as e:
            print(f"   ❌ Errore verifica finale: {e}")
        
        print("\n✅ PULIZIA FINALE COMPLETATA!")
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script eliminerà definitivamente:")
    print("   - Tutti gli utenti con email @test.com")
    print("   - Utenti con username contenente 'test'")
    print("   - Utente anonimo")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        clean_test_users_final()
    else:
        print("❌ Operazione annullata")





