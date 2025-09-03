#!/usr/bin/env python3
"""
Script per pulire manualmente i record di test dal database leads
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_leads_database():
    """Pulisce i record di test dal database leads"""
    
    print("🧹 PULIZIA DATABASE LEADS")
    print("=" * 50)
    
    try:
        # Inizializza connessione Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connessione Supabase stabilita")
        
        # Leggi tutti i record
        print("\n📖 Lettura record esistenti...")
        result = supabase.table('leads').select('*').execute()
        
        if not result.data:
            print("📭 Nessun record trovato nel database")
            return True
        
        print(f"📊 Trovati {len(result.data)} record")
        
        # Mostra i record
        print("\n📋 Record esistenti:")
        for i, lead in enumerate(result.data, 1):
            print(f"   {i}. ID: {lead['id']} - Nome: {lead.get('name', 'N/A')} - Email: {lead.get('email', 'N/A')}")
        
        # Chiedi conferma per eliminazione
        print(f"\n⚠️ ATTENZIONE: Stai per eliminare {len(result.data)} record")
        confirm = input("Sei sicuro di voler eliminare TUTTI i record? (scrivi 'ELIMINA TUTTO' per confermare): ")
        
        if confirm.upper() == 'ELIMINA TUTTO':
            print("\n🗑️ Eliminazione record in corso...")
            
            # Elimina tutti i record
            for lead in result.data:
                try:
                    supabase.table('leads').delete().eq('id', lead['id']).execute()
                    print(f"   ✅ Eliminato record ID: {lead['id']}")
                except Exception as e:
                    print(f"   ❌ Errore eliminazione record ID {lead['id']}: {e}")
            
            # Verifica eliminazione
            print("\n🔍 Verifica eliminazione...")
            verify_result = supabase.table('leads').select('*').execute()
            
            if not verify_result.data:
                print("✅ Database pulito con successo!")
            else:
                print(f"⚠️ Rimangono ancora {len(verify_result.data)} record")
                
        else:
            print("❌ Operazione annullata")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        logger.error(f"Errore pulizia database: {e}")
        return False

if __name__ == "__main__":
    print("⚠️ ATTENZIONE: Questo script eliminerà TUTTI i record dalla tabella leads")
    
    confirm = input("\nSei sicuro di voler procedere? (scrivi 'SI' per confermare): ")
    
    if confirm.upper() == 'SI':
        clean_leads_database()
    else:
        print("❌ Operazione annullata")
