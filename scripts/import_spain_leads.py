#!/usr/bin/env python3
"""
Script per importare lead spagnoli da Spain-1.xlsx
Converte il file Excel in formato compatibile con DASH_GESTIONE_LEAD
Creato da Ezio Camporeale
"""

import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime
import re

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import AuthManager

class SpainLeadsImporter:
    """Importatore per lead spagnoli"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.auth = AuthManager()
        
    def analyze_excel_file(self, file_path: str):
        """Analizza il file Excel per identificare la struttura"""
        print(f"🔍 Analisi file: {file_path}")
        
        try:
            df = pd.read_excel(file_path)
            
            print(f"📊 Struttura file:")
            print(f"   - Righe: {len(df)}")
            print(f"   - Colonne: {len(df.columns)}")
            
            # Identifica le colonne basandosi sui dati
            print(f"\n📋 Identificazione colonne:")
            
            # Analizza le prime righe per identificare i pattern
            sample_data = df.head(10)
            
            # Colonna 0 e 1: Email (duplicate)
            email_col = 0
            print(f"   - Colonna {email_col}: Email")
            
            # Colonna 2: Nome
            name_col = 2
            print(f"   - Colonna {name_col}: Nome")
            
            # Colonna 3: Cognome  
            surname_col = 3
            print(f"   - Colonna {surname_col}: Cognome")
            
            # Colonna 4: Paese
            country_col = 4
            print(f"   - Colonna {country_col}: Paese")
            
            # Colonna 5: Telefono
            phone_col = 5
            print(f"   - Colonna {phone_col}: Telefono")
            
            return df, {
                'email': email_col,
                'name': name_col, 
                'surname': surname_col,
                'country': country_col,
                'phone': phone_col
            }
            
        except Exception as e:
            print(f"❌ Errore nell'analisi del file: {e}")
            return None, None
    
    def clean_phone_number(self, phone):
        """Pulisce e formatta il numero di telefono"""
        if pd.isna(phone) or phone == '':
            return None
            
        # Converti in stringa
        phone_str = str(phone).strip()
        
        # Rimuovi spazi e caratteri speciali
        phone_clean = re.sub(r'[^\d+]', '', phone_str)
        
        # Se inizia con +34, mantieni
        if phone_clean.startswith('+34'):
            return phone_clean
        
        # Se inizia con 34, aggiungi +
        if phone_clean.startswith('34'):
            return '+' + phone_clean
            
        # Se inizia con 6 o 7 (mobile spagnoli), aggiungi +34
        if phone_clean.startswith(('6', '7')) and len(phone_clean) == 9:
            return '+34' + phone_clean
            
        # Se è un numero locale spagnolo, aggiungi +34
        if len(phone_clean) == 9 and phone_clean.startswith(('6', '7', '8', '9')):
            return '+34' + phone_clean
            
        return phone_clean
    
    def clean_email(self, email):
        """Pulisce l'email"""
        if pd.isna(email) or email == '':
            return None
            
        email_str = str(email).strip().lower()
        
        # Validazione email semplice
        if '@' in email_str and '.' in email_str:
            return email_str
            
        return None
    
    def convert_to_dashboard_format(self, df, column_mapping):
        """Converte i dati in formato compatibile con la dashboard"""
        print(f"\n🔄 Conversione dati in formato dashboard...")
        
        converted_data = []
        
        for index, row in df.iterrows():
            # Salta righe completamente vuote
            if pd.isna(row.iloc[0]) and pd.isna(row.iloc[1]):
                continue
                
            # Estrai i dati
            email = self.clean_email(row.iloc[column_mapping['email']])
            name = str(row.iloc[column_mapping['name']]).strip() if pd.notna(row.iloc[column_mapping['name']]) else ''
            surname = str(row.iloc[column_mapping['surname']]).strip() if pd.notna(row.iloc[column_mapping['surname']]) else ''
            country = str(row.iloc[column_mapping['country']]).strip() if pd.notna(row.iloc[column_mapping['country']]) else ''
            phone = self.clean_phone_number(row.iloc[column_mapping['phone']])
            
            # Salta se non abbiamo almeno email o nome
            if not email and not name:
                continue
                
            # Crea il record per la dashboard
            lead_data = {
                'first_name': name,
                'last_name': surname,
                'email': email,
                'phone': phone,
                'company': '',  # Non disponibile nel file originale
                'position': '',  # Non disponibile nel file originale
                'notes': f'Importato da Spain-1.xlsx - Paese: {country}',
                'lead_category_id': 1,  # Default category
                'lead_state_id': 1,     # Default state (Nuovo)
                'lead_priority_id': 2,  # Default priority (Media)
                'lead_source_id': 1,    # Default source
                'assigned_to': None,    # Non assegnato
                'group_id': None,       # Non assegnato a gruppo
                'created_by': 1         # Admin
            }
            
            converted_data.append(lead_data)
        
        print(f"✅ Convertiti {len(converted_data)} lead")
        return converted_data
    
    def import_to_database(self, leads_data, batch_size=100):
        """Importa i lead nel database"""
        print(f"\n📥 Importazione nel database...")
        
        success_count = 0
        error_count = 0
        
        for i in range(0, len(leads_data), batch_size):
            batch = leads_data[i:i + batch_size]
            
            print(f"   Importando batch {i//batch_size + 1}/{(len(leads_data)-1)//batch_size + 1} ({len(batch)} lead)...")
            
            for lead_data in batch:
                try:
                    success = self.db.create_lead(lead_data)
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        print(f"     ❌ Errore importazione: {lead_data.get('email', 'N/A')}")
                except Exception as e:
                    error_count += 1
                    print(f"     ❌ Errore: {e}")
        
        print(f"\n📊 Risultati importazione:")
        print(f"   ✅ Successi: {success_count}")
        print(f"   ❌ Errori: {error_count}")
        print(f"   📊 Totale: {success_count + error_count}")
        
        return success_count, error_count
    
    def create_summary_report(self, leads_data, success_count, error_count):
        """Crea un report di riepilogo"""
        print(f"\n📋 REPORT IMPORTAZIONE LEAD SPAGNOLI")
        print(f"=" * 50)
        print(f"📁 File sorgente: Spain-1.xlsx")
        print(f"📅 Data importazione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Lead processati: {len(leads_data)}")
        print(f"✅ Importati con successo: {success_count}")
        print(f"❌ Errori: {error_count}")
        print(f"📈 Tasso di successo: {(success_count/len(leads_data)*100):.1f}%")
        
        # Statistiche sui dati
        emails = [lead['email'] for lead in leads_data if lead['email']]
        phones = [lead['phone'] for lead in leads_data if lead['phone']]
        
        print(f"\n📊 Statistiche dati:")
        print(f"   📧 Email valide: {len(emails)}")
        print(f"   📞 Telefoni validi: {len(phones)}")
        
        # Esempi di lead importati
        print(f"\n📝 Esempi lead importati:")
        for i, lead in enumerate(leads_data[:5]):
            print(f"   {i+1}. {lead['first_name']} {lead['last_name']} - {lead['email']}")
    
    def run_import(self, file_path: str, test_mode: bool = False):
        """Esegue l'importazione completa"""
        print(f"🚀 INIZIO IMPORTAZIONE LEAD SPAGNOLI")
        print(f"=" * 50)
        
        # Analizza il file
        df, column_mapping = self.analyze_excel_file(file_path)
        if df is None:
            return False
        
        # Converti i dati
        leads_data = self.convert_to_dashboard_format(df, column_mapping)
        if not leads_data:
            print("❌ Nessun dato valido trovato")
            return False
        
        if test_mode:
            print(f"\n🧪 MODALITÀ TEST: Analisi completata")
            print(f"📊 Lead che verrebbero importati: {len(leads_data)}")
            
            # Mostra esempi
            print(f"\n📝 Esempi di lead:")
            for i, lead in enumerate(leads_data[:5]):
                print(f"   {i+1}. {lead['first_name']} {lead['last_name']} - {lead['email']} - {lead['phone']}")
            
            return True
        
        # Chiedi conferma
        print(f"\n⚠️  ATTENZIONE: Verranno importati {len(leads_data)} lead nel database.")
        try:
            confirm = input("Continuare? (s/n): ").lower().strip()
        except EOFError:
            print("❌ Input non disponibile. Usa --test per modalità test.")
            return False
        
        if confirm != 's':
            print("❌ Importazione annullata")
            return False
        
        # Importa nel database
        success_count, error_count = self.import_to_database(leads_data)
        
        # Crea report
        self.create_summary_report(leads_data, success_count, error_count)
        
        return success_count > 0

def main():
    """Funzione principale"""
    import sys
    
    importer = SpainLeadsImporter()
    
    # Percorso del file
    file_path = os.path.expanduser('~/Desktop/Spain-1.xlsx')
    
    if not os.path.exists(file_path):
        print(f"❌ File non trovato: {file_path}")
        return
    
    # Controlla se è modalità test
    test_mode = '--test' in sys.argv
    
    # Esegui importazione
    success = importer.run_import(file_path, test_mode=test_mode)
    
    if success:
        if test_mode:
            print(f"\n🧪 Test completato con successo!")
        else:
            print(f"\n🎉 Importazione completata con successo!")
    else:
        print(f"\n❌ Operazione fallita")

if __name__ == "__main__":
    main()
