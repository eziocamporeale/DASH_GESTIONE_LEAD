#!/usr/bin/env python3
"""
Script di migrazione task
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

def migrate_tasks():
    """Migra i task"""
    
    print("✅ MIGRAZIONE TASK")
    print("=" * 25)
    
    try:
        # Connessioni
        sqlite_conn = sqlite3.connect(DATABASE_PATH)
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Query task da SQLite
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        
        print(f"📊 Trovati {len(tasks)} task in SQLite")
        
        # Ottieni nomi colonne
        cursor.execute("PRAGMA table_info(tasks)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Migra ogni task
        for task_tuple in tasks:
            # Converti tuple in dict
            task = dict(zip(column_names, task_tuple))
            
            task_data = {
                'title': task['title'],
                'description': task['description'],
                'task_type_id': task['task_type_id'],
                'state_id': task['state_id'],
                'priority_id': task.get('priority_id', 2),
                'assigned_to': task['assigned_to'],
                'lead_id': task.get('lead_id', None),
                'due_date': task['due_date'],
                'created_by': task['created_by'],
                'created_at': task['created_at'],
                'updated_at': task['updated_at']
            }
            
            try:
                result = supabase.table('tasks').insert(task_data).execute()
                print(f"✅ Task migrato: {task['title']}")
            except Exception as e:
                print(f"❌ Errore task {task['title']}: {e}")
        
        sqlite_conn.close()
        print("\n✅ Migrazione task completata!")
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_tasks()
