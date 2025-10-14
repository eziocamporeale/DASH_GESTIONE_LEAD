#!/usr/bin/env python3
"""
Utility per la manutenzione dello storage
Include verifica e pulizia file orfani
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

def check_storage_files(silent=False):
    """Verifica tutti i file nello storage"""
    
    if not silent:
        print("🔍 VERIFICA FILES NELLO STORAGE")
        print("=" * 80)
    
    try:
        # Crea client Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Ottieni tutti i file attivi
        result = supabase.table('storage_files').select('*').eq('is_active', True).order('uploaded_at', desc=True).execute()
        
        if not result.data:
            if not silent:
                print("❌ Nessun file trovato nel database")
            return []
        
        if not silent:
            print(f"\n📊 Trovati {len(result.data)} file nel database\n")
        
        # Lista dei file mancanti
        missing_files = []
        existing_files = []
        
        for file in result.data:
            file_id = file.get('id')
            filename = file.get('original_filename')
            file_path = file.get('file_path')
            
            # Costruisci percorso completo
            if file_path:
                if not file_path.startswith('/'):
                    full_path = current_dir / file_path
                else:
                    full_path = Path(file_path)
                
                exists = full_path.exists()
                
                if not silent:
                    print(f"{'✅' if exists else '❌'} {filename} (ID: {file_id})")
                    if not exists:
                        print(f"   Path: {file_path}")
                        print()
                
                if exists:
                    existing_files.append(file)
                else:
                    missing_files.append(file)
        
        if not silent:
            print("=" * 80)
            print(f"✅ File esistenti: {len(existing_files)}")
            print(f"❌ File mancanti: {len(missing_files)}")
        
        return missing_files
    
    except Exception as e:
        if not silent:
            print(f"❌ Errore: {e}")
        return None


def clean_orphan_files(auto_confirm=False):
    """Elimina record di file orfani"""
    
    print("🧹 PULIZIA RECORD ORFANI")
    print("=" * 80)
    
    missing = check_storage_files(silent=True)
    
    if not missing:
        print("\n✅ Nessun file orfano trovato!")
        return 0
    
    print(f"\n🚨 Trovati {len(missing)} file orfani:\n")
    for file in missing:
        print(f"   - {file.get('original_filename')} (ID: {file.get('id')})")
    
    if not auto_confirm:
        print(f"\n⚠️  Questi record verranno contrassegnati come inattivi (soft delete)")
        confirm = input("Procedere? (s/N): ").strip().lower()
        
        if confirm != 's':
            print("❌ Operazione annullata")
            return 0
    
    # Elimina record orfani
    print(f"\n🧹 Pulizia in corso...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        deleted_count = 0
        
        for file in missing:
            try:
                supabase.table('storage_files').update({
                    'is_active': False
                }).eq('id', file.get('id')).execute()
                print(f"   ✅ Eliminato: {file.get('original_filename')}")
                deleted_count += 1
            except Exception as e:
                print(f"   ❌ Errore: {e}")
        
        print(f"\n✅ PULIZIA COMPLETATA!")
        print(f"   File orfani eliminati: {deleted_count}")
        
        return deleted_count
    
    except Exception as e:
        print(f"❌ Errore: {e}")
        return 0


def get_storage_stats():
    """Statistiche storage"""
    
    print("📊 STATISTICHE STORAGE")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # File attivi
        active = supabase.table('storage_files').select('*').eq('is_active', True).execute()
        # File inattivi
        inactive = supabase.table('storage_files').select('*').eq('is_active', False).execute()
        
        total_size = sum(f.get('file_size', 0) for f in active.data) if active.data else 0
        
        print(f"\n📁 File Attivi: {len(active.data) if active.data else 0}")
        print(f"🗑️  File Eliminati: {len(inactive.data) if inactive.data else 0}")
        print(f"💾 Spazio Usato: {total_size / 1024 / 1024:.2f} MB")
        
        if active.data:
            print(f"\n📂 Per Categoria:")
            categories = {}
            for f in active.data:
                cat = f.get('category', 'Altro')
                if cat not in categories:
                    categories[cat] = {'count': 0, 'size': 0}
                categories[cat]['count'] += 1
                categories[cat]['size'] += f.get('file_size', 0)
            
            for cat, stats in sorted(categories.items()):
                print(f"   {cat}: {stats['count']} file ({stats['size'] / 1024 / 1024:.2f} MB)")
        
        print()
    
    except Exception as e:
        print(f"❌ Errore: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manutenzione Storage')
    parser.add_argument('action', choices=['check', 'clean', 'stats'], help='Azione da eseguire')
    parser.add_argument('--auto', action='store_true', help='Auto-conferma (solo per clean)')
    
    args = parser.parse_args()
    
    if args.action == 'check':
        missing = check_storage_files()
        sys.exit(1 if missing and len(missing) > 0 else 0)
    
    elif args.action == 'clean':
        deleted = clean_orphan_files(auto_confirm=args.auto)
        sys.exit(0 if deleted >= 0 else 1)
    
    elif args.action == 'stats':
        get_storage_stats()
        sys.exit(0)

