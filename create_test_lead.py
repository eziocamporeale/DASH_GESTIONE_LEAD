#!/usr/bin/env python3
"""
Script per creare un lead di test e verificare la visualizzazione
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

def create_test_lead():
    """Crea un lead di test e verifica la visualizzazione"""
    
    print("🧪 CREAZIONE LEAD DI TEST")
    print("=" * 50)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        db = DatabaseManager()
        
        print("✅ Connessione Supabase stabilita")
        
        # Crea un lead di test
        print("\n📝 Creazione lead di test...")
        test_data = {
            'name': 'Mario Rossi',
            'email': 'mario.rossi@example.com',
            'phone': '+39 123 456 7890',
            'company': 'Azienda Test SRL',
            'position': 'Manager',
            'budget': 15000,
            'expected_close_date': '2024-12-31',
            'category_id': 1,
            'state_id': 1,
            'priority_id': 1,
            'source_id': 1,
            'assigned_to': 1,
            'notes': 'Lead di test per verifica visualizzazione',
            'created_by': 1
        }
        
        # Inserisci il lead
        result = supabase.table('leads').insert(test_data).execute()
        if result.data:
            test_lead_id = result.data[0]['id']
            print(f"✅ Lead di test creato con ID: {test_lead_id}")
            
            # Verifica che sia visibile tramite get_leads
            print(f"\n🔍 Verifica visualizzazione lead ID: {test_lead_id}")
            
            leads = db.get_leads()
            print(f"📋 Leads restituiti da get_leads(): {len(leads)}")
            
            if leads:
                for i, lead in enumerate(leads, 1):
                    print(f"   {i}. ID: {lead['id']} - Nome: {lead.get('name', lead.get('first_name', 'N/A'))} - Email: {lead.get('email', 'N/A')}")
                    print(f"      Stato: {lead.get('state_name', 'N/A')} - Categoria: {lead.get('category_name', 'N/A')}")
                    print(f"      Priorità: {lead.get('priority_name', 'N/A')} - Fonte: {lead.get('source_name', 'N/A')}")
            else:
                print("   📭 Nessun lead restituito da get_leads()")
                
            # Test con filtri specifici
            print(f"\n🔍 Test con filtri specifici...")
            
            # Test filtro stato
            state_filters = {'state_id': 1}
            leads_state = db.get_leads(filters=state_filters)
            print(f"📋 Leads con state_id=1: {len(leads_state)}")
            
            # Test filtro categoria
            category_filters = {'category_id': 1}
            leads_category = db.get_leads(filters=category_filters)
            print(f"📋 Leads con category_id=1: {len(leads_category)}")
            
            # Test ricerca
            search_filters = {'search': 'mario'}
            leads_search = db.get_leads(filters=search_filters)
            print(f"📋 Leads con ricerca 'mario': {len(leads_search)}")
            
            print(f"\n✅ Lead di test creato e verificato con successo!")
            print(f"   Ora puoi testare la visualizzazione nell'applicazione Streamlit")
            
        else:
            print("❌ Errore creazione lead di test")
            
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_lead()
