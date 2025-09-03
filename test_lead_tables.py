#!/usr/bin/env python3
"""
Test tabelle lead in Supabase
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

def test_lead_tables():
    """Testa le tabelle lead specifiche"""
    
    print("🔍 TEST TABELLE LEAD SUPABASE")
    print("=" * 40)
    
    try:
        # Crea client Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test tabelle lead
        tables = [
            'lead_states',
            'lead_priorities', 
            'lead_categories',
            'lead_sources',
            'leads',
            'task_states',
            'task_types',
            'tasks'
        ]
        
        for table in tables:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"✅ {table}: {len(result.data)} record trovati")
            except Exception as e:
                print(f"❌ {table}: Errore - {e}")
        
        print("\n🎯 Test completato!")
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")

if __name__ == "__main__":
    test_lead_tables()
