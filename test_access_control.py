#!/usr/bin/env python3
"""
Test dei controlli di accesso per la gestione utenti
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path
from datetime import datetime

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from components.auth.auth_manager import AuthManager
from database.database_manager import DatabaseManager

def test_access_control():
    """Testa i controlli di accesso per la gestione utenti"""
    
    print("🔒 TEST CONTROLLI DI ACCESSO")
    print("=" * 50)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Inizializza manager
        auth_manager = AuthManager()
        db = DatabaseManager()
        
        # Test 1: Login come Admin di test
        print("\n🧪 TEST 1: Login come Admin di test")
        admin_result = auth_manager.login('testadmin', 'password123')
        
        if admin_result:
            print(f"   ✅ Login Admin riuscito")
            print(f"   👤 Username: {admin_result.get('username')}")
            print(f"   👑 Role: {admin_result.get('role_name')}")
            print(f"   🔑 User ID: {admin_result.get('user_id')}")
        else:
            print(f"   ❌ Login Admin fallito")
            return
        
        # Test 2: Login come User normale di test
        print("\n🧪 TEST 2: Login come User normale di test")
        user_result = auth_manager.login('testuser', 'password123')
        
        if user_result:
            print(f"   ✅ Login User riuscito")
            print(f"   👤 Username: {user_result.get('username')}")
            print(f"   👑 Role: {user_result.get('role_name')}")
            print(f"   🔑 User ID: {user_result.get('user_id')}")
        else:
            print(f"   ❌ Login User fallito")
            return
        
        # Test 3: Verifica permessi Admin vs User
        print("\n🧪 TEST 3: Verifica permessi Admin vs User")
        
        # Simula controlli di accesso
        def check_admin_access(user_data, function_name):
            """Simula controllo accesso admin"""
            if not user_data or user_data.get('role_name') != 'Admin':
                return False, f"🚫 Accesso negato a {function_name}"
            return True, f"✅ Accesso consentito a {function_name}"
        
        # Test funzioni admin
        admin_functions = [
            "Gestione Utenti",
            "Creazione Utenti", 
            "Modifica Password",
            "Gestione Ruoli",
            "Eliminazione Utenti"
        ]
        
        print(f"\n   👑 Test permessi Admin:")
        for function in admin_functions:
            allowed, message = check_admin_access(admin_result, function)
            print(f"   {message}")
        
        print(f"\n   👤 Test permessi User:")
        for function in admin_functions:
            allowed, message = check_admin_access(user_result, function)
            print(f"   {message}")
        
        # Test 4: Verifica visibilità menu
        print("\n🧪 TEST 4: Verifica visibilità menu")
        
        def get_menu_options(user_data):
            """Simula opzioni menu basate sui permessi"""
            base_menu = [
                "📊 Dashboard",
                "👥 Lead", 
                "✅ Task",
                "🤖 AI Assistant",
                "🌐 Portali",
                "📞 Contatti",
                "🔗 Broker",
                "📝 Script",
                "📁 Storage",
                "📊 Report",
                "⚙️ Settings"
            ]
            
            if user_data and user_data.get('role_name') == 'Admin':
                # Solo admin vede gestione utenti
                admin_menu = base_menu.copy()
                admin_menu.insert(3, "👤 Utenti")
                admin_menu.insert(4, "👥 Gruppi")
                return admin_menu
            else:
                return base_menu
        
        admin_menu = get_menu_options(admin_result)
        user_menu = get_menu_options(user_result)
        
        print(f"   👑 Menu Admin ({len(admin_menu)} opzioni):")
        for option in admin_menu:
            print(f"      {option}")
        
        print(f"\n   👤 Menu User ({len(user_menu)} opzioni):")
        for option in user_menu:
            print(f"      {option}")
        
        # Verifica che User non veda gestione utenti
        has_user_management = "👤 Utenti" in user_menu
        print(f"\n   🔍 User vede gestione utenti: {'❌ SÌ (PROBLEMA!)' if has_user_management else '✅ NO (CORRETTO)'}")
        
        # Test 5: Verifica creazione utenti
        print("\n🧪 TEST 5: Verifica creazione utenti")
        
        # Simula tentativo di creazione utente
        import time
        timestamp = int(time.time())
        test_user_data = {
            'first_name': 'Test',
            'last_name': 'Access',
            'email': f'test.access.{timestamp}@example.com',
            'username': f'test.access.{timestamp}',
            'password': 'password123',
            'role_id': 2,  # User
            'department_id': 1,
            'is_active': True,
            'is_admin': False
        }
        
        # Test con admin
        print(f"   👑 Test creazione utente da Admin:")
        admin_role = admin_result.get('role_name') or ('Admin' if admin_result.get('role_id') == 1 else 'User')
        user_id_admin = db.create_user(test_user_data, admin_role)
        if user_id_admin:
            print(f"   ✅ Admin può creare utenti (ID: {user_id_admin})")
        else:
            print(f"   ❌ Admin non può creare utenti")
        
        # Test con user normale
        print(f"   👤 Test creazione utente da User:")
        user_role = user_result.get('role_name') or ('Admin' if user_result.get('role_id') == 1 else 'User')
        user_id_user = db.create_user(test_user_data, user_role)
        if user_id_user:
            print(f"   ❌ PROBLEMA: User può creare utenti (ID: {user_id_user})")
        else:
            print(f"   ✅ User non può creare utenti (CORRETTO)")
        
        # Test 6: Verifica creazione admin
        print("\n🧪 TEST 6: Verifica creazione admin")
        
        admin_user_data = {
            'first_name': 'Test',
            'last_name': 'Admin',
            'email': f'test.admin.{timestamp}@example.com',
            'username': f'test.admin.{timestamp}',
            'password': 'password123',
            'role_id': 1,  # Admin
            'department_id': 1,
            'is_active': True,
            'is_admin': True
        }
        
        # Test con admin (dovrebbe funzionare)
        print(f"   👑 Test creazione admin da Admin:")
        # Usa role_name se disponibile, altrimenti usa role_id
        admin_role = admin_result.get('role_name') or ('Admin' if admin_result.get('role_id') == 1 else 'User')
        admin_id_admin = db.create_user(admin_user_data, admin_role)
        if admin_id_admin:
            print(f"   ✅ Admin può creare admin (ID: {admin_id_admin})")
        else:
            print(f"   ❌ Admin non può creare admin")
        
        # Test con user normale (dovrebbe fallire)
        print(f"   👤 Test creazione admin da User:")
        user_role = user_result.get('role_name') or ('Admin' if user_result.get('role_id') == 1 else 'User')
        admin_id_user = db.create_user(admin_user_data, user_role)
        if admin_id_user:
            print(f"   ❌ PROBLEMA: User può creare admin (ID: {admin_id_user})")
        else:
            print(f"   ✅ User non può creare admin (CORRETTO)")
        
        print("\n✅ TEST CONTROLLI DI ACCESSO COMPLETATO!")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script testerà i controlli di accesso!")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        test_access_control()
    else:
        print("❌ Test annullato")
