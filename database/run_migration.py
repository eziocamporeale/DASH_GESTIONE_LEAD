#!/usr/bin/env python3
"""
Script per eseguire la migrazione del sistema gruppi lead
Esegue la migrazione in modo sicuro con verifiche pre e post
Creato da Ezio Camporeale
"""

import os
import sys
from pathlib import Path
from datetime import datetime

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

class MigrationRunner:
    """Gestisce l'esecuzione sicura della migrazione"""
    
    def __init__(self):
        """Inizializza il runner di migrazione"""
        if not SUPABASE_AVAILABLE:
            raise ImportError("Libreria supabase non disponibile")
        
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.migration_file = Path(__file__).parent / "migration_lead_groups.sql"
        
    def read_migration_sql(self) -> str:
        """Legge il file SQL di migrazione"""
        try:
            with open(self.migration_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Errore lettura file migrazione: {e}")
            return ""
    
    def execute_migration(self, sql_content: str) -> bool:
        """Esegue la migrazione usando le API Supabase"""
        try:
            print("🚀 Inizio esecuzione migrazione...")
            
            # Esegui la migrazione step by step usando le API Supabase
            success = True
            
            # 1. Crea tabella lead_groups
            print("📋 Creazione tabella lead_groups...")
            try:
                # Verifica se la tabella esiste già
                self.supabase.table('lead_groups').select('id').limit(1).execute()
                print("ℹ️ Tabella lead_groups già esistente")
            except:
                # Crea la tabella usando un approccio semplificato
                print("⚠️ Creazione tabella lead_groups richiede accesso admin Supabase")
                print("ℹ️ Procedi manualmente dal dashboard Supabase o usa SQL Editor")
                success = False
            
            # 2. Crea tabella user_lead_groups
            print("📋 Creazione tabella user_lead_groups...")
            try:
                self.supabase.table('user_lead_groups').select('id').limit(1).execute()
                print("ℹ️ Tabella user_lead_groups già esistente")
            except:
                print("⚠️ Creazione tabella user_lead_groups richiede accesso admin Supabase")
                success = False
            
            # 3. Verifica colonna group_id in leads
            print("📋 Verifica colonna group_id in leads...")
            try:
                self.supabase.table('leads').select('group_id').limit(1).execute()
                print("✅ Colonna group_id presente in leads")
            except:
                print("⚠️ Aggiunta colonna group_id richiede accesso admin Supabase")
                success = False
            
            # 4. Inserisci gruppi di default
            print("📋 Inserimento gruppi di default...")
            try:
                groups_data = [
                    {'name': 'Team Vendite', 'description': 'Gruppo venditori principale', 'color': '#28A745'},
                    {'name': 'Team Corporate', 'description': 'Venditori per clienti aziendali', 'color': '#007BFF'},
                    {'name': 'Team Retail', 'description': 'Venditori per clienti retail', 'color': '#FFC107'},
                    {'name': 'Team Nord', 'description': 'Venditori per clienti del Nord Italia', 'color': '#17A2B8'},
                    {'name': 'Team Sud', 'description': 'Venditori per clienti del Sud Italia', 'color': '#FD7E14'},
                    {'name': 'Team Centro', 'description': 'Venditori per clienti del Centro Italia', 'color': '#6F42C1'}
                ]
                
                for group in groups_data:
                    try:
                        # Prova a inserire il gruppo
                        result = self.supabase.table('lead_groups').insert(group).execute()
                        print(f"✅ Gruppo '{group['name']}' creato")
                    except Exception as e:
                        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                            print(f"ℹ️ Gruppo '{group['name']}' già esistente")
                        else:
                            print(f"⚠️ Errore creazione gruppo '{group['name']}': {e}")
                            
            except Exception as e:
                print(f"❌ Errore inserimento gruppi: {e}")
                success = False
            
            # 5. Assegna utenti al gruppo Team Vendite
            print("📋 Assegnazione utenti al gruppo Team Vendite...")
            try:
                # Ottieni tutti gli utenti
                users_result = self.supabase.table('users').select('id, role_id, is_admin').execute()
                users = users_result.data
                
                # Ottieni il gruppo Team Vendite
                groups_result = self.supabase.table('lead_groups').select('id').eq('name', 'Team Vendite').execute()
                if groups_result.data:
                    team_vendite_id = groups_result.data[0]['id']
                    
                    for user in users:
                        try:
                            assignment = {
                                'user_id': user['id'],
                                'group_id': team_vendite_id,
                                'can_manage': user.get('role_id') == 1 or user.get('is_admin', False)
                            }
                            
                            result = self.supabase.table('user_lead_groups').insert(assignment).execute()
                            print(f"✅ Utente {user['id']} assegnato al Team Vendite")
                            
                        except Exception as e:
                            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                                print(f"ℹ️ Utente {user['id']} già assegnato al Team Vendite")
                            else:
                                print(f"⚠️ Errore assegnazione utente {user['id']}: {e}")
                else:
                    print("⚠️ Gruppo Team Vendite non trovato")
                    
            except Exception as e:
                print(f"❌ Errore assegnazione utenti: {e}")
                success = False
            
            return success
            
        except Exception as e:
            print(f"❌ Errore durante migrazione: {e}")
            return False
    
    def verify_migration(self) -> bool:
        """Verifica che la migrazione sia stata eseguita correttamente"""
        try:
            print("🔍 Verifica post-migrazione...")
            
            # Verifica che le tabelle siano state create
            tables_to_check = ['lead_groups', 'user_lead_groups']
            
            for table in tables_to_check:
                try:
                    result = self.supabase.table(table).select("id").limit(1).execute()
                    print(f"✅ Tabella {table} verificata")
                except Exception as e:
                    print(f"❌ Tabella {table} non trovata: {e}")
                    return False
            
            # Verifica che la colonna group_id sia stata aggiunta a leads
            try:
                result = self.supabase.table('leads').select("group_id").limit(1).execute()
                print("✅ Colonna group_id aggiunta a leads")
            except Exception as e:
                print(f"❌ Colonna group_id non trovata in leads: {e}")
                return False
            
            # Conta i gruppi creati
            try:
                result = self.supabase.table('lead_groups').select("id").execute()
                groups_count = len(result.data)
                print(f"📊 Gruppi creati: {groups_count}")
            except Exception as e:
                print(f"⚠️ Errore conteggio gruppi: {e}")
            
            # Conta le assegnazioni utenti-gruppi
            try:
                result = self.supabase.table('user_lead_groups').select("id").execute()
                assignments_count = len(result.data)
                print(f"👥 Assegnazioni utenti-gruppi: {assignments_count}")
            except Exception as e:
                print(f"⚠️ Errore conteggio assegnazioni: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore durante verifica: {e}")
            return False
    
    def run_migration(self) -> bool:
        """Esegue la migrazione completa"""
        print("🛡️ MIGRAZIONE SISTEMA GRUPPI LEAD")
        print("=" * 50)
        print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🗄️ Database: {SUPABASE_URL}")
        print("=" * 50)
        
        # Leggi il file di migrazione
        sql_content = self.read_migration_sql()
        if not sql_content:
            print("❌ Impossibile leggere il file di migrazione")
            return False
        
        print(f"📄 File migrazione: {self.migration_file}")
        print(f"📏 Dimensione: {len(sql_content)} caratteri")
        print("-" * 50)
        
        # Chiedi conferma all'utente (solo se non in modalità test)
        print("⚠️ ATTENZIONE: Questa operazione modificherà il database!")
        print("📋 Assicurati di aver fatto un backup prima di procedere.")
        print()
        
        # Se siamo in modalità test (variabile d'ambiente), salta la conferma
        if os.getenv('MIGRATION_TEST_MODE'):
            print("🧪 Modalità test attiva - procedo automaticamente")
            response = 'sì'
        else:
            response = input("Vuoi procedere con la migrazione? (sì/no): ").lower().strip()
        
        if response not in ['sì', 'si', 's', 'yes', 'y']:
            print("❌ Migrazione annullata dall'utente")
            return False
        
        print("-" * 50)
        
        # Esegui la migrazione
        if not self.execute_migration(sql_content):
            print("❌ Migrazione fallita")
            return False
        
        print("-" * 50)
        
        # Verifica la migrazione
        if not self.verify_migration():
            print("❌ Verifica migrazione fallita")
            return False
        
        print("=" * 50)
        print("🎉 MIGRAZIONE COMPLETATA CON SUCCESSO!")
        print("📋 Prossimi passi:")
        print("   1. Testare il sistema con dati di esempio")
        print("   2. Aggiornare l'interfaccia per gestire i gruppi")
        print("   3. Assegnare lead esistenti ai gruppi appropriati")
        print("   4. Configurare i filtri per utenti e gruppi")
        print("=" * 50)
        
        return True

def main():
    """Funzione principale"""
    try:
        migration_runner = MigrationRunner()
        success = migration_runner.run_migration()
        
        if success:
            print("\n✅ Migrazione eseguita con successo!")
            return True
        else:
            print("\n❌ Migrazione fallita!")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante l'esecuzione: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
