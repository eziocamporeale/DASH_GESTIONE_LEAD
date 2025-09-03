#!/usr/bin/env python3
"""
Script per testare il modulo utenti
Inserisce alcuni utenti di test
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager

def create_test_users():
    """Crea alcuni utenti di test"""
    
    db = DatabaseManager()
    
    # Utenti di test
    test_users = [
        {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'mario.rossi@example.com',
            'phone': '+39 123 456 789',
            'username': 'mario.rossi',
            'password': 'password123',
            'role_id': 2,  # Manager
            'department_id': 1,  # Vendite
            'notes': 'Manager vendite esperto',
            'is_active': True,
            'is_admin': False,
            'created_by': 1
        },
        {
            'first_name': 'Giulia',
            'last_name': 'Bianchi',
            'email': 'giulia.bianchi@example.com',
            'phone': '+39 987 654 321',
            'username': 'giulia.bianchi',
            'password': 'password123',
            'role_id': 3,  # Setter
            'department_id': 1,  # Vendite
            'notes': 'Setter specializzata in lead qualificazione',
            'is_active': True,
            'is_admin': False,
            'created_by': 1
        },
        {
            'first_name': 'Luca',
            'last_name': 'Verdi',
            'email': 'luca.verdi@example.com',
            'phone': '+39 555 123 456',
            'username': 'luca.verdi',
            'password': 'password123',
            'role_id': 4,  # Closer
            'department_id': 1,  # Vendite
            'notes': 'Closer esperto in chiusura deal',
            'is_active': True,
            'is_admin': False,
            'created_by': 1
        },
        {
            'first_name': 'Anna',
            'last_name': 'Neri',
            'email': 'anna.neri@example.com',
            'phone': '+39 111 222 333',
            'username': 'anna.neri',
            'password': 'password123',
            'role_id': 5,  # Viewer
            'department_id': 2,  # Marketing
            'notes': 'Analista marketing',
            'is_active': True,
            'is_admin': False,
            'created_by': 1
        },
        {
            'first_name': 'Paolo',
            'last_name': 'Gialli',
            'email': 'paolo.gialli@example.com',
            'phone': '+39 444 555 666',
            'username': 'paolo.gialli',
            'password': 'password123',
            'role_id': 3,  # Setter
            'department_id': 1,  # Vendite
            'notes': 'Setter junior in formazione',
            'is_active': False,  # Inattivo
            'is_admin': False,
            'created_by': 1
        }
    ]
    
    print("🚀 Creazione utenti di test...")
    
    created_count = 0
    for i, user_data in enumerate(test_users, 1):
        try:
            user_id = db.create_user(user_data)
            if user_id:
                print(f"✅ Utente {i} creato: {user_data['first_name']} {user_data['last_name']} (ID: {user_id})")
                created_count += 1
            else:
                print(f"❌ Errore creazione utente {i}: {user_data['first_name']} {user_data['last_name']}")
        except Exception as e:
            print(f"❌ Errore creazione utente {i}: {e}")
    
    print(f"\n📊 Risultato: {created_count}/{len(test_users)} utenti creati con successo")
    
    # Verifica
    all_users = db.get_all_users()
    print(f"📈 Totale utenti nel database: {len(all_users)}")
    
    return created_count

def show_user_stats():
    """Mostra statistiche sugli utenti"""
    
    db = DatabaseManager()
    stats = db.get_user_stats()
    
    print("\n📊 Statistiche Utenti:")
    print("=" * 40)
    
    # Utenti totali
    total_users = stats['total_users'][0]['count'] if stats['total_users'] else 0
    print(f"📈 Utenti totali: {total_users}")
    
    # Utenti attivi
    active_users = stats['active_users'][0]['count'] if stats['active_users'] else 0
    print(f"✅ Utenti attivi: {active_users}")
    
    # Admin
    admin_users = stats['admin_users'][0]['count'] if stats['admin_users'] else 0
    print(f"👑 Admin: {admin_users}")
    
    # Utenti per ruolo
    print("\n📋 Utenti per Ruolo:")
    for role in stats['users_by_role']:
        print(f"  • {role['name']}: {role['count']}")

if __name__ == "__main__":
    print("🧪 Test Modulo Utenti")
    print("=" * 50)
    
    # Crea utenti di test
    created_count = create_test_users()
    
    if created_count > 0:
        # Mostra statistiche
        show_user_stats()
        
        print("\n✅ Test completato con successo!")
        print("🎯 Ora puoi testare il modulo utenti nell'applicazione")
    else:
        print("\n❌ Nessun utente creato. Verifica il database.")
