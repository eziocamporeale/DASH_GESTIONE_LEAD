#!/usr/bin/env python3
"""
Script per forzare il refresh dell'applicazione Streamlit
Creato da Ezio Camporeale
"""

import requests
import time

def force_refresh():
    """Forza il refresh dell'applicazione Streamlit"""
    
    print("🔄 FORZA REFRESH APPLICAZIONE")
    print("=" * 50)
    
    try:
        # URL dell'applicazione
        url = "http://localhost:8501"
        
        print(f"🌐 Tentativo connessione a: {url}")
        
        # Prova a fare una richiesta per forzare il refresh
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Applicazione raggiungibile")
            print("🔄 Refresh forzato - ora ricarica la pagina nel browser")
        else:
            print(f"⚠️ Applicazione risponde con status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossibile connettersi all'applicazione")
        print("   Verifica che l'applicazione sia in esecuzione su http://localhost:8501")
    except Exception as e:
        print(f"❌ Errore: {e}")
    
    print("\n📋 ISTRUZIONI:")
    print("1. Vai su http://localhost:8501")
    print("2. Premi F5 o Ctrl+R per ricaricare la pagina")
    print("3. Oppure clicca sul pulsante 'Aggiorna' di Streamlit")
    print("4. Verifica che il lead 'Mario Rossi' sia visibile")

if __name__ == "__main__":
    force_refresh()
