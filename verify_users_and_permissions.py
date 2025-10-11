#!/usr/bin/env python3
"""
Script completo per verificare utenti e privilegi in Supabase
Dashboard Gestione Lead - Ezio Camporeale
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import SUPABASE_URL, SUPABASE_KEY, USER_ROLES
from supabase import create_client, Client

def verify_users_and_permissions():
    """Verifica completa degli utenti e dei loro privilegi"""
    
    print("🔍 VERIFICA COMPLETA UTENTI E PRIVILEGI")
    print("=" * 60)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Supabase URL: {SUPABASE_URL}")
    print("=" * 60)
    
    try:
        # Crea client Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 1. Ottieni tutti gli utenti
        print("\n📋 1. RECUPERO UTENTI...")
        users_result = supabase.table('users').select('*').execute()
        users = users_result.data
        
        if not users:
            print("❌ Nessun utente trovato")
            return
        
        print(f"✅ Trovati {len(users)} utenti")
        
        # 2. Ottieni tutti i ruoli
        print("\n🔑 2. RECUPERO RUOLI...")
        roles_result = supabase.table('roles').select('*').execute()
        roles_data = roles_result.data
        
        # Crea mappa ruoli per lookup veloce
        roles_map = {role['id']: role for role in roles_data}
        print(f"✅ Trovati {len(roles_data)} ruoli")
        
        # 3. Ottieni tutti i dipartimenti
        print("\n🏢 3. RECUPERO DIPARTIMENTI...")
        dept_result = supabase.table('departments').select('*').execute()
        departments_data = dept_result.data
        
        # Crea mappa dipartimenti per lookup veloce
        dept_map = {dept['id']: dept for dept in departments_data}
        print(f"✅ Trovati {len(departments_data)} dipartimenti")
        
        # 4. Analisi dettagliata utenti
        print("\n" + "=" * 60)
        print("👥 ANALISI DETTAGLIATA UTENTI")
        print("=" * 60)
        
        admin_users = []
        active_users = []
        inactive_users = []
        
        for user in users:
            # Informazioni base
            user_id = user.get('id', 'N/A')
            username = user.get('username', 'N/A')
            email = user.get('email', 'N/A')
            first_name = user.get('first_name', 'N/A')
            last_name = user.get('last_name', 'N/A')
            phone = user.get('phone', 'N/A')
            role_id = user.get('role_id', 'N/A')
            is_active = user.get('is_active', False)
            is_admin = user.get('is_admin', False)
            department_id = user.get('department_id', 'N/A')
            last_login = user.get('last_login', 'N/A')
            created_at = user.get('created_at', 'N/A')
            
            # Informazioni ruolo
            role_info = roles_map.get(role_id, {})
            role_name = role_info.get('name', 'N/A')
            
            # Informazioni dipartimento
            dept_info = dept_map.get(department_id, {})
            dept_name = dept_info.get('name', 'N/A')
            
            print(f"\n👤 UTENTE: {username}")
            print(f"   🆔 ID: {user_id}")
            print(f"   📧 Email: {email}")
            print(f"   👨‍💼 Nome: {first_name} {last_name}")
            print(f"   📱 Telefono: {phone}")
            print(f"   🔑 Ruolo ID: {role_id}")
            print(f"   🏷️ Ruolo Nome: {role_name}")
            print(f"   🏢 Dipartimento: {dept_name} (ID: {department_id})")
            print(f"   ✅ Attivo: {is_active}")
            print(f"   👑 Admin: {is_admin}")
            print(f"   🕒 Ultimo Login: {last_login}")
            print(f"   📅 Creato: {created_at}")
            
            # Classifica utenti
            if is_admin or role_name == 'Admin':
                admin_users.append(user)
                print(f"   🚨 ⚠️  UTENTE CON PRIVILEGI ADMIN!")
            elif is_active:
                active_users.append(user)
                print(f"   ✅ Utente normale attivo")
            else:
                inactive_users.append(user)
                print(f"   ❌ Utente inattivo")
        
        # 5. Report di sicurezza
        print("\n" + "=" * 60)
        print("🛡️ REPORT SICUREZZA")
        print("=" * 60)
        
        print(f"\n📊 STATISTICHE:")
        print(f"   👥 Totale utenti: {len(users)}")
        print(f"   👑 Utenti Admin: {len(admin_users)}")
        print(f"   ✅ Utenti attivi: {len(active_users)}")
        print(f"   ❌ Utenti inattivi: {len(inactive_users)}")
        
        print(f"\n🚨 UTENTI CON PRIVILEGI ADMIN:")
        if admin_users:
            for admin in admin_users:
                print(f"   - {admin.get('username', 'N/A')} ({admin.get('email', 'N/A')})")
                print(f"     Role ID: {admin.get('role_id', 'N/A')}")
                print(f"     Admin Flag: {admin.get('is_admin', False)}")
        else:
            print("   ✅ Nessun utente admin trovato")
        
        # 6. Analisi ruoli e permessi
        print(f"\n🔑 RUOLI DISPONIBILI:")
        for role in roles_data:
            role_id = role.get('id', 'N/A')
            role_name = role.get('name', 'N/A')
            role_desc = role.get('description', 'N/A')
            print(f"   ID {role_id}: {role_name} - {role_desc}")
        
        # 7. Analisi dipartimenti
        print(f"\n🏢 DIPARTIMENTI:")
        for dept in departments_data:
            dept_id = dept.get('id', 'N/A')
            dept_name = dept.get('name', 'N/A')
            dept_desc = dept.get('description', 'N/A')
            print(f"   ID {dept_id}: {dept_name} - {dept_desc}")
        
        # 8. Raccomandazioni di sicurezza
        print(f"\n" + "=" * 60)
        print("💡 RACCOMANDAZIONI SICUREZZA")
        print("=" * 60)
        
        if len(admin_users) > 2:
            print("⚠️ ATTENZIONE: Troppi utenti admin!")
            print("   Raccomandazione: Ridurre il numero di admin a massimo 2")
        
        # Verifica utenti con dati mancanti
        users_with_missing_data = []
        for user in users:
            if not user.get('email') or not user.get('first_name') or not user.get('last_name'):
                users_with_missing_data.append(user)
        
        if users_with_missing_data:
            print("⚠️ ATTENZIONE: Utenti con dati mancanti:")
            for user in users_with_missing_data:
                print(f"   - {user.get('username', 'N/A')}: email={bool(user.get('email'))}, nome={bool(user.get('first_name'))}")
        
        # Verifica utenti inattivi
        if inactive_users:
            print(f"⚠️ ATTENZIONE: {len(inactive_users)} utenti inattivi")
            print("   Raccomandazione: Disattivare o eliminare utenti non utilizzati")
        
        # 9. Salva report in file
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_users': len(users),
            'admin_users': len(admin_users),
            'active_users': len(active_users),
            'inactive_users': len(inactive_users),
            'admin_details': [
                {
                    'username': admin.get('username'),
                    'email': admin.get('email'),
                    'role_id': admin.get('role_id'),
                    'is_admin': admin.get('is_admin')
                } for admin in admin_users
            ],
            'roles': roles_data,
            'departments': departments_data
        }
        
        report_file = Path("user_security_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Report salvato in: {report_file}")
        print("\n✅ Verifica completata!")
        
    except Exception as e:
        print(f"❌ Errore durante la verifica: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_users_and_permissions()






