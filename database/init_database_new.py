#!/usr/bin/env python3
"""
Inizializzazione Database DASH_GESTIONE_LEAD - Nuovo Schema
Creato da Ezio Camporeale
"""

import sqlite3
import os
import sys
from pathlib import Path
import bcrypt
import json

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

from config import DATABASE_PATH, LEAD_STATES, LEAD_PRIORITIES, LEAD_CATEGORIES, USER_ROLES, TASK_STATES

def create_database():
    """Crea il database e le tabelle"""
    try:
        # Assicurati che la directory data esista
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Connetti al database (lo crea se non esiste)
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        print("📁 Creazione database...")
        
        # Leggi e esegui lo schema SQL
        schema_file = current_dir / "database" / "schema.sql"
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Esegui le query SQL
        cursor.executescript(schema_sql)
        
        print("✅ Schema database creato con successo")
        
        # Popola le tabelle con dati di default
        populate_default_data(cursor)
        
        conn.commit()
        conn.close()
        
        print("✅ Database inizializzato con successo!")
        print(f"📂 Percorso database: {DATABASE_PATH}")
        
    except Exception as e:
        print(f"❌ Errore durante la creazione del database: {e}")
        raise

def populate_default_data(cursor):
    """Popola le tabelle con dati di default"""
    print("📊 Popolamento dati di default...")
    
    # Inserisci ruoli
    print("  👥 Inserimento ruoli...")
    for role in USER_ROLES:
        cursor.execute("""
            INSERT OR IGNORE INTO roles (id, name, description, permissions)
            VALUES (?, ?, ?, ?)
        """, (role['id'], role['name'], f"Ruolo {role['name']}", json.dumps(role['permissions'])))
    
    # Inserisci stati lead
    print("  📈 Inserimento stati lead...")
    for state in LEAD_STATES:
        cursor.execute("""
            INSERT OR IGNORE INTO lead_states (id, name, color, description, order_index)
            VALUES (?, ?, ?, ?, ?)
        """, (state['id'], state['name'], state['color'], f"Stato {state['name']}", state['order']))
    
    # Inserisci priorità lead
    print("  ⚡ Inserimento priorità lead...")
    for priority in LEAD_PRIORITIES:
        cursor.execute("""
            INSERT OR IGNORE INTO lead_priorities (id, name, color, description)
            VALUES (?, ?, ?, ?)
        """, (priority['id'], priority['name'], priority['color'], f"Priorità {priority['name']}"))
    
    # Inserisci categorie lead
    print("  🏷️ Inserimento categorie lead...")
    for category in LEAD_CATEGORIES:
        cursor.execute("""
            INSERT OR IGNORE INTO lead_categories (id, name, color, description)
            VALUES (?, ?, ?, ?)
        """, (category['id'], category['name'], category['color'], category['description']))
    
    # Inserisci stati task
    print("  ✅ Inserimento stati task...")
    for state in TASK_STATES:
        cursor.execute("""
            INSERT OR IGNORE INTO task_states (id, name, color, description)
            VALUES (?, ?, ?, ?)
        """, (state['id'], state['name'], state['color'], f"Stato task {state['name']}"))
    
    # Inserisci fonti lead di default
    print("  📞 Inserimento fonti lead...")
    default_sources = [
        ("Website", "Lead dal sito web"),
        ("Social Media", "Lead dai social media"),
        ("Email Marketing", "Campagne email marketing"),
        ("Referral", "Referral da clienti"),
        ("Cold Call", "Cold calling"),
        ("Eventi", "Eventi e fiere"),
        ("LinkedIn", "LinkedIn"),
        ("Altro", "Altre fonti")
    ]
    
    for source in default_sources:
        cursor.execute("""
            INSERT OR IGNORE INTO lead_sources (name, description)
            VALUES (?, ?)
        """, source)
    
    # Inserisci tipi task di default
    print("  📋 Inserimento tipi task...")
    default_task_types = [
        ("Chiamata", "Chiamata al lead", "#17A2B8"),
        ("Email", "Invio email", "#28A745"),
        ("Meeting", "Riunione con il lead", "#FFC107"),
        ("Proposta", "Preparazione proposta", "#FD7E14"),
        ("Follow-up", "Follow-up", "#6C757D"),
        ("Qualificazione", "Qualificazione lead", "#DC3545")
    ]
    
    for task_type in default_task_types:
        cursor.execute("""
            INSERT OR IGNORE INTO task_types (name, description, color)
            VALUES (?, ?, ?)
        """, task_type)
    
    # Crea utente admin di default
    print("  👤 Creazione utente admin...")
    admin_password = "admin123"  # Cambiare in produzione!
    password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
    
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, email, password_hash, first_name, last_name, role_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("admin", "admin@example.com", password_hash.decode('utf-8'), "Admin", "User", 1))
    
    # Inserisci impostazioni di default
    print("  ⚙️ Inserimento impostazioni...")
    default_settings = [
        ("company_name", "La Tua Azienda", "Nome dell'azienda"),
        ("company_email", "info@tuazienda.com", "Email aziendale"),
        ("company_phone", "+39 123 456 789", "Telefono aziendale"),
        ("items_per_page", "20", "Numero di elementi per pagina"),
        ("auto_assign_leads", "true", "Assegnazione automatica lead"),
        ("lead_scoring_enabled", "true", "Abilita scoring automatico lead"),
        ("email_notifications", "true", "Abilita notifiche email"),
        ("backup_frequency", "daily", "Frequenza backup (daily/weekly/monthly)")
    ]
    
    for setting in default_settings:
        cursor.execute("""
            INSERT OR IGNORE INTO settings (key, value, description)
            VALUES (?, ?, ?)
        """, setting)
    
    print("✅ Dati di default inseriti con successo!")

