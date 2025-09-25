#!/usr/bin/env python3
"""
Script intelligente per importare lead spagnoli da Spain-1.xlsx
Evita duplicati controllando email già esistenti
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

class SmartSpainLeadsImporter:
    """Importatore intelligente per lead spagnoli"""
    
    def __init__(self):
        self.db = DatabaseManager()
        
    def get_existing_emails(self):
        """Ottiene tutte le email già presenti nel database"""
        print("🔍 Controllo email esistenti nel database...")
        
        leads = self.db.get_leads(limit=10000)
        existing_emails = set()
        
        for lead in leads:
            email = lead.get('email')
            if email:
                existing_emails.add(email.lower().strip())
        
        print(f"📊 Email esistenti trovate: {len(existing_emails)}")
        return existing_emails
    
    def clean_phone_number(self, phone):
        """Pulisce e formatta il numero di telefono"""
        if pd.isna(phone) or phone == '':
            return None
            
        phone_str = str(phone).strip()
        phone_clean = re.sub(r'[^\d+]', '', phone_str)
        
        if phone_clean.startswith('+34'):
            return phone_clean
        if phone_clean.startswith('34'):
            return '+' + phone_clean
        if phone_clean.startswith(('6', '7')) and len(phone_clean) == 9:
            return '+34' + phone_clean
        if len(phone_clean) == 9 and phone_clean.startswith(('6', '7', '8', '9')):
            return '+34' + phone_clean
            
        return phone_clean
    
    def clean_email(self, email):
        """Pulisce l'email"""
        if pd.isna(email) or email == '':
            return None
            
        email_str = str(email).strip().lower()
        if '@' in email_str and '.' in email_str:
            return email_str
        return None
    
    def import_new_leads_only(self, file_path: str, batch_size: int = 100):
        """Importa solo i lead nuovi (evita duplicati)"""
        print(f"🚀 IMPORT INTELLIGENTE LEAD SPAGNOLI")
        print(f"=" * 50)
        
        # Ottieni email esistenti
        existing_emails = self.get_existing_emails()
        
        # Leggi il file Excel
        df = pd.read_excel(file_path)
        print(f"📊 File letto: {len(df)} righe")
        
        # Filtra solo i lead nuovi
        new_leads = []
        skipped_count = 0
        
        for index, row in df.iterrows():
            # Salta righe vuote
            if pd.isna(row.iloc[0]) and pd.isna(row.iloc[1]):
                continue
                
            email = self.clean_email(row.iloc[0])
            
            # Salta se email già esistente
            if email and email in existing_emails:
                skipped_count += 1
                continue
                
            # Estrai dati
            name = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
            surname = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ''
            country = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ''
            phone = self.clean_phone_number(row.iloc[5])
            
            # Salta se non abbiamo almeno email o nome
            if not email and not name:
                continue
                
            # Crea il record
            lead_data = {
                'first_name': name,
                'last_name': surname,
                'email': email,
                'phone': phone,
                'company': '',
                'position': '',
                'notes': f'Importato da Spain-1.xlsx - Paese: {country}',
                'lead_category_id': 1,
                'lead_state_id': 1,
                'lead_priority_id': 2,
                'lead_source_id': 1,
                'assigned_to': None,
                'group_id': None,
                'created_by': 1
            }
            
            new_leads.append(lead_data)
        
        print(f"📊 Lead da importare: {len(new_leads)}")
        print(f"⏭️  Lead saltati (duplicati): {skipped_count}")
        
        if not new_leads:
            print("✅ Nessun nuovo lead da importare!")
            return True
        
        # Importa in batch
        success_count = 0
        error_count = 0
        
        for i in range(0, len(new_leads), batch_size):
            batch = new_leads[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(new_leads) - 1) // batch_size + 1
            
            print(f"📥 Importando batch {batch_num}/{total_batches} ({len(batch)} lead)...")
            
            for lead_data in batch:
                try:
                    success = self.db.create_lead(lead_data)
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"     ❌ Errore: {e}")
        
        # Report finale
        print(f"\n📊 RISULTATI FINALI:")
        print(f"   ✅ Lead importati: {success_count}")
        print(f"   ❌ Errori: {error_count}")
        print(f"   ⏭️  Duplicati saltati: {skipped_count}")
        print(f"   📈 Tasso successo: {(success_count/(success_count+error_count)*100):.1f}%")
        
        return success_count > 0

def main():
    """Funzione principale"""
    importer = SmartSpainLeadsImporter()
    
    file_path = os.path.expanduser('~/Desktop/Spain-1.xlsx')
    
    if not os.path.exists(file_path):
        print(f"❌ File non trovato: {file_path}")
        return
    
    # Importa solo i lead nuovi
    success = importer.import_new_leads_only(file_path)
    
    if success:
        print(f"\n🎉 Importazione intelligente completata!")
    else:
        print(f"\n❌ Importazione fallita")

if __name__ == "__main__":
    main()

