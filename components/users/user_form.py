#!/usr/bin/env python3
"""
Componente User Form per DASH_GESTIONE_LEAD
Form per creazione e modifica utenti
Creato da Ezio Camporeale
"""

import streamlit as st
from typing import Dict, Optional
import sys
from pathlib import Path
from datetime import datetime

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import get_current_user, AuthManager
from config import CUSTOM_COLORS

class UserForm:
    """Gestisce il form per creazione e modifica utenti"""
    
    def __init__(self):
        """Inizializza il form utente"""
        self.db = DatabaseManager()
        self.auth = AuthManager()
        self.current_user = get_current_user()
    
    def render_user_form(self, user_data: Optional[Dict] = None, mode: str = "create"):
        """
        Renderizza il form per creazione/modifica utente
        
        Args:
            user_data: Dati dell'utente per modifica (None per nuovo utente)
            mode: "create" per nuovo utente, "edit" per modifica
        """
        
        # Ottieni dati di lookup
        roles = self.db.get_roles()
        departments = self.db.get_departments()
        
        # Preparazione dati per selectbox
        roles_options = {role['name']: role['id'] for role in roles}
        departments_options = {dept['name']: dept['id'] for dept in departments}
        
        # Titolo del form
        title = "👤 Nuovo Utente" if mode == "create" else "✏️ Modifica Utente"
        st.markdown(f"## {title}")
        
        # Form
        with st.form(f"user_form_{mode}", clear_on_submit=(mode == "create")):
            
            # Informazioni personali
            st.markdown("### 👤 Informazioni Personali")
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input(
                    "Nome *",
                    value=user_data.get('first_name', '') if user_data else '',
                    help="Nome dell'utente"
                )
                
                email = st.text_input(
                    "Email *",
                    value=user_data.get('email', '') if user_data else '',
                    help="Email dell'utente"
                )
            
            with col2:
                last_name = st.text_input(
                    "Cognome *",
                    value=user_data.get('last_name', '') if user_data else '',
                    help="Cognome dell'utente"
                )
                
                phone = st.text_input(
                    "Telefono",
                    value=user_data.get('phone', '') if user_data else '',
                    help="Numero di telefono"
                )
            
            # Ruolo e Dipartimento
            st.markdown("### 🏢 Ruolo e Dipartimento")
            col1, col2 = st.columns(2)
            
            with col1:
                # Ruolo
                current_role = user_data.get('role_name', '') if user_data else ''
                # Gestisce il caso in cui current_role sia "N/A" o non valido
                if current_role and current_role != 'N/A' and current_role in roles_options:
                    role_index = list(roles_options.keys()).index(current_role)
                else:
                    role_index = 0
                
                role = st.selectbox(
                    "Ruolo *",
                    options=list(roles_options.keys()),
                    index=role_index,
                    help="Ruolo dell'utente nel sistema"
                )
            
            with col2:
                # Dipartimento
                current_department = user_data.get('department_name', '') if user_data else ''
                # Gestisce il caso in cui current_department sia "N/A" o non valido
                if current_department and current_department != 'N/A' and current_department in departments_options:
                    department_index = list(departments_options.keys()).index(current_department) + 1
                else:
                    department_index = 0
                
                department = st.selectbox(
                    "Dipartimento",
                    options=[""] + list(departments_options.keys()),
                    index=department_index,
                    help="Dipartimento di appartenenza"
                )
            
            # Credenziali
            st.markdown("### 🔐 Credenziali")
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input(
                    "Username *",
                    value=user_data.get('username', '') if user_data else '',
                    help="Nome utente per l'accesso"
                )
            
            with col2:
                # Password solo per nuovo utente o se richiesto
                if mode == "create":
                    password = st.text_input(
                        "Password *",
                        type="password",
                        help="Password per l'accesso"
                    )
                else:
                    password = st.text_input(
                        "Nuova Password (lasciare vuoto per non modificare)",
                        type="password",
                        help="Nuova password (opzionale)"
                    )
            
            # Informazioni aggiuntive
            st.markdown("### 📝 Informazioni Aggiuntive")
            
            # Note
            notes = st.text_area(
                "Note",
                value=user_data.get('notes', '') if user_data else '',
                height=80,
                help="Note aggiuntive sull'utente"
            )
            
            # Stato utente
            col1, col2 = st.columns(2)
            
            with col1:
                is_active = st.checkbox(
                    "Utente Attivo",
                    value=user_data.get('is_active', True) if user_data else True,
                    help="L'utente può accedere al sistema"
                )
            
            with col2:
                # Solo per admin: permessi speciali
                if self.current_user.get('role_name') == 'Admin':
                    is_admin = st.checkbox(
                        "Permessi Admin",
                        value=user_data.get('is_admin', False) if user_data else False,
                        help="Permessi amministrativi speciali"
                    )
                else:
                    is_admin = user_data.get('is_admin', False) if user_data else False
            
            # Pulsanti
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                submit_button = st.form_submit_button(
                    "💾 Salva Utente" if mode == "create" else "💾 Aggiorna Utente",
                    use_container_width=True
                )
            
            with col2:
                cancel_button = st.form_submit_button(
                    "❌ Annulla",
                    use_container_width=True
                )
            
            # Gestione submit
            if submit_button:
                if not first_name or not last_name or not email or not username:
                    st.error("❌ Nome, cognome, email e username sono obbligatori!")
                    return None
                
                if mode == "create" and not password:
                    st.error("❌ Password obbligatoria per nuovo utente!")
                    return None
                
                # Verifica email unica
                if mode == "create":
                    existing_user = self.db.get_user_by_email(email)
                    if existing_user:
                        st.error("❌ Email già registrata!")
                        return None
                
                # Verifica username unico
                if mode == "create":
                    existing_user = self.db.get_user_by_username(username)
                    if existing_user:
                        st.error("❌ Username già in uso!")
                        return None
                
                # Prepara i dati
                form_data = {
                    'first_name': first_name.strip(),
                    'last_name': last_name.strip(),
                    'email': email.strip().lower(),
                    'phone': phone.strip() if phone else None,
                    'username': username.strip().lower(),
                    'role_id': roles_options[role],
                    'department_id': departments_options[department] if department else None,
                    'notes': notes.strip() if notes else None,
                    'is_active': is_active,
                    'is_admin': is_admin
                }
                
                # Gestione password
                if mode == "create":
                    form_data['password_hash'] = password  # Usa password_hash per Supabase
                elif password:  # Modifica con nuova password
                    form_data['password_hash'] = password  # Usa password_hash per Supabase
                
                # Salva nel database
                if mode == "create":
                    user_id = self.db.create_user(form_data)
                    if user_id:
                        st.success(f"✅ Utente '{first_name} {last_name}' creato con successo!")
                        
                        # Log attività
                        self.db.log_activity(
                            user_id=self.current_user['user_id'],
                            action='create_user',
                            entity_type='user',
                            entity_id=user_id,
                            details=f"Creato nuovo utente: {first_name} {last_name}"
                        )
                        
                        return user_id
                    else:
                        st.error("❌ Errore durante la creazione dell'utente")
                        return None
                
                else:  # mode == "edit"
                    if self.db.update_user(user_data['id'], form_data):
                        st.success(f"✅ Utente '{first_name} {last_name}' aggiornato con successo!")
                        
                        # Log attività
                        self.db.log_activity(
                            user_id=self.current_user['user_id'],
                            action='update_user',
                            entity_type='user',
                            entity_id=user_data['id'],
                            details=f"Aggiornato utente: {first_name} {last_name}"
                        )
                        
                        return user_data['id']
                    else:
                        st.error("❌ Errore durante l'aggiornamento dell'utente")
                        return None
            
            elif cancel_button:
                st.info("❌ Operazione annullata")
                return None
        
        return None

def render_user_form_wrapper(user_data: Optional[Dict] = None, mode: str = "create"):
    """Wrapper per renderizzare il form utente"""
    form = UserForm()
    return form.render_user_form(user_data, mode)

# Test della classe
if __name__ == "__main__":
    st.set_page_config(
        page_title="Test User Form",
        page_icon="👤",
        layout="wide"
    )
    
    st.title("🧪 Test User Form")
    
    # Test form nuovo utente
    st.markdown("### Test Form Nuovo Utente")
    user_id = render_user_form_wrapper()
    
    if user_id:
        st.success(f"✅ Utente creato con ID: {user_id}")
        
        # Test form modifica utente
        st.markdown("### Test Form Modifica Utente")
        user_data = {
            'id': user_id,
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'mario.rossi@example.com',
            'phone': '+39 123 456 789',
            'username': 'mario.rossi',
            'role_name': 'Manager',
            'department_name': 'Vendite',
            'notes': 'Manager vendite esperto',
            'is_active': True,
            'is_admin': False
        }
        
        updated_id = render_user_form_wrapper(user_data, "edit")
        if updated_id:
            st.success(f"✅ Utente aggiornato con ID: {updated_id}")
