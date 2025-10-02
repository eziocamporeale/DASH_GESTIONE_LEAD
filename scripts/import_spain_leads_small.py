#!/usr/bin/env python3
"""
Script per importare un piccolo batch di lead spagnoli da Spain-1.xlsx
Versione di test con solo 10 lead
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

class SpainLeadsSmallImporter:
    """Importatore per un piccolo batch di lead spagnoli"""
    
    def __init__(self):
        self.db = DatabaseManager()
        
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
    
    def import_small_batch(self, file_path: str, num_leads: int = 10):
        """Importa un piccolo batch di lead per test"""
        print(f"🧪 IMPORT BATTERIA PICCOLA - {num_leads} LEAD")
        print(f"=" * 50)
        
        try:
            df = pd.read_excel(file_path)
            print(f"📊 File letto: {len(df)} righe")
            
            success_count = 0
            error_count = 0
            
            for i in range(min(num_leads, len(df))):
                row = df.iloc[i]
                
                # Salta righe vuote
                if pd.isna(row.iloc[0]) and pd.isna(row.iloc[1]):
                    continue
                
                # Estrai dati
                email = self.clean_email(row.iloc[0])
                name = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
                surname = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ''
                country = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ''
                phone = self.clean_phone_number(row.iloc[5])
                
                if not email and not name:
                    continue
                
                # Crea lead data
                lead_data = {
                    'first_name': name,
                    'last_name': surname,
                    'email': email,
                    'phone': phone,
                    'company': '',
                    'position': '',
                    'notes': f'Importato da Spain-1.xlsx (test) - Paese: {country}',
                    'lead_category_id': 1,
                    'lead_state_id': 1,
                    'lead_priority_id': 2,
                    'lead_source_id': 1,
                    'assigned_to': None,
                    'group_id': None,
                    'created_by': 1
                }
                
                print(f"📝 Importando: {name} {surname} - {email}")
                
                try:
                    success = self.db.create_lead(lead_data)
                    if success:
                        success_count += 1
                        print(f"   ✅ Successo")
                    else:
                        error_count += 1
                        print(f"   ❌ Errore")
                except Exception as e:
                    error_count += 1
                    print(f"   ❌ Errore: {e}")
            
            print(f"\n📊 RISULTATI:")
            print(f"   ✅ Successi: {success_count}")
            print(f"   ❌ Errori: {error_count}")
            print(f"   📈 Tasso successo: {(success_count/(success_count+error_count)*100):.1f}%")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Errore generale: {e}")
            return False

def main():
    """Funzione principale"""
    importer = SpainLeadsSmallImporter()
    
    file_path = os.path.expanduser('~/Desktop/Spain-1.xlsx')
    
    if not os.path.exists(file_path):
        print(f"❌ File non trovato: {file_path}")
        return
    
    # Importa 10 lead di test
    success = importer.import_small_batch(file_path, num_leads=10)
    
    if success:
        print(f"\n🎉 Test importazione completato!")
    else:
        print(f"\n❌ Test importazione fallito")

if __name__ == "__main__":
    main()





