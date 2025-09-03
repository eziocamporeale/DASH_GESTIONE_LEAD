#!/usr/bin/env python3
"""
Script per testare il modulo lead
Inserisce alcuni lead di test
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from config import LEAD_STATES, LEAD_CATEGORIES, LEAD_PRIORITIES

def create_test_leads():
    """Crea alcuni lead di test"""
    
    db = DatabaseManager()
    
    # Lead di test
    test_leads = [
        {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'mario.rossi@azienda1.com',
            'phone': '+39 123 456 789',
            'company': 'Azienda Innovativa Srl',
            'position': 'CEO',
            'state_id': 1,  # Nuovo
            'category_id': 1,  # Caldo
            'priority_id': 1,  # Alta
            'source_id': 1,  # Website
            'assigned_to': 1,  # Admin
            'budget': 50000.0,
            'expected_close_date': '2025-12-31',
            'notes': 'Lead molto interessato al nostro prodotto. Ha già fatto domande specifiche.',
            'created_by': 1
        },
        {
            'first_name': 'Giulia',
            'last_name': 'Bianchi',
            'email': 'giulia.bianchi@startup.com',
            'phone': '+39 987 654 321',
            'company': 'TechStartup',
            'position': 'CTO',
            'state_id': 2,  # Contattato
            'category_id': 2,  # Tiepido
            'priority_id': 2,  # Media
            'source_id': 2,  # Social Media
            'assigned_to': 1,  # Admin
            'budget': 25000.0,
            'expected_close_date': '2025-11-15',
            'notes': 'Interessata ma vuole vedere una demo prima di decidere.',
            'created_by': 1
        },
        {
            'first_name': 'Luca',
            'last_name': 'Verdi',
            'email': 'luca.verdi@corporation.it',
            'phone': '+39 555 123 456',
            'company': 'Corporation Italia',
            'position': 'IT Manager',
            'state_id': 3,  # Qualificato
            'category_id': 1,  # Caldo
            'priority_id': 1,  # Alta
            'source_id': 3,  # Email Marketing
            'assigned_to': 1,  # Admin
            'budget': 100000.0,
            'expected_close_date': '2025-10-30',
            'notes': 'Lead qualificato con budget importante. Richiede personalizzazione.',
            'created_by': 1
        },
        {
            'first_name': 'Anna',
            'last_name': 'Neri',
            'email': 'anna.neri@consulting.com',
            'phone': '+39 333 789 012',
            'company': 'Consulting Group',
            'position': 'Partner',
            'state_id': 4,  # Proposta
            'category_id': 2,  # Tiepido
            'priority_id': 2,  # Media
            'source_id': 4,  # Referral
            'assigned_to': 1,  # Admin
            'budget': 35000.0,
            'expected_close_date': '2025-12-15',
            'notes': 'Proposta inviata. In attesa di feedback.',
            'created_by': 1
        },
        {
            'first_name': 'Paolo',
            'last_name': 'Gialli',
            'email': 'paolo.gialli@smallbiz.it',
            'phone': '+39 444 567 890',
            'company': 'Piccola Impresa',
            'position': 'Titolare',
            'state_id': 1,  # Nuovo
            'category_id': 3,  # Freddo
            'priority_id': 3,  # Bassa
            'source_id': 5,  # Cold Call
            'assigned_to': 1,  # Admin
            'budget': 5000.0,
            'expected_close_date': '2026-01-15',
            'notes': 'Lead freddo da cold calling. Necessita nurturing.',
            'created_by': 1
        }
    ]
    
    print("🚀 Creazione lead di test...")
    
    created_count = 0
    for i, lead_data in enumerate(test_leads, 1):
        try:
            lead_id = db.create_lead(lead_data)
            if lead_id:
                print(f"✅ Lead {i} creato: {lead_data['first_name']} {lead_data['last_name']} (ID: {lead_id})")
                created_count += 1
            else:
                print(f"❌ Errore creazione lead {i}: {lead_data['first_name']} {lead_data['last_name']}")
        except Exception as e:
            print(f"❌ Errore creazione lead {i}: {e}")
    
    print(f"\n📊 Risultato: {created_count}/{len(test_leads)} lead creati con successo")
    
    # Verifica
    all_leads = db.get_leads()
    print(f"📈 Totale lead nel database: {len(all_leads)}")
    
    return created_count

def show_lead_stats():
    """Mostra statistiche sui lead"""
    
    db = DatabaseManager()
    stats = db.get_lead_stats()
    
    print("\n📊 Statistiche Lead:")
    print("=" * 40)
    
    # Lead totali
    total_leads = stats['total_leads'][0]['count'] if stats['total_leads'] else 0
    print(f"📈 Lead totali: {total_leads}")
    
    # Lead per stato
    print("\n📋 Lead per Stato:")
    for state in stats['leads_by_state']:
        print(f"  • {state['name']}: {state['count']}")
    
    # Lead per categoria
    print("\n🏷️ Lead per Categoria:")
    for category in stats['leads_by_category']:
        print(f"  • {category['name']}: {category['count']}")
    
    # Lead per fonte
    print("\n📞 Lead per Fonte:")
    for source in stats['leads_by_source']:
        print(f"  • {source['name']}: {source['count']}")

if __name__ == "__main__":
    print("🧪 Test Modulo Lead")
    print("=" * 50)
    
    # Crea lead di test
    created_count = create_test_leads()
    
    if created_count > 0:
        # Mostra statistiche
        show_lead_stats()
        
        print("\n✅ Test completato con successo!")
        print("🎯 Ora puoi testare il modulo lead nell'applicazione")
    else:
        print("\n❌ Nessun lead creato. Verifica il database.")