def verify_database():
    """Verifica che il database sia stato creato correttamente"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verifica tabelle principali
        tables = [
            'users', 'roles', 'departments', 'leads', 'lead_categories', 
            'lead_states', 'lead_priorities', 'lead_sources', 'tasks', 
            'task_types', 'task_states', 'contact_templates', 'contact_sequences', 
            'contact_steps', 'lead_contacts', 'activity_log', 'settings'
        ]
        
        print("\n🔍 Verifica struttura database...")
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print(f"  ✅ Tabella {table} presente")
            else:
                print(f"  ❌ Tabella {table} mancante")
        
        # Verifica dati di default
        print("\n📊 Verifica dati di default...")
        
        # Conta utenti
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"  👥 Utenti: {user_count}")
        
        # Conta ruoli
        cursor.execute("SELECT COUNT(*) FROM roles")
        role_count = cursor.fetchone()[0]
        print(f"  🎭 Ruoli: {role_count}")
        
        # Conta stati lead
        cursor.execute("SELECT COUNT(*) FROM lead_states")
        state_count = cursor.fetchone()[0]
        print(f"  📈 Stati lead: {state_count}")
        
        # Conta fonti lead
        cursor.execute("SELECT COUNT(*) FROM lead_sources")
        source_count = cursor.fetchone()[0]
        print(f"  📞 Fonti lead: {source_count}")
        
        # Conta template
        cursor.execute("SELECT COUNT(*) FROM contact_templates")
        template_count = cursor.fetchone()[0]
        print(f"  📧 Template: {template_count}")
        
        # Conta sequenze
        cursor.execute("SELECT COUNT(*) FROM contact_sequences")
        sequence_count = cursor.fetchone()[0]
        print(f"  📞 Sequenze: {sequence_count}")
        
        conn.close()
        
        print("\n✅ Verifica database completata!")
        
    except Exception as e:
        print(f"❌ Errore durante la verifica: {e}")

if __name__ == "__main__":
    print("🚀 Inizializzazione Database DASH_GESTIONE_LEAD - Nuovo Schema")
    print("=" * 60)
    
    try:
        create_database()
        verify_database()
        
        print("\n🎉 Database pronto per l'uso!")
        print("\n📝 Credenziali di default:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Email: admin@example.com")
        print("\n⚠️  IMPORTANTE: Cambiare la password admin in produzione!")
        
    except Exception as e:
        print(f"\n❌ Errore fatale: {e}")
        sys.exit(1)
