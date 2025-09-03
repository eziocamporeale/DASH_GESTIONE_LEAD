#!/usr/bin/env python3
"""
Script per eliminare forzatamente tutti i record leads
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

def force_clean_leads():
    """Elimina forzatamente tutti i record leads"""
    
    print("🧹 ELIMINAZIONE FORZATA RECORD LEADS")
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
        
        print(f"📊 Trovati {len(result.data)} record da eliminare")
        
        # Elimina tutti i record
        print("\n🗑️ Eliminazione record in corso...")
        
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
        
        return True
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        return False

if __name__ == "__main__":
    force_clean_leads()
