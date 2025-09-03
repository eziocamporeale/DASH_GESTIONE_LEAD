#!/usr/bin/env python3
"""
Script di test per il modulo contatti DASH_GESTIONE_LEAD
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path
from datetime import datetime

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager

def test_contact_templates():
    """Testa la creazione di template di contatto"""
    print("🧪 Test Template di Contatto")
    print("=" * 40)
    
    db = DatabaseManager()
    
    # Template di esempio
    templates = [
        {
            'name': 'Follow-up Email Standard',
            'type': 'Email',
            'category': 'Follow-up',
            'subject': 'Follow-up sulla nostra proposta',
            'content': """Gentile {nome},

Grazie per il suo interesse nella nostra proposta.

Spero che abbia avuto modo di esaminare i dettagli che abbiamo discusso.

Ha domande o vorrebbe programmare una chiamata per approfondire?

Cordiali saluti,
{utente_nome}
{utente_email}""",
            'delay_hours': 24,
            'max_retries': 3,
            'priority': 'Media',
            'notes': 'Template standard per follow-up',
            'is_active': True,
            'created_by': 1
        },
        {
            'name': 'Proposta Commerciale',
            'type': 'Email',
            'category': 'Proposta',
            'subject': 'Proposta commerciale per {azienda}',
            'content': """Gentile {nome},

In allegato trova la nostra proposta commerciale personalizzata per {azienda}.

La proposta include:
- Analisi delle esigenze
- Soluzioni proposte
- Investimento richiesto
- Timeline di implementazione

Siamo disponibili per una presentazione dettagliata.

Cordiali saluti,
{utente_nome}
{utente_email}""",
            'delay_hours': 0,
            'max_retries': 2,
            'priority': 'Alta',
            'notes': 'Template per invio proposte',
            'is_active': True,
            'created_by': 1
        },
        {
            'name': 'SMS Reminder',
            'type': 'SMS',
            'category': 'Reminder',
            'subject': None,
            'content': 'Gentile {nome}, le ricordiamo il nostro appuntamento di domani alle {ora}. Conferma? {utente_nome}',
            'delay_hours': 2,
            'max_retries': 1,
            'priority': 'Alta',
            'notes': 'SMS di reminder per appuntamenti',
            'is_active': True,
            'created_by': 1
        },
        {
            'name': 'Qualificazione Lead',
            'type': 'Email',
            'category': 'Qualificazione',
            'subject': 'Qualificazione lead {azienda}',
            'content': """Gentile {nome},

Grazie per aver mostrato interesse nei nostri servizi.

Per poterle offrire la migliore soluzione, avrei bisogno di alcune informazioni:

1. Qual è il suo ruolo in {azienda}?
2. Quali sono le principali sfide che sta affrontando?
3. Ha un budget definito per questo progetto?
4. Qual è la timeline desiderata?

Può rispondere a queste domande o preferisce una chiamata?

Cordiali saluti,
{utente_nome}
{utente_email}""",
            'delay_hours': 12,
            'max_retries': 3,
            'priority': 'Media',
            'notes': 'Template per qualificazione lead',
            'is_active': True,
            'created_by': 1
        },
        {
            'name': 'Chiusura Deal',
            'type': 'Email',
            'category': 'Chiusura',
            'subject': 'Conferma accordo commerciale',
            'content': """Gentile {nome},

Perfetto! Siamo entusiasti di iniziare questa collaborazione con {azienda}.

Confermiamo i dettagli dell'accordo:
- Servizi: {servizi}
- Investimento: {investimento}
- Timeline: {timeline}

Il prossimo passo è la firma del contratto.

Grazie per la fiducia!

