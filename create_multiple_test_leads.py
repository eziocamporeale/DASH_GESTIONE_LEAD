#!/usr/bin/env python3
"""
Script per creare più lead di test
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

def create_multiple_test_leads():
    """Crea più lead di test"""
    
    print("🧪 CREAZIONE MULTIPLI LEAD DI TEST")
    print("=" * 50)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("✅ Connessione Supabase stabilita")
        
        # Lista di lead di test
        test_leads = [
            {
                'name': 'Giulia Bianchi',
                'email': 'giulia.bianchi@example.com',
                'phone': '+39 234 567 8901',
                'company': 'Tech Solutions SRL',
                'position': 'CEO',
                'budget': 25000,
                'expected_close_date': '2024-11-30',
                'category_id': 2,
                'state_id': 2,
                'priority_id': 2,
                'source_id': 2,
                'assigned_to': 1,
                'notes': 'Lead interessato ai nostri servizi',
                'created_by': 1
            },
            {
                'name': 'Marco Verdi',
                'email': 'marco.verdi@example.com',
                'phone': '+39 345 678 9012',
                'company': 'Digital Marketing Agency',
                'position': 'Marketing Manager',
                'budget': 18000,
                'expected_close_date': '2024-12-15',
                'category_id': 1,
                'state_id': 1,
                'priority_id': 1,
                'source_id': 1,
                'assigned_to': 1,
                'notes': 'Lead caldo, pronto per la proposta',
                'created_by': 1
            },
            {
                'name': 'Sofia Neri',
                'email': 'sofia.neri@example.com',
                'phone': '+39 456 789 0123',
                'company': 'Startup Innovativa',
                'position': 'Founder',
                'budget': 35000,
                'expected_close_date': '2025-01-15',
                'category_id': 3,
                'state_id': 3,
                'priority_id': 3,
                'source_id': 3,
                'assigned_to': 1,
                'notes': 'Lead freddo, necessita nurturing',
                'created_by': 1
            }
        ]
        
        print(f"\n📝 Creazione {len(test_leads)} lead di test...")
        
        created_leads = []
        
        for i, lead_data in enumerate(test_leads, 1):
            try:
                result = supabase.table('leads').insert(lead_data).execute()
                if result.data:
                    lead_id = result.data[0]['id']
                    created_leads.append(lead_id)
                    print(f"   ✅ Lead {i} creato con ID: {lead_id} - {lead_data['name']}")
                else:
                    print(f"   ❌ Errore creazione lead {i}")
            except Exception as e:
                print(f"   ❌ Errore creazione lead {i}: {e}")
        
        print(f"\n📊 Riepilogo:")
        print(f"   Lead creati con successo: {len(created_leads)}")
        print(f"   ID dei lead: {created_leads}")
        
        # Verifica totale leads nel database
        result = supabase.table('leads').select('*').execute()
        print(f"   Totale leads nel database: {len(result.data)}")
        
        print(f"\n✅ Lead di test creati con successo!")
        print(f"   Ora ricarica la pagina Streamlit per vedere i risultati")
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_multiple_test_leads()
