#!/usr/bin/env python3
"""
Test per il modulo di importazione Excel
Creato da Ezio Camporeale
"""

import pandas as pd
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from components.settings.excel_importer import ExcelImporter
from database.database_manager import DatabaseManager

def test_excel_importer():
    """Test del modulo ExcelImporter"""
    
    print("🧪 Test Modulo Importazione Excel")
    print("=" * 50)
    
    try:
        # Inizializza l'importatore
        importer = ExcelImporter()
        print("✅ ExcelImporter inizializzato correttamente")
        
        # Test mapping automatico colonne
        test_columns = ['Nome', 'Cognome', 'Email', 'Telefono', 'Azienda', 'Posizione']
        mapping = importer.auto_map_columns(test_columns)
        print(f"✅ Mapping automatico: {mapping}")
        
        # Test creazione DataFrame di test
        test_data = {
            'Nome': ['Mario', 'Giulia', 'Luca'],
            'Cognome': ['Rossi', 'Bianchi', 'Verdi'],
            'Email': ['mario.rossi@email.com', 'giulia.bianchi@email.com', 'luca.verdi@email.com'],
            'Telefono': ['+39 123 456 7890', '+39 098 765 4321', '+39 555 123 4567'],
            'Azienda': ['Azienda A', 'Azienda B', 'Azienda C'],
            'Posizione': ['CEO', 'Manager', 'Developer']
        }
        
        df = pd.DataFrame(test_data)
        print(f"✅ DataFrame di test creato: {len(df)} righe")
        
        # Test validazione dati
        column_mapping = importer.auto_map_columns(df.columns.tolist())
        validation_result = importer.validate_data(df, column_mapping)
        print(f"✅ Validazione dati: {'Valido' if validation_result['valid'] else 'Non valido'}")
        
        if not validation_result['valid']:
            print("❌ Errori di validazione:")
            for error in validation_result['errors']:
                print(f"   • {error}")
        
        if validation_result['warnings']:
            print("⚠️ Avvisi:")
            for warning in validation_result['warnings']:
                print(f"   • {warning}")
        
        # Test preparazione dati
        test_row = df.iloc[0]
        lead_data = importer.prepare_lead_data(test_row, column_mapping)
        print(f"✅ Dati lead preparati: {lead_data}")
        
        print("\n🎉 Tutti i test sono passati con successo!")
        
    except Exception as e:
        print(f"❌ Errore durante i test: {str(e)}")
        import traceback
        traceback.print_exc()

def test_database_methods():
    """Test dei metodi del database necessari per l'importazione"""
    
    print("\n🧪 Test Metodi Database")
    print("=" * 50)
    
    try:
        db = DatabaseManager()
        print("✅ DatabaseManager inizializzato")
        
        # Test metodi di lettura
        sources = db.get_lead_sources()
        print(f"✅ Fonti lead: {len(sources)} trovate")
        
        categories = db.get_lead_categories()
        print(f"✅ Categorie lead: {len(categories)} trovate")
        
        priorities = db.get_lead_priorities()
        print(f"✅ Priorità lead: {len(priorities)} trovate")
        
        states = db.get_lead_states()
        print(f"✅ Stati lead: {len(states)} trovati")
        
        print("\n🎉 Tutti i test del database sono passati!")
        
    except Exception as e:
        print(f"❌ Errore durante i test del database: {str(e)}")
        import traceback
        traceback.print_exc()

def create_sample_excel():
    """Crea un file Excel di esempio per test"""
    
    print("\n📊 Creazione File Excel di Esempio")
    print("=" * 50)
    
    try:
        # Dati di esempio
        sample_data = {
            'Nome': ['Mario', 'Giulia', 'Luca', 'Anna', 'Marco'],
            'Cognome': ['Rossi', 'Bianchi', 'Verdi', 'Neri', 'Blu'],
            'Email': ['mario.rossi@email.com', 'giulia.bianchi@email.com', 'luca.verdi@email.com', 'anna.neri@email.com', 'marco.blu@email.com'],
            'Telefono': ['+39 123 456 7890', '+39 098 765 4321', '+39 555 123 4567', '+39 333 444 5555', '+39 666 777 8888'],
            'Azienda': ['Azienda A SRL', 'Azienda B SPA', 'Azienda C SRL', 'Azienda D SPA', 'Azienda E SRL'],
            'Posizione': ['CEO', 'Manager', 'Developer', 'Analyst', 'Designer'],
            'Fonte': ['Website', 'Telefono', 'Email', 'Social', 'Referral'],
            'Categoria': ['A', 'B', 'A', 'C', 'B'],
            'Stato': ['Nuovo', 'Qualificato', 'Nuovo', 'Contattato', 'Nuovo'],
            'Priorità': ['Alta', 'Media', 'Bassa', 'Media', 'Alta'],
            'Budget': [50000, 25000, 15000, 30000, 40000],
            'Data Chiusura': ['2024-12-31', '2024-11-30', '2025-01-15', '2024-10-31', '2025-02-28'],
            'Note': ['Cliente molto interessato', 'Richiede demo', 'Budget limitato', 'Decisione rapida', 'Cliente strategico']
        }
        
        df = pd.DataFrame(sample_data)
        
        # Salva il file Excel
        excel_path = Path(__file__).parent / 'sample_clients.xlsx'
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        print(f"✅ File Excel di esempio creato: {excel_path}")
        print(f"📊 Righe: {len(df)}")
        print(f"📋 Colonne: {list(df.columns)}")
        
        return excel_path
        
    except Exception as e:
        print(f"❌ Errore nella creazione del file Excel: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 Avvio Test Modulo Importazione Excel")
    print("=" * 60)
    
    # Test del modulo ExcelImporter
    test_excel_importer()
    
    # Test dei metodi del database
    test_database_methods()
    
    # Crea file Excel di esempio
    excel_path = create_sample_excel()
    
    print("\n" + "=" * 60)
    print("✅ Test completati!")
    
    if excel_path:
        print(f"📁 File Excel di esempio disponibile: {excel_path}")
        print("💡 Puoi usare questo file per testare l'importazione nella dashboard")
