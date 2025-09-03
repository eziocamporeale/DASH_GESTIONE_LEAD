#!/usr/bin/env python3
"""
Script di migrazione semplificato
Creato da Ezio Camporeale
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import logging

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import DATABASE_PATH, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_leads_only():
    """Migra solo i lead per test"""
    
    print("🚀 MIGRAZIONE SEMPLIFICATA - SOLO LEAD")
    print("=" * 50)
    
    try:
        # Connessioni
        sqlite_conn = sqlite3.connect(DATABASE_PATH)
        
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Query lead da SQLite
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM leads")
        leads = cursor.fetchall()
        
        print(f"📊 Trovati {len(leads)} lead in SQLite")
        
        # Ottieni nomi colonne
        cursor.execute("PRAGMA table_info(leads)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Migra ogni lead
        for lead_tuple in leads:
            # Converti tuple in dict
            lead = dict(zip(column_names, lead_tuple))
            
            # Combina first_name e last_name in name
            full_name = f"{lead['first_name']} {lead['last_name']}".strip()
            
            lead_data = {
                'name': full_name,
                'email': lead['email'],
                'phone': lead['phone'],
                'company': lead['company'],
                'position': lead['position'],
                'budget': float(lead['budget']) if lead['budget'] else None,
                'expected_close_date': lead['expected_close_date'],
                'category_id': lead['category_id'],
                'state_id': lead['state_id'],
                'priority_id': lead['priority_id'],
                'source_id': lead['source_id'],
                'assigned_to': lead['assigned_to'],
                'notes': lead['notes'],
                'created_by': lead['created_by']
            }
            
            try:
                result = supabase.table('leads').insert(lead_data).execute()
                print(f"✅ Lead migrato: {full_name}")
            except Exception as e:
                print(f"❌ Errore lead {full_name}: {e}")
        
        sqlite_conn.close()
        print("\n✅ Migrazione lead completata!")
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_leads_only()
