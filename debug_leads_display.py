#!/usr/bin/env python3
"""
Script per debuggare la visualizzazione dei lead
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

def debug_leads_display():
    """Debugga la visualizzazione dei lead"""
    
    print("🔍 DEBUG VISUALIZZAZIONE LEAD")
    print("=" * 50)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        db = DatabaseManager()
        
        print("✅ Connessione Supabase stabilita")
        
        # 1. Verifica leads nel database
        print("\n📊 1. VERIFICA LEADS NEL DATABASE")
        print("-" * 30)
        
        result = supabase.table('leads').select('*').execute()
        print(f"📋 Leads trovati nel database: {len(result.data)}")
        
        if result.data:
            for i, lead in enumerate(result.data, 1):
                print(f"   {i}. ID: {lead['id']} - Nome: {lead.get('name', 'N/A')} - Email: {lead.get('email', 'N/A')}")
        else:
            print("   📭 Nessun lead trovato nel database")
            return
        
        # 2. Test funzione get_leads senza filtri
        print("\n🔍 2. TEST FUNZIONE GET_LEADS SENZA FILTRI")
        print("-" * 30)
        
        leads = db.get_leads()
        print(f"📋 Leads restituiti da get_leads(): {len(leads)}")
        
        if leads:
            for i, lead in enumerate(leads, 1):
                print(f"   {i}. ID: {lead['id']} - Nome: {lead.get('name', lead.get('first_name', 'N/A'))} - Email: {lead.get('email', 'N/A')}")
        else:
            print("   📭 Nessun lead restituito da get_leads()")
        
        # 3. Test funzione get_leads con filtri vuoti
        print("\n🔍 3. TEST FUNZIONE GET_LEADS CON FILTRI VUOTI")
        print("-" * 30)
        
        empty_filters = {}
        leads_with_filters = db.get_leads(filters=empty_filters)
        print(f"📋 Leads restituiti con filtri vuoti: {len(leads_with_filters)}")
        
        # 4. Test con filtri specifici
        print("\n🔍 4. TEST CON FILTRI SPECIFICI")
        print("-" * 30)
        
        # Test filtro stato
        state_filters = {'state_id': 1}
        leads_state = db.get_leads(filters=state_filters)
        print(f"📋 Leads con state_id=1: {len(leads_state)}")
        
        # Test filtro categoria
        category_filters = {'category_id': 1}
        leads_category = db.get_leads(filters=category_filters)
        print(f"📋 Leads con category_id=1: {len(leads_category)}")
        
        # Test ricerca
        search_filters = {'search': 'test'}
        leads_search = db.get_leads(filters=search_filters)
        print(f"📋 Leads con ricerca 'test': {len(leads_search)}")
        
        # 5. Verifica dati di lookup
        print("\n🔍 5. VERIFICA DATI DI LOOKUP")
        print("-" * 30)
        
        states = db.get_lead_states()
        print(f"📋 Stati disponibili: {len(states)}")
        for state in states:
            print(f"   - ID: {state['id']} - Nome: {state['name']}")
        
        categories = db.get_lead_categories()
        print(f"📋 Categorie disponibili: {len(categories)}")
        for cat in categories:
            print(f"   - ID: {cat['id']} - Nome: {cat['name']}")
        
        priorities = db.get_lead_priorities()
        print(f"📋 Priorità disponibili: {len(priorities)}")
        for pri in priorities:
            print(f"   - ID: {pri['id']} - Nome: {pri['name']}")
        
        sources = db.get_lead_sources()
        print(f"📋 Fonti disponibili: {len(sources)}")
        for src in sources:
            print(f"   - ID: {src['id']} - Nome: {src['name']}")
        
        users = db.get_all_users()
        print(f"📋 Utenti disponibili: {len(users)}")
        for user in users:
            print(f"   - ID: {user['id']} - Nome: {user.get('first_name', '')} {user.get('last_name', '')}")
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_leads_display()
