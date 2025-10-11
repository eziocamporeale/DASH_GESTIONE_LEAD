#!/usr/bin/env python3
"""
Test della funzionalità di eliminazione utenti
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path
from datetime import datetime

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import AuthManager

def test_delete_functionality():
    """Testa la funzionalità di eliminazione utenti"""
    
    print("🗑️ TEST FUNZIONALITÀ ELIMINAZIONE UTENTI")
    print("=" * 50)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Inizializza manager
        db = DatabaseManager()
        auth_manager = AuthManager()
        
        # Test 1: Creare utenti di test
        print("\n🧪 TEST 1: Creazione utenti di test")
        
        import time
        timestamp = int(time.time())
        
        # Crea utente admin di test
        admin_data = {
            'first_name': 'Test',
            'last_name': 'Admin',
            'email': f'test.admin.{timestamp}@example.com',
            'username': f'testadmin.{timestamp}',
            'password': 'password123',
            'role_id': 1,
            'department_id': 1,
            'is_active': True,
            'is_admin': True
        }
        
        admin_id = db.create_user(admin_data, 'Admin')
        if admin_id:
            print(f"   ✅ Admin di test creato (ID: {admin_id})")
        else:
            print(f"   ❌ Errore creazione admin di test")
            return
        
        # Crea utenti normali di test
        users_to_delete = []
        for i in range(3):
            user_data = {
                'first_name': f'Test',
                'last_name': f'User{i+1}',
                'email': f'test.user{i+1}.{timestamp}@example.com',
                'username': f'testuser{i+1}.{timestamp}',
                'password': 'password123',
                'role_id': 2,
                'department_id': 1,
                'is_active': True,
                'is_admin': False
            }
            
            user_id = db.create_user(user_data, 'Admin')
            if user_id:
                users_to_delete.append(user_id)
                print(f"   ✅ User{i+1} di test creato (ID: {user_id})")
            else:
                print(f"   ❌ Errore creazione User{i+1}")
        
        # Test 2: Verifica che gli utenti esistano
        print(f"\n🧪 TEST 2: Verifica esistenza utenti")
        
        all_users = db.get_all_users()
        test_users = [u for u in all_users if u.get('email', '').endswith(f'@{timestamp}@example.com'.replace('@', ''))]
        
        print(f"   📊 Utenti di test trovati: {len(test_users)}")
        for user in test_users:
            print(f"   👤 {user.get('username', 'N/A')} (ID: {user.get('id', 'N/A')})")
        
        # Test 3: Test eliminazione utenti
        print(f"\n🧪 TEST 3: Test eliminazione utenti")
        
        for user_id in users_to_delete:
            print(f"   🗑️ Eliminando utente ID: {user_id}")
            
            # Prova a eliminare l'utente
            success = db.delete_user(user_id)
            
            if success:
                print(f"   ✅ Utente {user_id} eliminato con successo")
                
                # Verifica che sia stato eliminato
                user_check = db.get_user(user_id)
                if not user_check:
                    print(f"   ✅ Verificato: utente {user_id} non esiste più")
                else:
                    print(f"   ❌ PROBLEMA: utente {user_id} ancora presente")
            else:
                print(f"   ❌ Errore eliminazione utente {user_id}")
        
        # Test 4: Test eliminazione admin (dovrebbe fallire o essere limitata)
        print(f"\n🧪 TEST 4: Test eliminazione admin")
        
        print(f"   🗑️ Tentativo eliminazione admin ID: {admin_id}")
        success = db.delete_user(admin_id)
        
        if success:
            print(f"   ⚠️ ATTENZIONE: Admin {admin_id} eliminato (potrebbe essere un problema di sicurezza)")
        else:
            print(f"   ✅ Admin {admin_id} protetto dall'eliminazione")
        
        # Test 5: Verifica stato finale
        print(f"\n🧪 TEST 5: Verifica stato finale")
        
        final_users = db.get_all_users()
        remaining_test_users = [u for u in final_users if u.get('email', '').endswith(f'@{timestamp}@example.com'.replace('@', ''))]
        
        print(f"   📊 Utenti di test rimanenti: {len(remaining_test_users)}")
        
        if len(remaining_test_users) == 0:
            print(f"   ✅ Tutti gli utenti di test eliminati con successo")
        else:
            print(f"   ⚠️ Alcuni utenti di test non eliminati:")
            for user in remaining_test_users:
                print(f"      👤 {user.get('username', 'N/A')} (ID: {user.get('id', 'N/A')})")
        
        # Test 6: Test eliminazione utente inesistente
        print(f"\n🧪 TEST 6: Test eliminazione utente inesistente")
        
        fake_user_id = 99999
        success = db.delete_user(fake_user_id)
        
        if success:
            print(f"   ❌ PROBLEMA: Eliminazione utente inesistente riuscita")
        else:
            print(f"   ✅ Eliminazione utente inesistente fallita correttamente")
        
        print("\n✅ TEST ELIMINAZIONE UTENTI COMPLETATO!")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script testerà la funzionalità di eliminazione utenti!")
    print("   Verranno creati e eliminati utenti di test")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        test_delete_functionality()
    else:
        print("❌ Test annullato")
