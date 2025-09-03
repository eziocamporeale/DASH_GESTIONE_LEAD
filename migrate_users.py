#!/usr/bin/env python3
"""
Script di migrazione utenti
Creato da Ezio Camporeale
"""

import sqlite3
import sys
from pathlib import Path
import logging

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import DATABASE_PATH, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_users():
    """Migra gli utenti"""
    
    print("👤 MIGRAZIONE UTENTI")
    print("=" * 30)
    
    try:
        # Connessioni
        sqlite_conn = sqlite3.connect(DATABASE_PATH)
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Query utenti da SQLite
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        print(f"📊 Trovati {len(users)} utenti in SQLite")
        
        # Ottieni nomi colonne
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Migra ogni utente
        for user_tuple in users:
            # Converti tuple in dict
            user = dict(zip(column_names, user_tuple))
            
            user_data = {
                'username': user['username'],
                'email': user['email'],
                'password_hash': user['password_hash'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'phone': user.get('phone', None),
                'role_id': user['role_id'],
                'department_id': user.get('department_id', None),
                'is_active': bool(user['is_active']),
                'is_admin': user.get('is_admin', False),
                'notes': user.get('notes', None),
                'last_login': user.get('last_login', None),
                'created_by': user.get('created_by', None),
                'created_at': user['created_at'],
                'updated_at': user['updated_at']
            }
            
            try:
                # Controlla se l'utente esiste già
                existing = supabase.table('users').select('id').eq('username', user['username']).execute()
                if not existing.data:
                    result = supabase.table('users').insert(user_data).execute()
                    print(f"✅ Utente migrato: {user['first_name']} {user['last_name']}")
                else:
                    print(f"⚠️ Utente già esistente: {user['first_name']} {user['last_name']}")
            except Exception as e:
                print(f"❌ Errore utente {user['first_name']} {user['last_name']}: {e}")
        
        sqlite_conn.close()
        print("\n✅ Migrazione utenti completata!")
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_users()
