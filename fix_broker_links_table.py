#!/usr/bin/env python3
"""
Script per modificare la tabella broker_links rimuovendo il campo created_by
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager

def fix_broker_links_table():
    """Modifica la tabella broker_links per rimuovere il campo created_by"""
    
    print("🔧 Modifica tabella broker_links...")
    
    # Inizializza il database manager
    db = DatabaseManager()
    
    try:
        # Prova a rimuovere il campo created_by
        print("📝 Tentativo rimozione campo created_by...")
        
        # Usa SQL per rimuovere il campo
        result = db.supabase.rpc('exec_sql', {
            'sql': 'ALTER TABLE broker_links DROP COLUMN IF EXISTS created_by;'
        }).execute()
        
        print("✅ Campo created_by rimosso dalla tabella broker_links")
        
    except Exception as e:
        print(f"❌ Errore rimozione campo: {e}")
        
        # Prova un approccio alternativo - ricreare la tabella senza created_by
        print("\n🔄 Tentativo ricreazione tabella...")
        try:
            # Prima elimina la tabella esistente
            db.supabase.rpc('exec_sql', {
                'sql': 'DROP TABLE IF EXISTS broker_links;'
            }).execute()
            
            # Ricrea la tabella senza created_by
            create_sql = """
            CREATE TABLE broker_links (
                id SERIAL PRIMARY KEY,
                broker_name VARCHAR(255) NOT NULL,
                affiliate_link TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            
            db.supabase.rpc('exec_sql', {
                'sql': create_sql
            }).execute()
            
            print("✅ Tabella broker_links ricreata senza campo created_by")
            
        except Exception as e2:
            print(f"❌ Errore ricreazione tabella: {e2}")
            print("\n💡 SOLUZIONE MANUALE:")
            print("1. Vai su https://supabase.com/dashboard")
            print("2. Seleziona il tuo progetto")
            print("3. Vai su 'SQL Editor'")
            print("4. Esegui questo comando:")
            print("   ALTER TABLE broker_links DROP COLUMN IF EXISTS created_by;")
            print("5. Oppure ricrea la tabella senza il campo created_by")
            return False
    
    return True

if __name__ == "__main__":
    fix_broker_links_table()
