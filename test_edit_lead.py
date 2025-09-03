#!/usr/bin/env python3
"""
Script per testare la modifica dei lead
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

def test_edit_lead():
    """Testa la modifica dei lead"""
    
    print("🧪 TEST MODIFICA LEAD")
    print("=" * 50)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        db = DatabaseManager()
        
        print("✅ Connessione Supabase stabilita")
        
        # Crea un lead di test
        print("\n📝 Creazione lead di test...")
        test_data = {
            'name': 'Test Lead Edit',
            'email': 'test.edit@example.com',
            'phone': '+39 123 456 7890',
            'company': 'Test Company Edit',
            'position': 'Test Position',
            'budget': 10000,
            'expected_close_date': '2024-12-31',
            'category_id': 1,
            'state_id': 1,
            'priority_id': 1,
            'source_id': 1,
            'assigned_to': 1,
            'notes': 'Test lead per modifica',
            'created_by': 1
        }
        
        # Inserisci il lead
        result = supabase.table('leads').insert(test_data).execute()
        if result.data:
            test_lead_id = result.data[0]['id']
            print(f"✅ Lead di test creato con ID: {test_lead_id}")
            
            # Leggi il lead per ottenere i dati completi
            print(f"\n📖 Lettura lead ID: {test_lead_id}")
            lead_data = db.get_lead(test_lead_id)
            
            if lead_data:
                print("✅ Lead letto correttamente")
                print(f"   Nome: {lead_data.get('name', 'N/A')}")
                print(f"   Email: {lead_data.get('email', 'N/A')}")
                print(f"   Company: {lead_data.get('company', 'N/A')}")
                
                # Testa la funzione update_lead del database_manager
                print(f"\n✏️ Test modifica lead ID: {test_lead_id}")
                
                update_data = {
                    'first_name': 'Test',
                    'last_name': 'Lead Modified',
                    'email': 'test.modified@example.com',
                    'phone': '+39 987 654 3210',
                    'company': 'Test Company Modified',
                    'position': 'Test Position Modified',
                    'lead_state_id': 2,  # Cambia stato
                    'lead_priority_id': 2,  # Cambia priorità
                    'lead_category_id': 2,  # Cambia categoria
                    'lead_source_id': 2,  # Cambia fonte
                    'assigned_to': 1,
                    'budget': 20000,
                    'expected_close_date': '2025-06-30',
                    'notes': 'Test lead modificato',
                    'created_by': 1
                }
                
                if db.update_lead(test_lead_id, update_data):
                    print("✅ Modifica riuscita tramite database_manager")
                    
                    # Verifica la modifica
                    print("\n🔍 Verifica modifica...")
                    updated_lead = db.get_lead(test_lead_id)
                    if updated_lead:
                        print(f"   Nome aggiornato: {updated_lead.get('name', 'N/A')}")
                        print(f"   Email aggiornata: {updated_lead.get('email', 'N/A')}")
                        print(f"   Company aggiornata: {updated_lead.get('company', 'N/A')}")
                        print(f"   Budget aggiornato: {updated_lead.get('budget', 'N/A')}")
                    else:
                        print("❌ Errore lettura lead dopo modifica")
                else:
                    print("❌ Modifica fallita tramite database_manager")
                    
                    # Prova modifica diretta
                    print("🔄 Tentativo modifica diretta...")
                    try:
                        direct_update = {
                            'name': 'Test Lead Direct Modified',
                            'email': 'test.direct@example.com',
                            'company': 'Test Company Direct'
                        }
                        supabase.table('leads').update(direct_update).eq('id', test_lead_id).execute()
                        print("✅ Modifica diretta riuscita")
                    except Exception as e:
                        print(f"❌ Modifica diretta fallita: {e}")
            else:
                print("❌ Errore lettura lead di test")
        else:
            print("❌ Errore creazione lead di test")
            
    except Exception as e:
        print(f"❌ Errore generale: {e}")

if __name__ == "__main__":
    test_edit_lead()
