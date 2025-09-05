#!/usr/bin/env python3
"""
Script per creare la tabella contact_sequences nel database Supabase
Creato da Ezio Camporeale
"""

import os
from database.database_manager import DatabaseManager

def create_contact_sequences_table():
    """Crea la tabella contact_sequences nel database Supabase"""
    
    print("📞 Creazione tabella contact_sequences...")
    
    # Comando SQL per creare la tabella contact_sequences
    sql_command = """
    CREATE TABLE IF NOT EXISTS contact_sequences (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        type VARCHAR(50) NOT NULL,
        trigger_event VARCHAR(50),
        categories JSONB DEFAULT '[]',
        sources JSONB DEFAULT '[]',
        priorities JSONB DEFAULT '[]',
        min_budget DECIMAL(10,2),
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
    print("\n✅ Dopo aver creato la tabella, le sequenze contatti funzioneranno!")
    
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
    create_contact_sequences_table()
