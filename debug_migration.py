#!/usr/bin/env python3
"""
Script di debug per migrazione
Creato da Ezio Camporeale
"""

import sqlite3
import sys
from pathlib import Path
import json

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import DATABASE_PATH

def debug_sqlite_data():
    """Debug dei dati SQLite"""
    
    print("🔍 DEBUG DATI SQLITE")
    print("=" * 40)
    
    try:
        # Connessione SQLite
        sqlite_conn = sqlite3.connect(DATABASE_PATH)
        sqlite_conn.row_factory = sqlite3.Row
        
        # Query lead da SQLite
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM leads LIMIT 1")
        lead = cursor.fetchone()
        
        if lead:
            print("📋 Primo lead trovato:")
            print(f"   ID: {lead['id']}")
            print(f"   Nome: {lead['name']}")
            print(f"   Email: {lead['email']}")
            print(f"   Phone: {lead['phone']}")
            print(f"   Company: {lead['company']}")
            print(f"   Position: {lead['position']}")
            print(f"   Budget: {lead['budget']}")
            print(f"   Expected Close Date: {lead['expected_close_date']}")
            print(f"   Category ID: {lead['category_id']}")
            print(f"   State ID: {lead['state_id']}")
            print(f"   Priority ID: {lead['priority_id']}")
            print(f"   Source ID: {lead['source_id']}")
            print(f"   Assigned To: {lead['assigned_to']}")
            print(f"   Notes: {lead['notes']}")
            print(f"   Created By: {lead['created_by']}")
            print(f"   Created At: {lead['created_at']}")
            print(f"   Updated At: {lead['updated_at']}")
            
            # Test conversione dati
            print("\n🔄 Test conversione dati:")
            try:
                lead_data = {
                    'name': lead['name'],
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
                print("✅ Conversione dati riuscita")
                print(f"   Budget convertito: {lead_data['budget']}")
                print(f"   Tipo budget: {type(lead_data['budget'])}")
            except Exception as e:
                print(f"❌ Errore conversione: {e}")
        else:
            print("❌ Nessun lead trovato")
        
        sqlite_conn.close()
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_sqlite_data()