Cordiali saluti,
{utente_nome}
{utente_email}""",
            'delay_hours': 0,
            'max_retries': 1,
            'priority': 'Alta',
            'notes': 'Template per chiusura deal',
            'is_active': True,
            'created_by': 1
        }
    ]
    
    print(f"📧 Creazione {len(templates)} template...")
    
    created_templates = []
    for template in templates:
        try:
            template_id = db.create_contact_template(template)
            if template_id:
                created_templates.append(template_id)
                print(f"  ✅ Template '{template['name']}' creato (ID: {template_id})")
            else:
                print(f"  ❌ Errore creazione template '{template['name']}'")
        except Exception as e:
            print(f"  ❌ Errore creazione template '{template['name']}': {e}")
    
    print(f"\n📊 Template creati: {len(created_templates)}/{len(templates)}")
    return created_templates

def test_contact_sequences():
    """Testa la creazione di sequenze di contatto"""
    print("\n🧪 Test Sequenze di Contatto")
    print("=" * 40)
    
    db = DatabaseManager()
    
    # Sequenze di esempio
    sequences = [
        {
            'name': 'Sequenza Lead Nascita',
            'type': 'Lead Nascita',
            'trigger_event': 'Lead Creato',
            'categories': ['Caldo', 'Tiepido'],
            'sources': ['Website', 'Social Media'],
            'priorities': ['Alta', 'Media'],
            'min_budget': 0,
            'notes': 'Sequenza automatica per nuovi lead',
            'is_active': True,
            'created_by': 1
        },
        {
            'name': 'Sequenza Follow-up',
            'type': 'Follow-up',
            'trigger_event': 'Proposta Inviata',
            'categories': ['Caldo', 'Tiepido', 'Freddo'],
            'sources': ['Website', 'Social Media', 'Email Marketing'],
            'priorities': ['Alta', 'Media', 'Bassa'],
            'min_budget': 1000,
            'notes': 'Sequenza follow-up dopo proposta',
            'is_active': True,
            'created_by': 1
        },
        {
            'name': 'Sequenza Qualificazione',
            'type': 'Qualificazione',
            'trigger_event': 'Lead Qualificato',
            'categories': ['Caldo'],
            'sources': ['Website', 'Referral'],
            'priorities': ['Alta'],
            'min_budget': 5000,
            'notes': 'Sequenza per lead qualificati',
            'is_active': True,
            'created_by': 1
        }
    ]
    
    print(f"📞 Creazione {len(sequences)} sequenze...")
    
    created_sequences = []
    for sequence in sequences:
        try:
            sequence_id = db.create_contact_sequence(sequence)
            if sequence_id:
                created_sequences.append(sequence_id)
                print(f"  ✅ Sequenza '{sequence['name']}' creata (ID: {sequence_id})")
            else:
                print(f"  ❌ Errore creazione sequenza '{sequence['name']}'")
        except Exception as e:
            print(f"  ❌ Errore creazione sequenza '{sequence['name']}': {e}")
    
    print(f"\n📊 Sequenze create: {len(created_sequences)}/{len(sequences)}")
    return created_sequences

def show_contact_stats():
    """Mostra statistiche sui contatti"""
    print("\n📊 Statistiche Contatti")
    print("=" * 40)
    
    db = DatabaseManager()
    
    try:
        # Statistiche template
        templates = db.get_contact_templates()
        print(f"📧 Template totali: {len(templates)}")
        
        # Template per tipo
        email_templates = [t for t in templates if t['type'] == 'Email']
        sms_templates = [t for t in templates if t['type'] == 'SMS']
        print(f"  📧 Template Email: {len(email_templates)}")
        print(f"  📱 Template SMS: {len(sms_templates)}")
        
        # Template per categoria
        categories = {}
        for template in templates:
            cat = template['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("  📋 Template per categoria:")
        for cat, count in categories.items():
            print(f"    - {cat}: {count}")
        
        # Statistiche sequenze
        sequences = db.get_contact_sequences()
        print(f"\n📞 Sequenze totali: {len(sequences)}")
        
        # Sequenze per tipo
        sequence_types = {}
        for sequence in sequences:
            seq_type = sequence['type']
            sequence_types[seq_type] = sequence_types.get(seq_type, 0) + 1
        
        print("  📋 Sequenze per tipo:")
        for seq_type, count in sequence_types.items():
            print(f"    - {seq_type}: {count}")
        
    except Exception as e:
        print(f"❌ Errore nel recupero statistiche: {e}")

if __name__ == "__main__":
    print("🚀 Test Modulo Contatti DASH_GESTIONE_LEAD")
    print("=" * 50)
    
    try:
        # Test template
        created_templates = test_contact_templates()
        
        # Test sequenze
        created_sequences = test_contact_sequences()
        
        # Mostra statistiche
        show_contact_stats()
        
        print("\n🎉 Test completato con successo!")
        print(f"📧 Template creati: {len(created_templates)}")
        print(f"📞 Sequenze create: {len(created_sequences)}")
        
    except Exception as e:
        print(f"\n❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()
