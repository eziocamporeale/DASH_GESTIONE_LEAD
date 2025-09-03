#!/usr/bin/env python3
"""
Script per testare l'eliminazione dei lead
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client
from database.database_manager import DatabaseManager

def test_delete_lead():
    """Testa l'eliminazione dei lead"""
    
    print("🧪 TEST ELIMINAZIONE LEAD")
    print("=" * 50)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        db = DatabaseManager()
        
        print("✅ Connessione Supabase stabilita")
        
        # Crea un lead di test
        print("\n📝 Creazione lead di test...")
        test_data = {
            'name': 'Test Lead Delete',
            'email': 'test.delete@example.com',
            'phone': '+39 123 456 7890',
            'company': 'Test Company Delete',
            'position': 'Test Position',
            'budget': 10000,
            'expected_close_date': '2024-12-31',
            'category_id': 1,
            'state_id': 1,
            'priority_id': 1,
            'source_id': 1,
            'assigned_to': 1,
            'notes': 'Test lead per eliminazione',
            'created_by': 1
        }
        
        # Inserisci il lead
        result = supabase.table('leads').insert(test_data).execute()
        if result.data:
            test_lead_id = result.data[0]['id']
            print(f"✅ Lead di test creato con ID: {test_lead_id}")
            
            # Testa la funzione delete_lead del database_manager
            print(f"\n🗑️ Test eliminazione lead ID: {test_lead_id}")
            
            if db.delete_lead(test_lead_id):
                print("✅ Eliminazione riuscita tramite database_manager")
            else:
                print("❌ Eliminazione fallita tramite database_manager")
                
                # Prova eliminazione diretta
                print("🔄 Tentativo eliminazione diretta...")
                try:
                    supabase.table('leads').delete().eq('id', test_lead_id).execute()
                    print("✅ Eliminazione diretta riuscita")
                except Exception as e:
                    print(f"❌ Eliminazione diretta fallita: {e}")
        else:
            print("❌ Errore creazione lead di test")
            
    except Exception as e:
        print(f"❌ Errore generale: {e}")

if __name__ == "__main__":
    test_delete_lead()
