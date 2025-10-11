#!/usr/bin/env python3
"""
Componente User Management per DASH_GESTIONE_LEAD
Gestione utenti con tabella e azioni
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
import sys
from pathlib import Path
from datetime import datetime

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import get_current_user
from config import CUSTOM_COLORS

class UserManagement:
    """Gestisce la gestione degli utenti"""
    
    def __init__(self):
        """Inizializza la gestione utenti"""
        self.db = DatabaseManager()
        self.current_user = get_current_user()
    
    def render_user_filters(self) -> Dict:
        """Renderizza i filtri per gli utenti"""
        
        st.markdown("### 🔍 Filtri Utenti")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Filtro ruolo
            roles = self.db.get_roles()
            role_options = ["Tutti"] + [role['name'] for role in roles]
            selected_role = st.selectbox(
                "Ruolo",
                options=role_options,
                index=0
            )
        
        with col2:
            # Filtro dipartimento
            departments = self.db.get_departments()
            dept_options = ["Tutti"] + [dept['name'] for dept in departments]
            selected_department = st.selectbox(
                "Dipartimento",
                options=dept_options,
                index=0
            )
        
        with col3:
            # Filtro stato
            status_options = ["Tutti", "Attivi", "Inattivi"]
            selected_status = st.selectbox(
                "Stato",
                options=status_options,
                index=0
            )
        
        with col4:
            # Ricerca testuale
            search_term = st.text_input(
                "🔍 Ricerca",
                placeholder="Nome, email, username...",
                help="Cerca per nome, email o username"
            )
        
        # Preparazione filtri
        filters = {}
        
        if selected_role != "Tutti":
            role_id = next((role['id'] for role in roles if role['name'] == selected_role), None)
            if role_id:
                filters['role_id'] = role_id
        
        if selected_department != "Tutti":
            dept_id = next((dept['id'] for dept in departments if dept['name'] == selected_department), None)
            if dept_id:
                filters['department_id'] = dept_id
        
        if selected_status == "Attivi":
            filters['is_active'] = True
        elif selected_status == "Inattivi":
            filters['is_active'] = False
        
        if search_term:
            filters['search'] = search_term
        
        return filters
    
    def render_user_table(self, filters: Dict = None):
        """Renderizza la tabella degli utenti"""
        
        # Ottieni gli utenti
        users = self.db.get_users(filters=filters) if filters else self.db.get_all_users()
        
        # Applica filtraggio per ruolo Tester
        current_user = get_current_user()
        if current_user and current_user.get('role_name') == 'Tester':
            users = self.db.filter_sensitive_data_for_tester(users, 'user')
            st.info("🔒 **Modalità Tester**: I dati sensibili degli utenti sono stati mascherati per proteggere la privacy")
        
        if not users:
            st.info("📭 Nessun utente trovato")
            return
        
        # Converti in DataFrame
        df = pd.DataFrame(users)
        
        # Prepara le colonne per la visualizzazione
        if not df.empty:
            # Formatta le date (gestisce formato ISO8601 da Supabase)
            if 'created_at' in df.columns:
                try:
                    df['created_at'] = pd.to_datetime(df['created_at'], format='mixed').dt.strftime('%d/%m/%Y')
                except:
                    df['created_at'] = 'Data non disponibile'
            
            if 'last_login' in df.columns:
                try:
                    df['last_login'] = pd.to_datetime(df['last_login'], format='mixed').dt.strftime('%d/%m/%Y %H:%M')
                    df['last_login'] = df['last_login'].fillna('-')
                except:
                    df['last_login'] = '-'
            
            # Combina nome completo
            df['Nome Completo'] = df.apply(
                lambda row: f"{row['first_name']} {row['last_name']}", 
                axis=1
            )
            
            # Formatta stato
            df['Stato'] = df['is_active'].apply(lambda x: "✅ Attivo" if x else "❌ Inattivo")
            
            # Formatta admin
            df['Admin'] = df['is_admin'].apply(lambda x: "👑 Sì" if x else "👤 No")
        
        # Mostra la tabella
        st.markdown("### 📊 Lista Utenti")
        
        if not df.empty:
            # Seleziona solo le colonne da mostrare
            display_columns = [
                'Nome Completo', 'email', 'username', 'role_name', 
                'department_name', 'phone', 'Stato', 'Admin', 'created_at'
            ]
            
            # Filtra le colonne disponibili
            available_columns = [col for col in display_columns if col in df.columns]
            display_df = df[available_columns]
            
            # Rinomina le colonne
            column_mapping = {
                'Nome Completo': '👤 Nome Completo',
                'email': '📧 Email',
                'username': '🔑 Username',
                'role_name': '🏢 Ruolo',
                'department_name': '📋 Dipartimento',
                'phone': '📞 Telefono',
                'Stato': '📈 Stato',
                'Admin': '👑 Admin',
                'created_at': '📅 Creato'
            }
            
            display_df = display_df.rename(columns=column_mapping)
            
            # Mostra la tabella con azioni
            self.render_interactive_user_table(display_df, df)
    
    def render_interactive_user_table(self, display_df, original_df):
        """Renderizza una tabella interattiva con pulsanti per ogni utente"""
        
        # Crea una tabella con Streamlit
        for index, row in display_df.iterrows():
            # Ottieni i dati originali per questo utente
            original_row = original_df.iloc[index]
            user_id = original_row['id']
            
            # Crea un container per ogni riga utente
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                
                with col1:
                    st.write(f"**{row['👤 Nome Completo']}**")
                    st.write(f"📧 {row['📧 Email']}")
                    st.write(f"🔑 {row['🔑 Username']}")
                
                with col2:
                    st.write(f"🏢 {row['🏢 Ruolo']}")
                    st.write(f"📋 {row['📋 Dipartimento']}")
                
                with col3:
                    st.write(f"📞 {row['📞 Telefono']}")
                    st.write(f"📈 {row['📈 Stato']}")
                
                with col4:
                    st.write(f"👑 {row['👑 Admin']}")
                    st.write(f"📅 {row['📅 Creato']}")
                
                with col5:
                    # Pulsanti azioni
                    if st.button("✏️", key=f"edit_{user_id}", help="Modifica utente"):
                        st.session_state['show_user_form'] = True
                        st.session_state['user_form_mode'] = 'edit'
                        st.session_state['edit_user_data'] = original_row.to_dict()
                        st.rerun()
                    
                    if st.button("🔐", key=f"pwd_{user_id}", help="Cambia password"):
                        st.session_state['show_password_form'] = True
                        st.session_state['password_mode'] = 'change'
                        st.session_state['password_user_data'] = original_row.to_dict()
                        st.rerun()
                    
                    if st.button("🔄", key=f"reset_{user_id}", help="Reset password"):
                        st.session_state['show_password_form'] = True
                        st.session_state['password_mode'] = 'reset'
                        st.session_state['password_user_data'] = original_row.to_dict()
                        st.rerun()
                    
                    # Pulsante DELETE - Solo per admin e non per se stesso
                    current_user = self.current_user
                    can_delete = (current_user and 
                                current_user.get('role_name') == 'Admin' and 
                                user_id != current_user.get('user_id'))
                    
                    if can_delete:
                        if st.button("🗑️", key=f"delete_{user_id}", help="Elimina utente"):
                            st.session_state['confirm_delete_user'] = user_id
                            st.session_state['delete_user_data'] = original_row.to_dict()
                            st.rerun()
                    else:
                        # Mostra pulsante disabilitato con tooltip
                        if st.button("🗑️", key=f"delete_{user_id}", help="Solo admin può eliminare utenti (e non se stesso)", disabled=True):
                            pass
                
                st.markdown("---")
    
    def render_user_actions(self):
        """Renderizza le azioni per gli utenti"""
        
        st.markdown("### ⚡ Azioni Rapide")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("👤 Nuovo Utente", use_container_width=True):
                st.session_state['show_user_form'] = True
                st.session_state['user_form_mode'] = 'create'
                st.rerun()
        
        with col2:
            if st.button("📊 Statistiche", use_container_width=True):
                self.show_user_stats()
        
        with col3:
            if st.button("📤 Export Excel", use_container_width=True):
                self.export_users_to_excel()
        
        with col4:
            if st.button("🔄 Aggiorna", use_container_width=True):
                st.rerun()
        
        # Aggiungi eliminazione multipla per admin
        current_user = self.current_user
        if current_user and current_user.get('role_name') == 'Admin':
            st.markdown("---")
            st.markdown("### 🗑️ Eliminazione Multipla")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.info("💡 Seleziona gli utenti da eliminare nella tabella sottostante")
            
            with col2:
                if st.button("🗑️ Elimina Selezionati", type="secondary", use_container_width=True):
                    st.warning("⚠️ Funzionalità di eliminazione multipla in arrivo...")
    
    def render_user_details(self, user_id: int):
        """Renderizza i dettagli di un utente"""
        
        user = self.db.get_user(user_id)
        if not user:
            st.error("❌ Utente non trovato")
            return
        
        st.markdown(f"### 👤 Dettagli Utente: {user['first_name']} {user['last_name']}")
        
        # Informazioni principali
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Nome:** {user['first_name']} {user['last_name']}")
            st.markdown(f"**Email:** {user['email']}")
            st.markdown(f"**Username:** {user['username']}")
            st.markdown(f"**Telefono:** {user['phone'] or 'N/A'}")
        
        with col2:
            st.markdown(f"**Ruolo:** {user['role_name']}")
            st.markdown(f"**Dipartimento:** {user['department_name'] or 'N/A'}")
            st.markdown(f"**Stato:** {'✅ Attivo' if user['is_active'] else '❌ Inattivo'}")
            st.markdown(f"**Admin:** {'👑 Sì' if user['is_admin'] else '👤 No'}")
        
        # Note
        if user.get('notes'):
            st.markdown(f"**Note:** {user['notes']}")
        
        # Date
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Creato:** {user['created_at']}")
        with col2:
            if user.get('last_login'):
                st.markdown(f"**Ultimo accesso:** {user['last_login']}")
        
        # Azioni
        st.markdown("### 🔧 Azioni")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✏️ Modifica", key=f"edit_user_{user_id}"):
                st.session_state['show_user_form'] = True
                st.session_state['user_form_mode'] = 'edit'
                st.session_state['edit_user_data'] = user
                st.rerun()
        
        with col2:
            if st.button("🔐 Cambia Password", key=f"change_pwd_{user_id}"):
                st.session_state['show_password_form'] = True
                st.session_state['password_mode'] = 'change'
                st.session_state['password_user_data'] = user
                st.rerun()
        
        with col3:
            if st.button("🔄 Reset Password", key=f"reset_pwd_{user_id}"):
                st.session_state['show_password_form'] = True
                st.session_state['password_mode'] = 'reset'
                st.session_state['password_user_data'] = user
                st.rerun()
        
        with col4:
            if st.button("🗑️ Elimina", key=f"delete_user_{user_id}"):
                self.delete_user(user_id)
    
    def show_user_stats(self):
        """Mostra statistiche sugli utenti"""
        
        stats = self.db.get_user_stats()
        
        st.markdown("### 📊 Statistiche Utenti")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_users = stats['total_users'][0]['count'] if stats['total_users'] else 0
            st.metric("👥 Utenti Totali", total_users)
        
        with col2:
            active_users = stats['active_users'][0]['count'] if stats['active_users'] else 0
            st.metric("✅ Utenti Attivi", active_users)
        
        with col3:
            admin_users = stats['admin_users'][0]['count'] if stats['admin_users'] else 0
            st.metric("👑 Admin", admin_users)
        
        with col4:
            recent_users = stats['recent_users'][0]['count'] if stats['recent_users'] else 0
            st.metric("🆕 Nuovi (30gg)", recent_users)
        
        # Utenti per ruolo
        st.markdown("#### 📋 Utenti per Ruolo")
        if stats['users_by_role']:
            role_df = pd.DataFrame(stats['users_by_role'])
            st.bar_chart(role_df.set_index('name')['count'])
    
    def export_users_to_excel(self):
        """Esporta gli utenti in Excel"""
        
        users = self.db.get_all_users()
        
        if not users:
            st.warning("📭 Nessun utente da esportare")
            return
        
        # Prepara i dati
        df = pd.DataFrame(users)
        
        # Formatta le colonne
        if not df.empty:
            df['Nome Completo'] = df.apply(
                lambda row: f"{row['first_name']} {row['last_name']}", 
                axis=1
            )
            df['Stato'] = df['is_active'].apply(lambda x: "Attivo" if x else "Inattivo")
            df['Admin'] = df['is_admin'].apply(lambda x: "Sì" if x else "No")
        
        # Seleziona colonne per export
        export_columns = [
            'Nome Completo', 'email', 'username', 'phone', 'role_name', 
            'department_name', 'Stato', 'Admin', 'created_at', 'notes'
        ]
        
        available_columns = [col for col in export_columns if col in df.columns]
        export_df = df[available_columns]
        
        # Genera il file Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"utenti_export_{timestamp}.xlsx"
        
        # Salva il file
        export_df.to_excel(filename, index=False, engine='openpyxl')
        
        # Download
        with open(filename, 'rb') as f:
            st.download_button(
                label="📥 Scarica Excel",
                data=f.read(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    def reset_user_password(self, user_id: int):
        """Reset della password di un utente"""
        
        if st.session_state.get('confirm_reset_password'):
            # Genera password temporanea
            import secrets
            import string
            
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            
            # Aggiorna password
            if self.db.update_user_password(user_id, temp_password):
                st.success(f"✅ Password resettata: {temp_password}")
                
                # Log attività
                self.db.log_activity(
                    user_id=self.current_user['user_id'],
                    action='reset_password',
                    entity_type='user',
                    entity_id=user_id,
                    details="Password resettata"
                )
            else:
                st.error("❌ Errore durante il reset della password")
            
            st.session_state['confirm_reset_password'] = False
        else:
            st.session_state['confirm_reset_password'] = True
            st.warning("⚠️ Conferma il reset della password")
    
    def delete_user(self, user_id: int):
        """Elimina un utente"""
        
        if st.session_state.get('confirm_delete_user'):
            if self.db.delete_user(user_id):
                st.success("✅ Utente eliminato con successo")
                
                # Log attività
                self.db.log_activity(
                    user_id=self.current_user['user_id'],
                    action='delete_user',
                    entity_type='user',
                    entity_id=user_id,
                    details="Utente eliminato"
                )
                
                st.rerun()
            else:
                st.error("❌ Errore durante l'eliminazione")
            
            st.session_state['confirm_delete_user'] = False
        else:
            st.session_state['confirm_delete_user'] = True
            st.warning("⚠️ Conferma l'eliminazione dell'utente")

def render_user_management_wrapper():
    """Wrapper per renderizzare la gestione utenti"""
    from components.auth.auth_manager import get_current_user
    
    # CONTROLLO SICUREZZA: Solo Admin può accedere alla gestione utenti
    current_user = get_current_user()
    if not current_user or current_user.get('role_name') != 'Admin':
        st.error("🚫 Accesso negato. Solo gli amministratori possono gestire gli utenti.")
        return
    
    management = UserManagement()
    
    # Gestione conferma eliminazione utente
    if st.session_state.get('confirm_delete_user'):
        user_id = st.session_state['confirm_delete_user']
        user_data = st.session_state.get('delete_user_data', {})
        
        st.markdown("### 🗑️ Conferma Eliminazione Utente")
        st.markdown("⚠️ **ATTENZIONE**: Questa azione è irreversibile!")
        
        st.markdown(f"""
        **Utente da eliminare:**
        - 👤 Nome: {user_data.get('first_name', 'N/A')} {user_data.get('last_name', 'N/A')}
        - 📧 Email: {user_data.get('email', 'N/A')}
        - 🔑 Username: {user_data.get('username', 'N/A')}
        - 👑 Ruolo: {user_data.get('role_name', 'N/A')}
        """)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            # Verifica se è un admin
            is_admin_user = user_data.get('role_id') == 1 or user_data.get('is_admin', False)
            
            if is_admin_user:
                st.warning("⚠️ **ATTENZIONE**: Stai per eliminare un utente ADMIN!")
                
            if st.button("✅ Conferma Eliminazione", type="primary", use_container_width=True):
                result = management.db.delete_user(user_id)
                
                if result:
                    st.success("✅ Utente eliminato con successo!")
                    
                    # Log attività
                    try:
                        management.db.log_activity(
                            user_id=current_user['user_id'],
                            action='delete_user',
                            entity_type='user',
                            entity_id=user_id,
                            details=f"Utente {user_data.get('username', 'N/A')} eliminato"
                        )
                    except Exception as e:
                        st.warning(f"⚠️ Errore nel log attività: {e}")
                    
                    # Pulisci session state
                    del st.session_state['confirm_delete_user']
                    if 'delete_user_data' in st.session_state:
                        del st.session_state['delete_user_data']
                    
                    st.rerun()
                else:
                    if is_admin_user:
                        st.error("❌ Impossibile eliminare l'utente: potrebbe essere l'ultimo admin del sistema")
                    else:
                        st.error("❌ Errore durante l'eliminazione dell'utente")
        
        with col2:
            if st.button("❌ Annulla", use_container_width=True):
                del st.session_state['confirm_delete_user']
                if 'delete_user_data' in st.session_state:
                    del st.session_state['delete_user_data']
                st.rerun()
        
        with col3:
            st.info("💡 **Suggerimento**: Prima di eliminare un utente, assicurati che non abbia dati associati (lead, task, etc.)")
    
    else:
        # Filtri
        filters = management.render_user_filters()
        
        # Azioni
        management.render_user_actions()
        
        # Tabella
        management.render_user_table(filters)

# Test della classe
if __name__ == "__main__":
    st.set_page_config(
        page_title="Test User Management",
        page_icon="👤",
        layout="wide"
    )
    
    st.title("🧪 Test User Management")
    
    # Test gestione utenti
    render_user_management_wrapper()
