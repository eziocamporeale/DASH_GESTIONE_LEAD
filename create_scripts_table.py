#!/usr/bin/env python3
"""
Script per creare la tabella scripts nel database Supabase
Creato da Ezio Camporeale
"""

import os
from database.database_manager import DatabaseManager

def create_scripts_table():
    """Crea la tabella scripts nel database Supabase"""
    
    print("🔧 Creazione tabella scripts...")
    
    # Comando SQL per creare la tabella scripts
    sql_command = """
    CREATE TABLE IF NOT EXISTS scripts (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        content TEXT NOT NULL,
        script_type VARCHAR(50) NOT NULL,
        category VARCHAR(50) NOT NULL,
        created_by UUID REFERENCES auth.users(id),
        is_active BOOLEAN DEFAULT TRUE,
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
    print("\n✅ Dopo aver creato la tabella, la sezione Script funzionerà correttamente!")
    
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
    create_scripts_table()