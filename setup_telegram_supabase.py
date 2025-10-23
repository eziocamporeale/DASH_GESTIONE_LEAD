#!/usr/bin/env python3
"""
📱 TELEGRAM SUPABASE SETUP - Dashboard Gestione Lead
Script per creare le tabelle Telegram in Supabase
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path
import logging

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_telegram_tables():
    """Crea le tabelle Telegram in Supabase"""
    try:
        from database.database_manager import DatabaseManager
        
        print("🚀 Creando tabelle Telegram in Supabase...")
        
        db = DatabaseManager()
        
        # SQL per creare le tabelle
        create_tables_sql = """
        -- Tabella configurazione Telegram
        CREATE TABLE IF NOT EXISTS telegram_config (
            id TEXT PRIMARY KEY,
            bot_token TEXT NOT NULL,
            chat_id TEXT NOT NULL,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Tabella impostazioni notifiche
        CREATE TABLE IF NOT EXISTS notification_settings (
            id SERIAL PRIMARY KEY,
            notification_type VARCHAR(100) UNIQUE NOT NULL,
            is_enabled BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Tabella log notifiche
        CREATE TABLE IF NOT EXISTS notification_logs (
            id TEXT PRIMARY KEY,
            notification_type VARCHAR(100) NOT NULL,
            message TEXT NOT NULL,
            status VARCHAR(20) NOT NULL,
            error_message TEXT,
            sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            retry_count INTEGER DEFAULT 0
        );

        -- Indici per ottimizzazione
        CREATE INDEX IF NOT EXISTS idx_notification_logs_type ON notification_logs(notification_type);
        CREATE INDEX IF NOT EXISTS idx_notification_logs_status ON notification_logs(status);
        CREATE INDEX IF NOT EXISTS idx_notification_logs_sent_at ON notification_logs(sent_at);
        CREATE INDEX IF NOT EXISTS idx_notification_settings_type ON notification_settings(notification_type);
        """
        
        # Esegui le query SQL
        print("📋 Eseguendo query SQL...")
        
        # Dividi le query e eseguile una per una
        queries = [q.strip() for q in create_tables_sql.split(';') if q.strip()]
        
        for i, query in enumerate(queries, 1):
            if query:
                print(f"  {i}. Eseguendo query...")
                try:
                    # Usa execute per query DDL
                    db.supabase.rpc('exec_sql', {'sql': query}).execute()
                    print(f"  ✅ Query {i} eseguita con successo")
                except Exception as e:
                    print(f"  ⚠️ Query {i} fallita (potrebbe già esistere): {e}")
        
        # Inserisci impostazioni notifiche di default
        print("📋 Inserendo impostazioni notifiche di default...")
        
        default_settings = [
            # Lead
            {'notification_type': 'lead_new_lead', 'is_enabled': True},
            {'notification_type': 'lead_status_changed', 'is_enabled': True},
            {'notification_type': 'lead_assigned', 'is_enabled': True},
            {'notification_type': 'lead_daily_report', 'is_enabled': False},
            
            # Task
            {'notification_type': 'task_new_task', 'is_enabled': True},
            {'notification_type': 'task_completed', 'is_enabled': True},
            {'notification_type': 'task_due_soon', 'is_enabled': True},
            {'notification_type': 'task_daily_report', 'is_enabled': False},
            
            # Utenti
            {'notification_type': 'user_new_user', 'is_enabled': True},
            {'notification_type': 'user_login', 'is_enabled': False},
            {'notification_type': 'user_daily_report', 'is_enabled': False},
        ]
        
        for setting in default_settings:
            try:
                db.supabase.table('notification_settings').upsert(
                    setting, 
                    on_conflict='notification_type'
                ).execute()
                print(f"  ✅ Impostazione {setting['notification_type']} inserita")
            except Exception as e:
                print(f"  ⚠️ Errore inserimento {setting['notification_type']}: {e}")
        
        print("✅ Setup tabelle Telegram completato!")
        return True
        
    except Exception as e:
        print(f"❌ Errore setup tabelle Telegram: {e}")
        return False

def verify_tables():
    """Verifica che le tabelle siano state create"""
    try:
        from database.database_manager import DatabaseManager
        
        print("🔍 Verificando tabelle create...")
        
        db = DatabaseManager()
        
        tables_to_check = ['telegram_config', 'notification_settings', 'notification_logs']
        
        for table in tables_to_check:
            try:
                response = db.supabase.table(table).select('*').limit(1).execute()
                print(f"✅ Tabella {table} verificata")
            except Exception as e:
                print(f"❌ Errore verifica tabella {table}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore verifica tabelle: {e}")
        return False

def main():
    """Esegue il setup completo"""
    print("🚀 Setup Sistema Telegram per Dashboard Lead")
    print("=" * 50)
    
    # Crea le tabelle
    if create_telegram_tables():
        print("\n🔍 Verificando setup...")
        verify_tables()
        print("\n🎉 Setup completato con successo!")
        print("\n📋 Prossimi passi:")
        print("1. Configura il bot Telegram nelle Impostazioni")
        print("2. Testa l'invio di notifiche")
        print("3. Verifica i log delle notifiche")
    else:
        print("\n❌ Setup fallito. Controlla i log per dettagli.")

if __name__ == "__main__":
    main()
