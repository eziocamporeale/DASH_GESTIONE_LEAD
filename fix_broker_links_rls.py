#!/usr/bin/env python3
"""
Script per disabilitare RLS sulla tabella broker_links
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager

def fix_broker_links_rls():
    """Disabilita RLS sulla tabella broker_links"""
    
    print("🔧 Disabilitazione RLS per broker_links...")
    
    # Inizializza il database manager
    db = DatabaseManager()
    
    try:
        # Prova a disabilitare RLS usando l'API Supabase
        print("📝 Tentativo disabilitazione RLS tramite API...")
        
        # Usa la funzione SQL per disabilitare RLS
        result = db.supabase.rpc('exec', {
            'sql': 'ALTER TABLE broker_links DISABLE ROW LEVEL SECURITY;'
        }).execute()
        
        print("✅ RLS disabilitato per broker_links")
        
    except Exception as e:
        print(f"❌ Errore API Supabase: {e}")
        
        # Prova con connessione diretta PostgreSQL
        print("\n🔄 Tentativo connessione diretta PostgreSQL...")
        try:
            import psycopg2
            from config import SUPABASE_URL, SUPABASE_KEY
            
            # Estrai informazioni di connessione dall'URL Supabase
            # URL formato: https://xjjmpurdjqwjomxmqqks.supabase.co
            url_parts = SUPABASE_URL.replace('https://', '').split('.')
            project_id = url_parts[0]
            
            # Connessione diretta a PostgreSQL di Supabase
            conn = psycopg2.connect(
                host=f"db.{project_id}.supabase.co",
                database="postgres",
                user="postgres",
                password="your-db-password",  # Serve la password del database
                port="5432"
            )
            
            cursor = conn.cursor()
            cursor.execute("ALTER TABLE broker_links DISABLE ROW LEVEL SECURITY;")
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ RLS disabilitato con connessione diretta")
            
        except Exception as e2:
            print(f"❌ Errore connessione diretta: {e2}")
            print("\n💡 SOLUZIONE MANUALE:")
            print("1. Vai su https://supabase.com/dashboard")
            print("2. Seleziona il tuo progetto")
            print("3. Vai su 'Table Editor'")
            print("4. Seleziona la tabella 'broker_links'")
            print("5. Vai su 'Settings' (icona ingranaggio)")
            print("6. Disabilita 'Row Level Security'")
            print("7. Salva le modifiche")
            
            print("\n🔄 Oppure prova a creare un broker link senza RLS...")
            return False
    
    return True

if __name__ == "__main__":
    fix_broker_links_rls()
