#!/usr/bin/env python3
"""
Script per eliminare utenti di test e i loro riferimenti
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

def clean_test_users_with_references():
    """Elimina utenti di test e tutti i loro riferimenti"""
    
    print("🧹 PULIZIA UTENTI DI TEST CON RIFERIMENTI")
    print("=" * 50)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Crea client Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Utenti di test da eliminare
        test_users = [
            'testuser2',
            'tester', 
            'testuser_1758070472',
            'test_1758040678'
        ]
        
        for username in test_users:
            print(f"\n🗑️ Pulizia utente: {username}")
            
            try:
                # Trova l'utente
                user_result = supabase.table('users').select('id').eq('username', username).execute()
                
                if not user_result.data:
                    print(f"   ℹ️ Utente {username} non trovato")
                    continue
                
                user_id = user_result.data[0]['id']
                print(f"   🆔 User ID: {user_id}")
                
                # 1. Elimina activity_log
                try:
                    activity_result = supabase.table('activity_log').delete().eq('user_id', user_id).execute()
                    print(f"   ✅ Eliminati {len(activity_result.data) if activity_result.data else 0} record da activity_log")
                except Exception as e:
                    print(f"   ⚠️ Errore activity_log: {e}")
                
                # 2. Aggiorna leads che hanno questo utente come assigned_to
                try:
                    leads_result = supabase.table('leads').update({'assigned_to': None}).eq('assigned_to', user_id).execute()
                    print(f"   ✅ Aggiornati {len(leads_result.data) if leads_result.data else 0} leads (assigned_to = null)")
                except Exception as e:
                    print(f"   ⚠️ Errore leads: {e}")
                
                # 3. Aggiorna tasks che hanno questo utente come assigned_to
                try:
                    tasks_result = supabase.table('tasks').update({'assigned_to': None}).eq('assigned_to', user_id).execute()
                    print(f"   ✅ Aggiornati {len(tasks_result.data) if tasks_result.data else 0} tasks (assigned_to = null)")
                except Exception as e:
                    print(f"   ⚠️ Errore tasks: {e}")
                
                # 4. Elimina l'utente
                try:
                    delete_result = supabase.table('users').delete().eq('id', user_id).execute()
                    print(f"   ✅ Utente {username} eliminato con successo")
                except Exception as e:
                    print(f"   ❌ Errore eliminazione utente: {e}")
                    
            except Exception as e:
                print(f"   ❌ Errore generale per {username}: {e}")
        
        # Pulizia utente anonimo
        print(f"\n🗑️ Pulizia utente anonimo...")
        try:
            # Trova utente con username vuoto
            user_result = supabase.table('users').select('id').or_('username.is.null,username.eq.').execute()
            
            for user in user_result.data:
                user_id = user['id']
                print(f"   🆔 User ID anonimo: {user_id}")
                
                # Aggiorna leads
                leads_result = supabase.table('leads').update({'assigned_to': None}).eq('assigned_to', user_id).execute()
                print(f"   ✅ Aggiornati {len(leads_result.data) if leads_result.data else 0} leads")
                
                # Elimina utente
                delete_result = supabase.table('users').delete().eq('id', user_id).execute()
                print(f"   ✅ Utente anonimo eliminato")
                
        except Exception as e:
            print(f"   ❌ Errore pulizia utente anonimo: {e}")
        
        # Verifica finale
        print(f"\n📊 VERIFICA FINALE...")
        try:
            all_users = supabase.table('users').select('id, username, email, role_id, is_active').execute()
            
            admin_count = 0
            user_count = 0
            tester_count = 0
            
            print(f"\n👥 UTENTI FINALI ({len(all_users.data)} totali):")
            
            for user in all_users.data:
                username = user.get('username', 'N/A')
                email = user.get('email', 'N/A')
                role_id = user.get('role_id', 'N/A')
                
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
            
        except Exception as e:
            print(f"   ❌ Errore verifica finale: {e}")
        
        print("\n✅ PULIZIA COMPLETATA!")
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script eliminerà definitivamente:")
    print("   - Utenti di test e tutti i loro dati collegati")
    print("   - Riferimenti in activity_log, leads, tasks")
    print("   - Utente anonimo")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        clean_test_users_with_references()
    else:
        print("❌ Operazione annullata")





