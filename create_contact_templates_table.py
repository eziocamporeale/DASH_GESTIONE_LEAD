#!/usr/bin/env python3
"""
Script per creare la tabella contact_templates nel database Supabase
Creato da Ezio Camporeale
"""

import os
from database.database_manager import DatabaseManager

def create_contact_templates_table():
    """Crea la tabella contact_templates nel database Supabase"""
    
    print("📞 Creazione tabella contact_templates...")
    
    # Comando SQL per creare la tabella contact_templates
    sql_command = """
    CREATE TABLE IF NOT EXISTS contact_templates (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        type VARCHAR(20) NOT NULL CHECK (type IN ('email', 'sms', 'whatsapp')),
        subject VARCHAR(200),
        content TEXT NOT NULL,
        category VARCHAR(50),
        delay_hours INTEGER DEFAULT 0,
        max_retries INTEGER DEFAULT 3,
        priority INTEGER DEFAULT 1,
        is_active BOOLEAN DEFAULT TRUE,
        notes TEXT,
        created_by INTEGER REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    print("📋 Comando SQL da eseguire:")
    print(sql_command)
    print("\n" + "="*60)
    print("⚠️  ATTENZIONE: Questo comando deve essere eseguito manualmente!")
    print("="*60)
    print("\n📝 ISTRUZIONI:")
    print("1. Vai su: https://supabase.com/dashboard")
    print("2. Seleziona il tuo progetto")
    print("3. Vai su: 'SQL Editor'")
    print("4. Copia e incolla il comando SQL sopra")
    print("5. Clicca 'Run' per eseguire")
    print("\n✅ Dopo aver creato la tabella, i template standard potranno essere inseriti!")
    
    # Tentativo di creazione automatica (probabilmente fallirà)
    try:
        db = DatabaseManager()
        if db.use_supabase:
            print("\n🔄 Tentativo creazione automatica...")
            result = db.supabase.rpc('exec_sql', {'sql': sql_command}).execute()
            print("✅ Tabella creata automaticamente!")
        else:
            print("ℹ️ Database locale - creazione automatica non necessaria")
    except Exception as e:
        print(f"❌ Creazione automatica fallita: {e}")
        print("📝 Segui le istruzioni manuali sopra")

if __name__ == "__main__":
    create_contact_templates_table()
