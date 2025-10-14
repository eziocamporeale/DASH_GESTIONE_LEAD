#!/usr/bin/env python3
"""
Script per verificare la sicurezza di tutti gli utenti
Controlla che solo gli utenti autorizzati abbiano permessi admin
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager

def verify_users_security():
    """Verifica la sicurezza di tutti gli utenti"""
    
    print("🔒 VERIFICA SICUREZZA UTENTI")
    print("=" * 70)
    
    # Inizializza il database manager
    db = DatabaseManager()
    
    try:
        # Ottieni tutti gli utenti
        users = db.get_all_users()
        
        if not users:
            print("❌ Nessun utente trovato!")
            return
        
        print(f"\n📊 Trovati {len(users)} utenti\n")
        
        # Lista degli utenti che DOVREBBERO essere admin (da verificare manualmente)
        legitimate_admins = ['admin']  # Username degli admin legittimi
        
        # Contatori
        total_admins = 0
        suspicious_admins = []
        empty_users = []
        inactive_users = []
        
        print("🔍 ANALISI UTENTI:")
        print("-" * 70)
        
        for user in users:
            username = user.get('username', '').strip()
            email = user.get('email', '').strip()
            role_name = user.get('role_name', 'N/A')
            role_id = user.get('role_id')
            is_active = user.get('is_active', True)
            user_id = user.get('id')
            
            # Controlla utenti admin
            if role_id == 1 or role_name == 'Admin':
                total_admins += 1
                status = "✅ LEGITTIMO" if username in legitimate_admins else "🚨 SOSPETTO"
                
                print(f"\n👤 ADMIN TROVATO: {username if username else f'ID:{user_id}'}")
                print(f"   📧 Email: {email if email else 'VUOTA'}")
                print(f"   🆔 ID: {user_id}")
                print(f"   🔑 Role ID: {role_id}")
                print(f"   🏷️ Role Name: {role_name}")
                print(f"   ✅ Attivo: {is_active}")
                print(f"   🔍 Stato: {status}")
                
                if username not in legitimate_admins:
                    suspicious_admins.append({
                        'id': user_id,
                        'username': username if username else f'ID:{user_id}',
                        'email': email,
                        'role_id': role_id
                    })
            
            # Controlla utenti con dati vuoti
            if not username or not email:
                empty_users.append({
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'role_name': role_name
                })
            
            # Controlla utenti inattivi
            if not is_active:
                inactive_users.append({
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'role_name': role_name
                })
        
        # Report finale
        print("\n" + "=" * 70)
        print("📋 REPORT SICUREZZA")
        print("=" * 70)
        
        print(f"\n✅ Totale utenti: {len(users)}")
        print(f"🔑 Totale admin: {total_admins}")
        
        if suspicious_admins:
            print(f"\n🚨 ADMIN SOSPETTI TROVATI: {len(suspicious_admins)}")
            print("\nUtenti con permessi admin che potrebbero non essere autorizzati:")
            for admin in suspicious_admins:
                print(f"   - {admin['username']} (ID: {admin['id']}, Email: {admin['email']})")
            
            print("\n⚠️  RACCOMANDAZIONE:")
            print("   Verifica manualmente questi utenti e rimuovi i permessi admin se non autorizzati.")
            print("   Usa lo script fix_user_role.py per correggere i permessi.")
        else:
            print(f"\n✅ Nessun admin sospetto trovato!")
        
        if empty_users:
            print(f"\n⚠️  UTENTI CON DATI VUOTI: {len(empty_users)}")
            print("\nUtenti con username o email vuoti:")
            for user in empty_users:
                print(f"   - ID: {user['id']}, Username: '{user['username']}', Email: '{user['email']}', Ruolo: {user['role_name']}")
            
            print("\n⚠️  RACCOMANDAZIONE:")
            print("   Controlla questi utenti e aggiorna i loro dati o eliminali se non più necessari.")
        
        if inactive_users:
            print(f"\n📛 UTENTI INATTIVI: {len(inactive_users)}")
            print("\nUtenti disattivati:")
            for user in inactive_users:
                print(f"   - {user['username']} (ID: {user['id']}, Ruolo: {user['role_name']})")
        
        print("\n" + "=" * 70)
        
        # Determina se ci sono problemi
        has_issues = len(suspicious_admins) > 0 or len(empty_users) > 0
        
        if has_issues:
            print("⚠️  ATTENZIONE: Sono stati trovati problemi di sicurezza!")
            return False
        else:
            print("✅ Sistema sicuro - Nessun problema rilevato!")
            return True
    
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    is_secure = verify_users_security()
    
    if not is_secure:
        print(f"\n💡 PROSSIMI PASSI:")
        print(f"   1. Verificare manualmente gli utenti sospetti")
        print(f"   2. Rimuovere permessi admin non autorizzati")
        print(f"   3. Aggiornare o eliminare utenti con dati vuoti")
        sys.exit(1)
    else:
        sys.exit(0)

