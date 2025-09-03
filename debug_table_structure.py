#!/usr/bin/env python3
"""
Debug struttura tabella leads
Creato da Ezio Camporeale
"""

import sqlite3
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import DATABASE_PATH

def debug_table_structure():
    """Debug della struttura tabella"""
    
    print("🔍 DEBUG STRUTTURA TABELLA LEADS")
    print("=" * 40)
    
    try:
        # Connessione SQLite
        sqlite_conn = sqlite3.connect(DATABASE_PATH)
        
        # Ottieni informazioni sulla tabella
        cursor = sqlite_conn.cursor()
        cursor.execute("PRAGMA table_info(leads)")
        columns = cursor.fetchall()
        
        print("📋 Struttura tabella leads:")
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - Nullable: {col[3]} - Default: {col[4]}")
        
        # Query un record per vedere i dati
        cursor.execute("SELECT * FROM leads LIMIT 1")
        lead = cursor.fetchone()
        
        if lead:
            print(f"\n📊 Primo record (tuple):")
            print(f"   {lead}")
            
            # Prova a convertire in dict
            column_names = [col[1] for col in columns]
            lead_dict = dict(zip(column_names, lead))
            
            print(f"\n📋 Primo record (dict):")
            for key, value in lead_dict.items():
                print(f"   {key}: {value}")
        
        sqlite_conn.close()
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_table_structure()
