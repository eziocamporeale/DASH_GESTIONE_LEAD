#!/usr/bin/env python3
"""
Script per creare la tabella broker_links_simple senza RLS
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager

def create_simple_broker_table():
    """Crea la tabella broker_links_simple senza RLS"""
    
    print("🔧 Creazione tabella broker_links_simple...")
    
    # Inizializza il database manager
    db = DatabaseManager()
    
    try:
        # SQL per creare la tabella semplice
        create_sql = """
        CREATE TABLE IF NOT EXISTS broker_links_simple (
            id SERIAL PRIMARY KEY,
            broker_name VARCHAR(255) NOT NULL,
            affiliate_link TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        print("📝 Creazione tabella...")
        
        # Prova a creare la tabella usando l'API Supabase
        # Nota: Supabase non supporta CREATE TABLE tramite API REST
        # Dobbiamo usare l'SQL Editor del dashboard
        
        print("❌ Supabase non supporta CREATE TABLE tramite API REST")
        print("\n💡 SOLUZIONE MANUALE:")
        print("1. Vai su https://supabase.com/dashboard")
        print("2. Seleziona il tuo progetto")
        print("3. Vai su 'SQL Editor'")
        print("4. Esegui questo comando:")
        print("   " + create_sql)
        print("5. Clicca 'Run' per eseguire il comando")
        
        return False
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

if __name__ == "__main__":
    create_simple_broker_table()
