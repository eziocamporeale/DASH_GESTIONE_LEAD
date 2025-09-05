#!/usr/bin/env python3
"""
Componente Password Manager per DASH_GESTIONE_LEAD
Gestione password utenti (solo admin)
Creato da Ezio Camporeale
"""

import streamlit as st
from typing import Dict, List, Optional
import sys
from pathlib import Path
from datetime import datetime

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import get_current_user, AuthManager
from config import CUSTOM_COLORS

class PasswordManager:
    """Gestisce la modifica delle password degli utenti (solo admin)"""
    
    def __init__(self):
        """Inizializza il gestore password"""
        self.db = DatabaseManager()
        self.auth = AuthManager()
        self.current_user = get_current_user()
    
    def render_password_change_form(self, user_data: Dict):
        """
        Renderizza il form per cambiare la password di un utente
        
        Args:
            user_data: Dati dell'utente di cui cambiare la password
        """
        
        st.markdown("### 🔐 Cambio Password")
        st.markdown(f"**Utente:** {user_data['first_name']} {user_data['last_name']} ({user_data['username']})")
        
        # Form per cambio password
        with st.form("password_change_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_password = st.text_input(
                    "Nuova Password *",
                    type="password",
                    help="Inserisci la nuova password (minimo 8 caratteri)"
                )
            
            with col2:
                confirm_password = st.text_input(
                    "Conferma Password *",
                    type="password",
                    help="Conferma la nuova password"
                )
            
            # Pulsanti
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                submit_button = st.form_submit_button(
                    "💾 Salva Password",
                    type="primary",
                    use_container_width=True
                )
            
            with col2:
                cancel_button = st.form_submit_button(
                    "❌ Annulla",
                    use_container_width=True
                )
            
            if cancel_button:
                # Torna alla gestione utenti
                st.session_state['show_password_form'] = False
                if 'password_user_data' in st.session_state:
                    del st.session_state['password_user_data']
                st.rerun()
            
            if submit_button:
                # Validazione password
                if not new_password or len(new_password) < 8:
                    st.error("❌ La password deve essere di almeno 8 caratteri")
                    return
                
                if new_password != confirm_password:
                    st.error("❌ Le password non coincidono")
                    return
                
                # Cambia la password
                success = self.change_user_password(user_data['id'], new_password)
                
                if success:
                    st.success(f"✅ Password aggiornata con successo per {user_data['username']}")
                    
                    # Registra l'attività
                    self.db.log_activity(
                        user_id=self.current_user['user_id'],
                        action='change_password',
                        entity_type='user',
                        entity_id=user_data['id'],
                        details=f"Password cambiata per utente {user_data['username']}"
                    )
                    
                    # Torna alla gestione utenti
                    st.session_state['show_password_form'] = False
                    if 'password_user_data' in st.session_state:
                        del st.session_state['password_user_data']
                    st.rerun()
                else:
                    st.error("❌ Errore nell'aggiornamento della password")
    
    def change_user_password(self, user_id: int, new_password: str) -> bool:
        """
        Cambia la password di un utente
        
        Args:
            user_id: ID dell'utente
            new_password: Nuova password
            
        Returns:
            bool: True se successo, False altrimenti
        """
        try:
            # Hash della nuova password
            password_hash = self.auth.hash_password(new_password)
            
            # Aggiorna la password nel database
            result = self.db.supabase.table('users').update({
                'password_hash': password_hash,
                'updated_at': datetime.now().isoformat()
            }).eq('id', user_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            st.error(f"❌ Errore nel cambio password: {e}")
            return False
    
    def render_password_reset_form(self, user_data: Dict):
        """
        Renderizza il form per resettare la password di un utente
        
        Args:
            user_data: Dati dell'utente di cui resettare la password
        """
        
        st.markdown("### 🔄 Reset Password")
        st.markdown(f"**Utente:** {user_data['first_name']} {user_data['last_name']} ({user_data['username']})")
        
        st.warning("⚠️ **Attenzione:** Il reset della password imposterà una password temporanea che l'utente dovrà cambiare al prossimo login.")
        
        # Password temporanea di default
        temp_password = "temp123456"
        
        with st.form("password_reset_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input(
                    "Password Temporanea",
                    value=temp_password,
                    disabled=True,
                    help="Password temporanea che verrà assegnata all'utente"
                )
            
            with col2:
                st.text_input(
                    "Conferma Password Temporanea",
                    value=temp_password,
                    disabled=True
                )
            
            # Pulsanti
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                submit_button = st.form_submit_button(
                    "🔄 Reset Password",
                    type="primary",
                    use_container_width=True
                )
            
            with col2:
                cancel_button = st.form_submit_button(
                    "❌ Annulla",
                    use_container_width=True
                )
            
            if cancel_button:
                # Torna alla gestione utenti
                st.session_state['show_password_form'] = False
                if 'password_user_data' in st.session_state:
                    del st.session_state['password_user_data']
                st.rerun()
            
            if submit_button:
                # Reset della password
                success = self.change_user_password(user_data['id'], temp_password)
                
                if success:
                    st.success(f"✅ Password resettata con successo per {user_data['username']}")
                    st.info(f"📧 **Password temporanea:** {temp_password}")
                    st.info("💡 L'utente dovrà cambiare questa password al prossimo login")
                    
                    # Registra l'attività
                    self.db.log_activity(
                        user_id=self.current_user['user_id'],
                        action='reset_password',
                        entity_type='user',
                        entity_id=user_data['id'],
                        details=f"Password resettata per utente {user_data['username']}"
                    )
                    
                    # Torna alla gestione utenti
                    st.session_state['show_password_form'] = False
                    if 'password_user_data' in st.session_state:
                        del st.session_state['password_user_data']
                    st.rerun()
                else:
                    st.error("❌ Errore nel reset della password")

def render_password_manager_wrapper():
    """Wrapper per il gestore password"""
    password_manager = PasswordManager()
    
    # Verifica che l'utente sia admin
    if not password_manager.current_user or password_manager.current_user['role_name'] != 'Admin':
        st.error("🚫 Accesso negato. Solo gli amministratori possono gestire le password.")
        return
    
    # Controlla se mostrare il form password
    if st.session_state.get('show_password_form', False):
        user_data = st.session_state.get('password_user_data', None)
        password_mode = st.session_state.get('password_mode', 'change')
        
        if not user_data:
            st.error("❌ Dati utente non trovati")
            return
        
        # Pulsante per tornare alla gestione utenti
        if st.button("← Torna alla Gestione Utenti"):
            st.session_state['show_password_form'] = False
            if 'password_user_data' in st.session_state:
                del st.session_state['password_user_data']
            if 'password_mode' in st.session_state:
                del st.session_state['password_mode']
            st.rerun()
        
        # Renderizza il form appropriato
        if password_mode == 'change':
            password_manager.render_password_change_form(user_data)
        elif password_mode == 'reset':
            password_manager.render_password_reset_form(user_data)
    
    else:
        st.info("🔐 Seleziona un utente dalla tabella per gestire la sua password")
