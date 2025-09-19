#!/usr/bin/env python3
"""
Script Backup Database Supabase per DASH_GESTIONE_LEAD
Scarica tutti i dati dal database Supabase e li salva in locale
Creato da Ezio Camporeale
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import sys
from typing import Dict, List, Any

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("❌ Libreria supabase non installata. Installa con: pip install supabase")

class SupabaseBackup:
    """Gestisce il backup completo del database Supabase"""
    
    def __init__(self):
        """Inizializza il backup manager"""
        if not SUPABASE_AVAILABLE:
            raise ImportError("Libreria supabase non disponibile")
        
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.backup_dir = Path(__file__).parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Timestamp per il backup
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_name = f"supabase_backup_{self.timestamp}"
        
    def get_all_tables(self) -> List[str]:
        """Ottiene la lista di tutte le tabelle nel database"""
        try:
            # Query per ottenere tutte le tabelle
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
            """
            
            result = self.supabase.rpc('execute_sql', {'query': query}).execute()
            tables = [row['table_name'] for row in result.data]
            
            print(f"📋 Trovate {len(tables)} tabelle: {', '.join(tables)}")
            return tables
            
        except Exception as e:
            print(f"⚠️ Errore ottenimento tabelle, uso lista predefinita: {e}")
            # Lista predefinita delle tabelle conosciute
            return [
                'roles', 'departments', 'users', 'lead_categories', 
                'lead_states', 'lead_priorities', 'lead_sources', 'leads',
                'task_types', 'task_states', 'tasks', 'contact_templates',
                'contact_sequences', 'contact_steps', 'lead_contacts', 
                'activity_log', 'settings'
            ]
    
    def backup_table_data(self, table_name: str) -> List[Dict]:
        """Backup dei dati di una singola tabella"""
        try:
            print(f"📥 Scaricando dati tabella: {table_name}")
            
            # Ottieni tutti i dati dalla tabella
            result = self.supabase.table(table_name).select("*").execute()
            
            if result.data:
                print(f"✅ {table_name}: {len(result.data)} record scaricati")
                return result.data
            else:
                print(f"ℹ️ {table_name}: tabella vuota")
                return []
                
        except Exception as e:
            print(f"❌ Errore backup tabella {table_name}: {e}")
            return []
    
    def create_sqlite_backup(self, all_data: Dict[str, List[Dict]]) -> str:
        """Crea un backup SQLite con tutti i dati"""
        backup_path = self.backup_dir / f"{self.backup_name}.db"
        
        try:
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Crea le tabelle e inserisci i dati
            for table_name, data in all_data.items():
                if not data:
                    continue
                    
                # Crea la tabella basandosi sui dati
                if data:
                    columns = list(data[0].keys())
                    create_sql = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {', '.join([f"{col} TEXT" for col in columns])}
                    );
                    """
                    cursor.execute(create_sql)
                    
                    # Inserisci i dati
                    for row in data:
                        placeholders = ', '.join(['?' for _ in columns])
                        values = [str(row.get(col, '')) for col in columns]
                        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                        cursor.execute(insert_sql, values)
            
            conn.commit()
            conn.close()
            
            print(f"✅ Backup SQLite creato: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Errore creazione backup SQLite: {e}")
            return ""
    
    def create_json_backup(self, all_data: Dict[str, List[Dict]]) -> str:
        """Crea un backup JSON con tutti i dati"""
        backup_path = self.backup_dir / f"{self.backup_name}.json"
        
        try:
            # Aggiungi metadati al backup
            backup_info = {
                'backup_timestamp': self.timestamp,
                'backup_date': datetime.now().isoformat(),
                'supabase_url': SUPABASE_URL,
                'tables_count': len(all_data),
                'total_records': sum(len(data) for data in all_data.values()),
                'data': all_data
            }
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Backup JSON creato: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Errore creazione backup JSON: {e}")
            return ""
    
    def create_sql_backup(self, all_data: Dict[str, List[Dict]]) -> str:
        """Crea un backup SQL con tutti i dati"""
        backup_path = self.backup_dir / f"{self.backup_name}.sql"
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(f"-- Backup Supabase DASH_GESTIONE_LEAD\n")
                f.write(f"-- Data: {datetime.now().isoformat()}\n")
                f.write(f"-- URL: {SUPABASE_URL}\n\n")
                
                for table_name, data in all_data.items():
                    if not data:
                        continue
                    
                    f.write(f"-- Tabella: {table_name}\n")
                    f.write(f"-- Record: {len(data)}\n\n")
                    
                    # Crea INSERT statements
                    for row in data:
                        columns = list(row.keys())
                        values = [f"'{str(row[col]).replace(chr(39), chr(39)+chr(39))}'" for col in columns]
                        
                        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
                        f.write(insert_sql)
                    
                    f.write("\n")
            
            print(f"✅ Backup SQL creato: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Errore creazione backup SQL: {e}")
            return ""
    
    def run_full_backup(self) -> Dict[str, str]:
        """Esegue il backup completo del database"""
        print("🚀 Inizio backup completo database Supabase...")
        print(f"📅 Timestamp: {self.timestamp}")
        print(f"📁 Directory backup: {self.backup_dir}")
        print("-" * 50)
        
        # Ottieni tutte le tabelle
        tables = self.get_all_tables()
        
        # Backup di tutte le tabelle
        all_data = {}
        for table in tables:
            all_data[table] = self.backup_table_data(table)
        
        print("-" * 50)
        print("📊 Riepilogo backup:")
        total_records = 0
        for table, data in all_data.items():
            records = len(data)
            total_records += records
            print(f"  {table}: {records} record")
        
        print(f"📈 Totale record: {total_records}")
        print("-" * 50)
        
        # Crea i diversi formati di backup
        backup_files = {}
        
        # Backup JSON
        json_file = self.create_json_backup(all_data)
        if json_file:
            backup_files['json'] = json_file
        
        # Backup SQL
        sql_file = self.create_sql_backup(all_data)
        if sql_file:
            backup_files['sql'] = sql_file
        
        # Backup SQLite
        sqlite_file = self.create_sqlite_backup(all_data)
        if sqlite_file:
            backup_files['sqlite'] = sqlite_file
        
        print("✅ Backup completato con successo!")
        return backup_files

def main():
    """Funzione principale per eseguire il backup"""
    try:
        backup_manager = SupabaseBackup()
        backup_files = backup_manager.run_full_backup()
        
        print("\n🎉 Backup completato!")
        print("📁 File creati:")
        for format_type, file_path in backup_files.items():
            print(f"  {format_type.upper()}: {file_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante il backup: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Backup eseguito con successo!")
    else:
        print("\n❌ Backup fallito!")
        sys.exit(1)
