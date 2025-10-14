#!/usr/bin/env python3
"""
Test del meccanismo di creazione utenti corretto
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path
from datetime import datetime

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager

def test_user_creation_fix():
    """Testa il meccanismo di creazione utenti corretto"""
    
    print("🧪 TEST MECCANISMO CREAZIONE UTENTI")
    print("=" * 50)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Inizializza database manager
        db = DatabaseManager()
        
        # Test 1: Creazione utente normale da admin (dovrebbe funzionare)
        print("\n🧪 TEST 1: Creazione utente normale da Admin")
        user_data_normal = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'mario.rossi@test.com',
            'username': 'mario.rossi',
            'password': 'password123',
            'phone': '+39 123 456 789',
            'role_id': 2,  # User
            'department_id': 1,  # Vendite
            'is_active': True,
            'is_admin': False,
            'notes': 'Utente di test normale'
        }
        
        user_id = db.create_user(user_data_normal, 'Admin')
        if user_id:
            print(f"   ✅ Utente normale creato con successo (ID: {user_id})")
        else:
            print(f"   ❌ Errore creazione utente normale")
        
        # Test 2: Creazione utente admin da admin (dovrebbe funzionare)
        print("\n🧪 TEST 2: Creazione utente admin da Admin")
        user_data_admin = {
            'first_name': 'Luigi',
            'last_name': 'Bianchi',
            'email': 'luigi.bianchi@test.com',
            'username': 'luigi.bianchi',
            'password': 'password123',
            'phone': '+39 987 654 321',
            'role_id': 1,  # Admin
            'department_id': 1,  # Vendite
            'is_active': True,
            'is_admin': True,
            'notes': 'Utente admin di test'
        }
        
        user_id = db.create_user(user_data_admin, 'Admin')
        if user_id:
            print(f"   ✅ Utente admin creato con successo (ID: {user_id})")
        else:
            print(f"   ❌ Errore creazione utente admin")
        
        # Test 3: Creazione utente admin da user normale (dovrebbe fallire)
        print("\n🧪 TEST 3: Tentativo creazione utente admin da User normale")
        user_data_unauthorized = {
            'first_name': 'Paolo',
            'last_name': 'Verdi',
            'email': 'paolo.verdi@test.com',
            'username': 'paolo.verdi',
            'password': 'password123',
            'phone': '+39 555 666 777',
            'role_id': 1,  # Admin
            'department_id': 1,  # Vendite
            'is_active': True,
            'is_admin': True,
            'notes': 'Tentativo non autorizzato'
        }
        
        user_id = db.create_user(user_data_unauthorized, 'User')
        if user_id:
            print(f"   ❌ PROBLEMA: Utente admin creato da User normale (ID: {user_id})")
        else:
            print(f"   ✅ SICUREZZA: Creazione utente admin bloccata correttamente")
        
        # Test 4: Creazione utente normale da user normale (dovrebbe funzionare)
        print("\n🧪 TEST 4: Creazione utente normale da User normale")
        user_data_normal_user = {
            'first_name': 'Giulia',
            'last_name': 'Neri',
            'email': 'giulia.neri@test.com',
            'username': 'giulia.neri',
            'password': 'password123',
            'phone': '+39 111 222 333',
            'role_id': 2,  # User
            'department_id': 2,  # Marketing
            'is_active': True,
            'is_admin': False,
            'notes': 'Utente normale da user normale'
        }
        
        user_id = db.create_user(user_data_normal_user, 'User')
        if user_id:
            print(f"   ✅ Utente normale creato con successo (ID: {user_id})")
        else:
            print(f"   ❌ Errore creazione utente normale")
        
        # Test 5: Verifica default role_id
        print("\n🧪 TEST 5: Test default role_id (senza specificare ruolo)")
        user_data_default = {
            'first_name': 'Anna',
            'last_name': 'Gialli',
            'email': 'anna.gialli@test.com',
            'username': 'anna.gialli',
            'password': 'password123',
            'phone': '+39 444 555 666',
            # Non specifico role_id - dovrebbe essere 2 (User)
            'department_id': 3,  # Sviluppo
            'is_active': True,
            'is_admin': False,
            'notes': 'Test default role_id'
        }
        
        user_id = db.create_user(user_data_default, 'Admin')
        if user_id:
            print(f"   ✅ Utente con default role_id creato (ID: {user_id})")
            
            # Verifica che sia effettivamente User (role_id = 2)
            user = db.get_user_by_id(user_id)
            if user and user.get('role_id') == 2:
                print(f"   ✅ Verificato: ruolo default corretto (User)")
            else:
                print(f"   ❌ PROBLEMA: ruolo non corretto - dovrebbe essere 2, è {user.get('role_id') if user else 'N/A'}")
        else:
            print(f"   ❌ Errore creazione utente con default")
        
        # Verifica finale
        print("\n📊 VERIFICA FINALE UTENTI CREATI:")
        all_users = db.get_all_users()
        test_users = [u for u in all_users if u.get('email', '').endswith('@test.com')]
        
        print(f"   📈 Utenti di test creati: {len(test_users)}")
        for user in test_users:
            username = user.get('username', 'N/A')
            email = user.get('email', 'N/A')
            role_id = user.get('role_id', 'N/A')
            is_admin = user.get('is_admin', False)
            
            role_name = "Admin" if role_id == 1 else "User" if role_id == 2 else "Tester" if role_id == 3 else f"Role_{role_id}"
            admin_flag = " (Admin Flag)" if is_admin else ""
            
            print(f"   👤 {username} ({email}) - {role_name}{admin_flag}")
        
        print("\n✅ TEST COMPLETATO!")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script creerà utenti di test nel database!")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        test_user_creation_fix()
    else:
        print("❌ Test annullato")





