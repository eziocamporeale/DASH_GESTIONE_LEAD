#!/usr/bin/env python3
"""
Script per testare il modulo task
Inserisce alcuni task di test
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager

def create_test_tasks():
    """Crea alcuni task di test"""
    
    db = DatabaseManager()
    
    # Task di test
    test_tasks = [
        {
            'title': 'Chiamata di follow-up Mario Rossi',
            'description': 'Chiamare Mario Rossi per aggiornamento sulla proposta commerciale',
            'task_type_id': 1,  # Chiamata
            'state_id': 1,  # Da Fare
            'priority_id': 1,  # Alta
            'assigned_to': 1,  # Admin
            'lead_id': 1,  # Mario Rossi
            'due_date': (date.today() + timedelta(days=2)).isoformat(),
            'created_by': 1
        },
        {
            'title': 'Preparazione demo per Giulia Bianchi',
            'description': 'Preparare demo personalizzata per TechStartup',
            'task_type_id': 3,  # Meeting
            'state_id': 2,  # In Corso
            'priority_id': 2,  # Media
            'assigned_to': 1,  # Admin
            'lead_id': 2,  # Giulia Bianchi
            'due_date': (date.today() + timedelta(days=5)).isoformat(),
            'created_by': 1
        },
        {
            'title': 'Invio proposta commerciale Luca Verdi',
            'description': 'Inviare proposta personalizzata per Corporation Italia',
            'task_type_id': 4,  # Proposta
            'state_id': 3,  # Completato
            'priority_id': 1,  # Alta
            'assigned_to': 1,  # Admin
            'lead_id': 3,  # Luca Verdi
            'due_date': date.today().isoformat(),
            'created_by': 1
        },
        {
            'title': 'Follow-up email Anna Neri',
            'description': 'Inviare email di follow-up dopo la proposta',
            'task_type_id': 2,  # Email
            'state_id': 1,  # Da Fare
            'priority_id': 2,  # Media
            'assigned_to': 1,  # Admin
            'lead_id': 4,  # Anna Neri
            'due_date': (date.today() + timedelta(days=1)).isoformat(),
            'created_by': 1
        },
        {
            'title': 'Qualificazione Paolo Gialli',
            'description': 'Qualificare il lead freddo da cold calling',
            'task_type_id': 6,  # Qualificazione
            'state_id': 1,  # Da Fare
            'priority_id': 3,  # Bassa
            'assigned_to': 1,  # Admin
            'lead_id': 5,  # Paolo Gialli
            'due_date': (date.today() + timedelta(days=7)).isoformat(),
            'created_by': 1
        },
        {
            'title': 'Meeting di presentazione Mario Rossi',
            'description': 'Meeting di presentazione prodotto con Azienda Innovativa',
            'task_type_id': 3,  # Meeting
            'state_id': 2,  # In Corso
            'priority_id': 1,  # Alta
            'assigned_to': 1,  # Admin
            'lead_id': 1,  # Mario Rossi
            'due_date': (date.today() + timedelta(days=3)).isoformat(),
            'created_by': 1
        },
        {
            'title': 'Preparazione documentazione tecnica',
            'description': 'Preparare documentazione tecnica per Luca Verdi',
            'task_type_id': 4,  # Proposta
            'state_id': 1,  # Da Fare
            'priority_id': 1,  # Alta
            'assigned_to': 1,  # Admin
            'lead_id': 3,  # Luca Verdi
            'due_date': (date.today() + timedelta(days=4)).isoformat(),
            'created_by': 1
        }
    ]
    
    print("🚀 Creazione task di test...")
    
    created_count = 0
    for i, task_data in enumerate(test_tasks, 1):
        try:
            task_id = db.create_task(task_data)
            if task_id:
                print(f"✅ Task {i} creato: {task_data['title']} (ID: {task_id})")
                created_count += 1
            else:
                print(f"❌ Errore creazione task {i}: {task_data['title']}")
        except Exception as e:
            print(f"❌ Errore creazione task {i}: {e}")
    
    print(f"\n📊 Risultato: {created_count}/{len(test_tasks)} task creati con successo")
    
    # Verifica
    all_tasks = db.get_tasks()
    print(f"📈 Totale task nel database: {len(all_tasks)}")
    
    return created_count

def show_task_stats():
    """Mostra statistiche sui task"""
    
    db = DatabaseManager()
    stats = db.get_task_stats()
    
    print("\n📊 Statistiche Task:")
    print("=" * 40)
    
    # Task totali
    total_tasks = stats['total_tasks'][0]['count'] if stats['total_tasks'] else 0
    print(f"📈 Task totali: {total_tasks}")
    
    # Task per stato
    print("\n📋 Task per Stato:")
    for state in stats['tasks_by_state']:
        print(f"  • {state['name']}: {state['count']}")
    
    # Task scaduti
    overdue_tasks = stats['overdue_tasks'][0]['count'] if stats['overdue_tasks'] else 0
    print(f"\n⏰ Task scaduti: {overdue_tasks}")

if __name__ == "__main__":
    print("🧪 Test Modulo Task")
    print("=" * 50)
    
    # Crea task di test
    created_count = create_test_tasks()
    
    if created_count > 0:
        # Mostra statistiche
        show_task_stats()
        
        print("\n✅ Test completato con successo!")
        print("🎯 Ora puoi testare il modulo task nell'applicazione")
    else:
        print("\n❌ Nessun task creato. Verifica il database.")
