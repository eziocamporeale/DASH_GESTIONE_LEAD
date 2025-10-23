#!/usr/bin/env python3
"""
📱 TELEGRAM COMPLETE TEST - Dashboard Gestione Lead
Test completo del sistema Telegram con setup automatico
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

def test_telegram_components():
    """Testa tutti i componenti Telegram"""
    print("🧪 Testando componenti Telegram...")
    
    try:
        # Test TelegramManager
        from components.telegram.telegram_manager import TelegramManager
        telegram_manager = TelegramManager()
        print("✅ TelegramManager importato correttamente")
        
        # Test TelegramSettingsUI
        from components.telegram.telegram_settings_ui import TelegramSettingsUI
        telegram_ui = TelegramSettingsUI()
        print("✅ TelegramSettingsUI importato correttamente")
        
        # Test integrazione LeadForm
        from components.leads.lead_form import LeadForm
        lead_form = LeadForm()
        if hasattr(lead_form, 'telegram_manager'):
            print("✅ TelegramManager integrato nel LeadForm")
        else:
            print("❌ TelegramManager NON integrato nel LeadForm")
            return False
        
        # Test metodo notifica
        if hasattr(lead_form, '_send_telegram_notification'):
            print("✅ Metodo _send_telegram_notification presente")
        else:
            print("❌ Metodo _send_telegram_notification mancante")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test componenti: {e}")
        return False

def test_settings_integration():
    """Testa l'integrazione nelle impostazioni"""
    print("🧪 Testando integrazione Settings...")
    
    try:
        from components.settings.settings_manager import SettingsManager
        settings_manager = SettingsManager()
        
        # Verifica che il metodo telegram sia presente
        if hasattr(settings_manager, 'render_telegram_settings'):
            print("✅ Metodo render_telegram_settings presente")
        else:
            print("❌ Metodo render_telegram_settings mancante")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test settings: {e}")
        return False

def test_file_structure():
    """Testa la struttura dei file"""
    print("🧪 Testando struttura file...")
    
    required_files = [
        'components/telegram/telegram_manager.py',
        'components/telegram/telegram_settings_ui.py',
        'components/telegram/__init__.py',
        'database/telegram_schema.sql',
        'database/init_telegram_tables.py',
        'setup_telegram_supabase.sql',
        'setup_telegram_supabase.py',
        'test_telegram_integration.py',
        'TELEGRAM_INTEGRATION_README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ File mancanti: {missing_files}")
        return False
    else:
        print("✅ Tutti i file richiesti presenti")
        return True

def test_syntax():
    """Testa la sintassi dei file Python"""
    print("🧪 Testando sintassi file Python...")
    
    python_files = [
        'components/telegram/telegram_manager.py',
        'components/telegram/telegram_settings_ui.py',
        'components/telegram/__init__.py',
        'database/init_telegram_tables.py',
        'setup_telegram_supabase.py',
        'test_telegram_integration.py'
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print(f"✅ {file_path} - Sintassi OK")
        except SyntaxError as e:
            print(f"❌ {file_path} - Errore sintassi: {e}")
            return False
        except Exception as e:
            print(f"⚠️ {file_path} - Errore: {e}")
    
    return True

def main():
    """Esegue tutti i test"""
    print("🚀 TEST COMPLETO SISTEMA TELEGRAM")
    print("=" * 50)
    
    tests = [
        ("Struttura File", test_file_structure),
        ("Sintassi Python", test_syntax),
        ("Componenti Telegram", test_telegram_components),
        ("Integrazione Settings", test_settings_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} fallito: {e}")
            results.append((test_name, False))
    
    # Riepilogo
    print("\n" + "=" * 50)
    print("📊 RIEPILOGO TEST")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Risultato: {passed}/{total} test superati")
    
    if passed == total:
        print("🎉 TUTTI I TEST SUPERATI!")
        print("\n📋 PROSSIMI PASSI:")
        print("1. Eseguire setup_telegram_supabase.sql in Supabase")
        print("2. Configurare bot Telegram nelle Impostazioni")
        print("3. Testare invio notifiche")
        print("4. Fare commit su Git")
    else:
        print("⚠️ Alcuni test falliti - controllare prima del commit")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
