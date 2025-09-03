#!/usr/bin/env python3
"""
Script di migrazione da SQLite a Supabase
Creato da Ezio Camporeale
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime
import logging

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

from config import DATABASE_PATH, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SupabaseMigrator:
    """Gestisce la migrazione da SQLite a Supabase"""
    
    def __init__(self):
        """Inizializza il migratore"""
        self.sqlite_path = DATABASE_PATH
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Connessione SQLite
        self.sqlite_conn = sqlite3.connect(self.sqlite_path)
        self.sqlite_conn.row_factory = sqlite3.Row
        
        logger.info("✅ Migratore Supabase inizializzato")
    
    def migrate_all(self):
        """Esegue la migrazione completa"""
        logger.info("🚀 Iniziando migrazione completa a Supabase...")
        
        try:
            # 1. Verifica connessione Supabase
            self.test_supabase_connection()
            
            # 2. Migra tabelle di lookup
            self.migrate_lookup_tables()
            
            # 3. Migra utenti
            self.migrate_users()
            
            # 4. Migra lead
            self.migrate_leads()
            
            # 5. Migra task
            self.migrate_tasks()
            
            # 6. Migra contatti
            self.migrate_contacts()
            
            # 7. Migra impostazioni
            self.migrate_settings()
            
            # 8. Migra log attività
            self.migrate_activity_log()
            
            logger.info("✅ Migrazione completata con successo!")
            
        except Exception as e:
            logger.error(f"❌ Errore durante la migrazione: {e}")
            raise
        finally:
            self.sqlite_conn.close()
    
    def test_supabase_connection(self):
        """Testa la connessione a Supabase"""
        try:
            # Test semplice query
            result = self.supabase.table('roles').select('*').limit(1).execute()
            logger.info("✅ Connessione Supabase verificata")
        except Exception as e:
            logger.error(f"❌ Errore connessione Supabase: {e}")
            raise
    
    def migrate_lookup_tables(self):
        """Migra le tabelle di lookup"""
        logger.info("📋 Migrando tabelle di lookup...")
        
        # Ruoli
        self.migrate_table('roles', ['id', 'name', 'description', 'permissions'])
        
        # Dipartimenti
        self.migrate_table('departments', ['id', 'name', 'description'])
        
        # Stati lead
        self.migrate_table('lead_states', ['id', 'name', 'color', 'order_index', 'description'])
        
        # Priorità lead
        self.migrate_table('lead_priorities', ['id', 'name', 'color', 'description'])
        
        # Categorie lead
        self.migrate_table('lead_categories', ['id', 'name', 'color', 'description'])
        
        # Fonti lead
        self.migrate_table('lead_sources', ['id', 'name', 'description'])
        
        # Stati task
        self.migrate_table('task_states', ['id', 'name', 'color', 'description'])
        
        # Tipi task
        self.migrate_table('task_types', ['id', 'name', 'description'])
        
        logger.info("✅ Tabelle di lookup migrate")
    
    def migrate_users(self):
        """Migra gli utenti"""
        logger.info("👤 Migrando utenti...")
        
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT u.*, r.name as role_name, d.name as department_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            LEFT JOIN departments d ON u.department_id = d.id
        """)
        
        users = cursor.fetchall()
        
        for user in users:
            user_data = {
                'username': user['username'],
                'email': user['email'],
                'password_hash': user['password_hash'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'phone': user['phone'],
                'role_id': user['role_id'],
                'department_id': user['department_id'],
                'is_active': bool(user['is_active']),
                'is_admin': bool(user['is_admin']),
                'notes': user['notes'],
                'last_login': user['last_login'],
                'created_by': user['created_by']
            }
            
            try:
                # Controlla se l'utente esiste già
                existing = self.supabase.table('users').select('id').eq('username', user['username']).execute()
                
                if not existing.data:
                    # Inserisci nuovo utente
                    result = self.supabase.table('users').insert(user_data).execute()
                    logger.info(f"✅ Utente migrato: {user['username']}")
                else:
                    logger.info(f"⚠️ Utente già esistente: {user['username']}")
                    
            except Exception as e:
                logger.error(f"❌ Errore migrazione utente {user['username']}: {e}")
        
        logger.info("✅ Utenti migrati")
    
    def migrate_leads(self):
        """Migra i lead"""
        logger.info("👥 Migrando lead...")
        
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT l.*, 
                   ls.name as state_name,
                   lp.name as priority_name,
                   lc.name as category_name,
                   lsrc.name as source_name,
                   u.username as assigned_username
            FROM leads l
            LEFT JOIN lead_states ls ON l.state_id = ls.id
            LEFT JOIN lead_priorities lp ON l.priority_id = lp.id
            LEFT JOIN lead_categories lc ON l.category_id = lc.id
            LEFT JOIN lead_sources lsrc ON l.source_id = lsrc.id
            LEFT JOIN users u ON l.assigned_to = u.id
        """)
        
        leads = cursor.fetchall()
        
        for lead in leads:
            lead_data = {
                'name': lead['name'],
                'email': lead['email'],
                'phone': lead['phone'],
                'company': lead['company'],
                'position': lead['position'],
                'budget': float(lead['budget']) if lead['budget'] else None,
                'expected_close_date': lead['expected_close_date'],
                'category_id': lead['category_id'],
                'state_id': lead['state_id'],
                'priority_id': lead['priority_id'],
                'source_id': lead['source_id'],
                'assigned_to': lead['assigned_to'],
                'notes': lead['notes'],
                'created_by': lead['created_by']
            }
            
            try:
                result = self.supabase.table('leads').insert(lead_data).execute()
                logger.info(f"✅ Lead migrato: {lead['name']}")
            except Exception as e:
                logger.error(f"❌ Errore migrazione lead {lead['name']}: {e}")
        
        logger.info("✅ Lead migrati")
    
    def migrate_tasks(self):
        """Migra i task"""
        logger.info("✅ Migrando task...")
        
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT t.*, 
                   ts.name as state_name,
                   tt.name as type_name,
                   lp.name as priority_name,
                   l.name as lead_name,
                   u.username as assigned_username
            FROM tasks t
            LEFT JOIN task_states ts ON t.state_id = ts.id
            LEFT JOIN task_types tt ON t.task_type_id = tt.id
            LEFT JOIN lead_priorities lp ON t.priority_id = lp.id
            LEFT JOIN leads l ON t.lead_id = l.id
            LEFT JOIN users u ON t.assigned_to = u.id
        """)
        
        tasks = cursor.fetchall()
        
        for task in tasks:
            task_data = {
                'title': task['title'],
                'description': task['description'],
                'task_type_id': task['task_type_id'],
                'state_id': task['state_id'],
                'priority_id': task['priority_id'],
                'lead_id': task['lead_id'],
                'assigned_to': task['assigned_to'],
                'due_date': task['due_date'],
                'completed_at': task['completed_at'],
                'created_by': task['created_by']
            }
            
            try:
                result = self.supabase.table('tasks').insert(task_data).execute()
                logger.info(f"✅ Task migrato: {task['title']}")
            except Exception as e:
                logger.error(f"❌ Errore migrazione task {task['title']}: {e}")
        
        logger.info("✅ Task migrati")
    
    def migrate_contacts(self):
        """Migra i contatti"""
        logger.info("📞 Migrando contatti...")
        
        # Template contatti
        self.migrate_table('contact_templates', [
            'id', 'name', 'type', 'subject', 'content', 'category', 
            'delay_hours', 'max_retries', 'priority', 'is_active', 'notes', 'created_by'
        ])
        
        # Sequenze contatti
        self.migrate_table('contact_sequences', [
            'id', 'name', 'type', 'trigger_event', 'categories', 'sources', 
            'priorities', 'min_budget', 'is_active', 'notes', 'created_by'
        ])
        
        # Step sequenze
        self.migrate_table('contact_steps', [
            'id', 'sequence_id', 'template_id', 'step_order', 'delay_hours'
        ])
        
        # Cronologia contatti
        self.migrate_table('lead_contacts', [
            'id', 'lead_id', 'template_id', 'sequence_id', 'type', 'subject', 
            'content', 'status', 'sent_at', 'delivered_at', 'opened_at', 
            'clicked_at', 'response_received', 'response_content', 'created_by'
        ])
        
        logger.info("✅ Contatti migrati")
    
    def migrate_settings(self):
        """Migra le impostazioni"""
        logger.info("⚙️ Migrando impostazioni...")
        
        self.migrate_table('settings', ['id', 'key', 'value', 'description'])
        
        logger.info("✅ Impostazioni migrate")
    
    def migrate_activity_log(self):
        """Migra il log attività"""
        logger.info("📝 Migrando log attività...")
        
        self.migrate_table('activity_log', [
            'id', 'user_id', 'action', 'entity_type', 'entity_id', 
            'details', 'ip_address', 'user_agent'
        ])
        
        logger.info("✅ Log attività migrato")
    
    def migrate_table(self, table_name: str, columns: list):
        """Migra una singola tabella"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        
        rows = cursor.fetchall()
        
        for row in rows:
            row_data = {}
            for col in columns:
                if col in row.keys():
                    value = row[col]
                    
                    # Gestisci tipi di dati speciali
                    if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
                        try:
                            value = json.loads(value)
                        except:
                            pass
                    
                    row_data[col] = value
            
            try:
                # Controlla se il record esiste già
                if 'id' in row_data:
                    existing = self.supabase.table(table_name).select('id').eq('id', row_data['id']).execute()
                    
                    if not existing.data:
                        result = self.supabase.table(table_name).insert(row_data).execute()
                        logger.info(f"✅ {table_name} migrato: ID {row_data['id']}")
                    else:
                        logger.info(f"⚠️ {table_name} già esistente: ID {row_data['id']}")
                else:
                    result = self.supabase.table(table_name).insert(row_data).execute()
                    logger.info(f"✅ {table_name} migrato")
                    
            except Exception as e:
                logger.error(f"❌ Errore migrazione {table_name}: {e}")
    
    def verify_migration(self):
        """Verifica la migrazione confrontando i conteggi"""
        logger.info("🔍 Verificando migrazione...")
        
        tables = [
            'roles', 'departments', 'users', 'lead_states', 'lead_priorities',
            'lead_categories', 'lead_sources', 'leads', 'task_states', 'task_types',
            'tasks', 'contact_templates', 'contact_sequences', 'contact_steps',
            'lead_contacts', 'settings', 'activity_log'
        ]
        
        for table in tables:
            try:
                # Conta SQLite
                cursor = self.sqlite_conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                sqlite_count = cursor.fetchone()[0]
                
                # Conta Supabase
                result = self.supabase.table(table).select('id', count='exact').execute()
                supabase_count = result.count
                
                logger.info(f"📊 {table}: SQLite={sqlite_count}, Supabase={supabase_count}")
                
                if sqlite_count != supabase_count:
                    logger.warning(f"⚠️ Discrepanza in {table}: SQLite={sqlite_count}, Supabase={supabase_count}")
                
            except Exception as e:
                logger.error(f"❌ Errore verifica {table}: {e}")
        
        logger.info("✅ Verifica completata")

def main():
    """Funzione principale"""
    print("🚀 MIGRAZIONE SQLITE → SUPABASE")
    print("=" * 50)
    
    try:
        migrator = SupabaseMigrator()
        
        # Esegui migrazione
        migrator.migrate_all()
        
        # Verifica migrazione
        migrator.verify_migration()
        
        print("\n✅ MIGRAZIONE COMPLETATA CON SUCCESSO!")
        print("🎯 Il database è ora su Supabase")
        print("🔧 Ricorda di aggiornare USE_SUPABASE = True in config.py")
        
    except Exception as e:
        print(f"\n❌ ERRORE DURANTE LA MIGRAZIONE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
