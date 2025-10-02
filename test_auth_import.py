#!/usr/bin/env python3
"""
Test per verificare l'import di auth_manager
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def test_auth_import():
    """Testa l'import di auth_manager"""
    
    print("🧪 TEST IMPORT AUTH_MANAGER")
    print("=" * 50)
    
    try:
        # Test 1: Import della classe
        print("1️⃣ Test import classe AuthManager...")
        from components.auth.auth_manager import AuthManager
        print("✅ Classe AuthManager importata")
        
        # Test 2: Creazione istanza
        print("2️⃣ Test creazione istanza...")
        auth = AuthManager()
        print("✅ Istanza AuthManager creata")
        
        # Test 3: Import dell'istanza globale
        print("3️⃣ Test import istanza auth_manager...")
        from components.auth.auth_manager import auth_manager
        print("✅ Istanza auth_manager importata")
        print(f"   Tipo: {type(auth_manager)}")
        
        # Test 4: Import delle funzioni
        print("4️⃣ Test import funzioni...")
        from components.auth.auth_manager import require_auth, get_current_user
        print("✅ Funzioni importate")
        
        print("\n🎉 TUTTI I TEST SUPERATI!")
        return True
        
    except ImportError as e:
        print(f"❌ Errore di import: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore generico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_auth_import()
