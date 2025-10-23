#!/usr/bin/env python3
"""
📱 TELEGRAM INTEGRATION TEST - Dashboard Gestione Lead
Script per testare l'integrazione del sistema Telegram
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path
import logging

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_telegram_manager():
    """Testa il TelegramManager"""
    try:
        from components.telegram.telegram_manager import TelegramManager
        
        print("🧪 Testando TelegramManager...")
        
        # Inizializza il manager
        telegram_manager = TelegramManager()
        
        # Verifica stato
        status = telegram_manager.get_status()
        print(f"📊 Stato TelegramManager: {status}")
        
        if status['is_configured']:
            print("✅ TelegramManager configurato correttamente")
            
            # Test connessione
            success, message = telegram_manager.test_connection()
            if success:
                print(f"✅ Test connessione: {message}")
            else:
                print(f"❌ Test connessione fallito: {message}")
            
            # Test invio messaggio
            success, message = telegram_manager.send_message("🧪 **Test Integrazione Lead**\n\nTest del sistema Telegram nel Dashboard Lead!")
            if success:
                print(f"✅ Test invio messaggio: {message}")
            else:
                print(f"❌ Test invio messaggio fallito: {message}")
                
        else:
            print("⚠️ TelegramManager non configurato - configurazione richiesta")
            
        return True
        
    except Exception as e:
        print(f"❌ Errore test TelegramManager: {e}")
        return False

def test_telegram_settings_ui():
    """Testa l'interfaccia TelegramSettingsUI"""
    try:
        from components.telegram.telegram_settings_ui import TelegramSettingsUI
        
        print("🧪 Testando TelegramSettingsUI...")
        
        # Inizializza l'interfaccia
        telegram_ui = TelegramSettingsUI()
        
        print("✅ TelegramSettingsUI inizializzato correttamente")
        
        # Test caricamento impostazioni
        settings = telegram_ui._get_default_notification_settings()
        print(f"📊 Impostazioni default: {len(settings)} impostazioni")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test TelegramSettingsUI: {e}")
        return False

def test_database_tables():
    """Testa le tabelle del database Telegram"""
    try:
        from database.database_manager import DatabaseManager
        
        print("🧪 Testando tabelle database Telegram...")
        
        db = DatabaseManager()
        
        # Verifica tabelle
        tables_to_check = ['telegram_config', 'notification_settings', 'notification_logs']
        
        for table in tables_to_check:
            try:
                response = db.supabase.table(table).select('*').limit(1).execute()
                print(f"✅ Tabella {table} accessibile")
            except Exception as e:
                print(f"❌ Errore accesso tabella {table}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test database: {e}")
        return False

def test_lead_form_integration():
    """Testa l'integrazione nel LeadForm"""
    try:
        from components.leads.lead_form import LeadForm
        
        print("🧪 Testando integrazione LeadForm...")
        
        # Inizializza il form
        lead_form = LeadForm()
        
        # Verifica che TelegramManager sia inizializzato
        if hasattr(lead_form, 'telegram_manager') and lead_form.telegram_manager:
            print("✅ TelegramManager integrato nel LeadForm")
            
            # Test metodo notifica
            test_data = {
                'nome': 'Test Lead',
                'email': 'test@example.com',
                'telefono': '+39 123 456 789',
                'broker': 'Test Broker',
                'fonte': 'Website',
                'priority': 'Media',
                'note': 'Test di integrazione',
                'created_by': 'Test User'
            }
            
            lead_form._send_telegram_notification('new_lead', test_data)
            print("✅ Test invio notifica Lead completato")
            
        else:
            print("❌ TelegramManager non integrato nel LeadForm")
            
        return True
        
    except Exception as e:
        print(f"❌ Errore test integrazione LeadForm: {e}")
        return False

def main():
    """Esegue tutti i test"""
    print("🚀 Avvio test integrazione Telegram per Dashboard Lead...")
    print("=" * 60)
    
    tests = [
        ("Database Tables", test_database_tables),
        ("TelegramManager", test_telegram_manager),
        ("TelegramSettingsUI", test_telegram_settings_ui),
        ("LeadForm Integration", test_lead_form_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Eseguendo test: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} fallito con eccezione: {e}")
            results.append((test_name, False))
    
    # Riepilogo risultati
    print("\n" + "=" * 60)
    print("📊 RIEPILOGO RISULTATI TEST")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Risultato finale: {passed}/{total} test superati")
    
    if passed == total:
        print("🎉 Tutti i test sono stati superati! Sistema Telegram integrato correttamente.")
    else:
        print("⚠️ Alcuni test sono falliti. Controlla la configurazione.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
