#!/usr/bin/env python3
"""
Componente Lead Form per DASH_GESTIONE_LEAD
Form per inserimento e modifica lead
Creato da Ezio Camporeale
"""

import streamlit as st
from typing import Dict, Optional
import sys
from pathlib import Path
from datetime import datetime, date

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import get_current_user
from config import CUSTOM_COLORS

class LeadForm:
    """Gestisce il form per inserimento e modifica lead"""
    
    def __init__(self):
        """Inizializza il form lead"""
        self.db = DatabaseManager()
        self.current_user = get_current_user()
    
    def render_lead_form(self, lead_data: Optional[Dict] = None, mode: str = "create"):
        """
        Renderizza il form per inserimento/modifica lead
        
        Args:
            lead_data: Dati del lead per modifica (None per nuovo lead)
            mode: "create" per nuovo lead, "edit" per modifica
        """
        
        # Controlla i permessi dell'utente
        can_create = self.current_user and self.current_user.get('role_name') != 'Tester'
        can_edit = self.current_user and self.current_user.get('role_name') != 'Tester'
        
        if mode == "create" and not can_create:
            st.error("🔒 **Accesso Negato**: Il ruolo Tester non può creare nuovi lead per proteggere i dati")
            return None
        
        if mode == "edit" and not can_edit:
            st.error("🔒 **Accesso Negato**: Il ruolo Tester non può modificare lead per proteggere i dati")
            return None
        
        # Ottieni dati di lookup
        lead_states = self.db.get_lead_states()
        lead_categories = self.db.get_lead_categories()
        lead_priorities = self.db.get_lead_priorities()
        lead_sources = self.db.get_lead_sources()
        users = self.db.get_all_users()
        
        # Preparazione dati per selectbox
        states_options = {state['name']: state['id'] for state in lead_states}
        categories_options = {cat['name']: cat['id'] for cat in lead_categories}
        priorities_options = {pri['name']: pri['id'] for pri in lead_priorities}
        sources_options = {src['name']: src['id'] for src in lead_sources}
        users_options = {f"{user['first_name']} {user['last_name']}": user['id'] for user in users}
        
        # Titolo del form
        title = "📝 Nuovo Lead" if mode == "create" else "✏️ Modifica Lead"
        st.markdown(f"## {title}")
        
        # Form
        with st.form(f"lead_form_{mode}", clear_on_submit=(mode == "create")):
            
            # Informazioni base
            st.markdown("### 👤 Informazioni Base")
            col1, col2 = st.columns(2)
            
            with col1:
                # Gestisce sia formato Supabase (name) che SQLite (first_name + last_name)
                if lead_data and 'name' in lead_data and lead_data['name']:
                    # Formato Supabase: dividi name in first_name e last_name
                    name_parts = lead_data['name'].split(' ', 1)
                    default_first_name = name_parts[0] if name_parts else ''
                    default_last_name = name_parts[1] if len(name_parts) > 1 else ''
                elif lead_data and 'first_name' in lead_data and 'last_name' in lead_data:
                    # Formato SQLite: usa first_name e last_name
                    default_first_name = lead_data.get('first_name', '')
                    default_last_name = lead_data.get('last_name', '')
                else:
                    # Nuovo lead
                    default_first_name = ''
                    default_last_name = ''
                
                first_name = st.text_input(
                    "Nome *",
                    value=default_first_name,
                    help="Nome del lead"
                )
                
                email = st.text_input(
                    "Email",
                    value=lead_data.get('email', '') if lead_data else '',
                    help="Email del lead"
                )
                
                company = st.text_input(
                    "Azienda",
                    value=lead_data.get('company', '') if lead_data else '',
                    help="Nome dell'azienda"
                )
            
            with col2:
                last_name = st.text_input(
                    "Cognome *",
                    value=default_last_name,
                    help="Cognome del lead"
                )
                
                phone = st.text_input(
                    "Telefono",
                    value=lead_data.get('phone', '') if lead_data else '',
                    help="Numero di telefono"
                )
                
                position = st.text_input(
                    "Posizione",
                    value=lead_data.get('position', '') if lead_data else '',
                    help="Posizione lavorativa"
                )
            
            # Classificazione
            st.markdown("### 🏷️ Classificazione")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Stato
                current_state = lead_data.get('state_name', 'Nuovo') if lead_data else 'Nuovo'
                state_name = st.selectbox(
                    "Stato *",
                    options=list(states_options.keys()),
                    index=list(states_options.keys()).index(current_state) if current_state in states_options else 0,
                    help="Stato attuale del lead"
                )
                
                # Priorità
                current_priority = lead_data.get('priority_name', 'Media') if lead_data else 'Media'
                priority_name = st.selectbox(
                    "Priorità *",
                    options=list(priorities_options.keys()),
                    index=list(priorities_options.keys()).index(current_priority) if current_priority in priorities_options else 1,
                    help="Priorità del lead"
                )
            
            with col2:
                # Categoria
                current_category = lead_data.get('category_name', 'Tiepido') if lead_data else 'Tiepido'
                category_name = st.selectbox(
                    "Categoria",
                    options=list(categories_options.keys()),
                    index=list(categories_options.keys()).index(current_category) if current_category in categories_options else 1,
                    help="Categoria del lead (caldo/tiepido/freddo)"
                )
                
                # Fonte
                current_source = lead_data.get('source_name', 'Website') if lead_data else 'Website'
                source_name = st.selectbox(
                    "Fonte",
                    options=list(sources_options.keys()),
                    index=list(sources_options.keys()).index(current_source) if current_source in sources_options else 0,
                    help="Fonte di acquisizione del lead"
                )
            
            with col3:
                # Assegnazione
                if lead_data and 'assigned_first_name' in lead_data and 'assigned_last_name' in lead_data and lead_data.get('assigned_first_name'):
                    current_assigned = f"{lead_data['assigned_first_name']} {lead_data['assigned_last_name']}"
                else:
                    current_assigned = ''
                assigned_user = st.selectbox(
                    "Assegnato a",
                    options=[""] + list(users_options.keys()),
                    index=0 if not current_assigned else list(users_options.keys()).index(current_assigned) + 1,
                    help="Utente responsabile del lead"
                )
                
                # Budget
                budget = st.number_input(
                    "Budget (€)",
                    min_value=0.0,
                    value=float(lead_data.get('budget', 0)) if lead_data and lead_data.get('budget') else 0.0,
                    step=100.0,
                    help="Budget stimato del lead"
                )
            
            # Date e note
            st.markdown("### 📅 Date e Note")
            col1, col2 = st.columns(2)
            
            with col1:
                # Data chiusura prevista
                current_close_date = lead_data.get('expected_close_date') if lead_data else None
                if current_close_date:
                    current_close_date = datetime.strptime(current_close_date, '%Y-%m-%d').date()
                
                close_date = st.date_input(
                    "Data chiusura prevista",
                    value=current_close_date,
                    help="Data prevista di chiusura del deal"
                )
            
            with col2:
                # Note
                notes = st.text_area(
                    "Note",
                    value=lead_data.get('notes', '') if lead_data else '',
                    height=100,
                    help="Note aggiuntive sul lead"
                )
            
            # Pulsanti
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                submit_button = st.form_submit_button(
                    "💾 Salva Lead" if mode == "create" else "💾 Aggiorna Lead",
                    use_container_width=True
                )
            
            with col2:
                cancel_button = st.form_submit_button(
                    "❌ Annulla",
                    use_container_width=True
                )
            
            # Gestione submit
            if submit_button:
                if not first_name or not last_name:
                    st.error("❌ Nome e cognome sono obbligatori!")
                    return None
                
                # Prepara i dati
                form_data = {
                    'first_name': first_name.strip(),
                    'last_name': last_name.strip(),
                    'email': email.strip() if email else None,
                    'phone': phone.strip() if phone else None,
                    'company': company.strip() if company else None,
                    'position': position.strip() if position else None,
                    'lead_state_id': states_options[state_name],
                    'lead_priority_id': priorities_options[priority_name],
                    'lead_category_id': categories_options[category_name],
                    'lead_source_id': sources_options[source_name],
                    'assigned_to': users_options[assigned_user] if assigned_user else None,
                    'budget': budget if budget > 0 else None,
                    'expected_close_date': close_date.isoformat() if close_date else None,
                    'notes': notes.strip() if notes else None,
                    'created_by': self.current_user['user_id']
                }
                
                # Salva nel database
                if mode == "create":
                    lead_id = self.db.create_lead(form_data)
                    if lead_id:
                        st.success(f"✅ Lead '{first_name} {last_name}' creato con successo!")
                        
                        # Log attività
                        self.db.log_activity(
                            user_id=self.current_user['user_id'],
                            action='create_lead',
                            entity_type='lead',
                            entity_id=lead_id,
                            details=f"Creato nuovo lead: {first_name} {last_name}"
                        )
                        
                        return lead_id
                    else:
                        st.error("❌ Errore durante la creazione del lead")
                        return None
                
                else:  # mode == "edit"
                    if self.db.update_lead(lead_data['id'], form_data):
                        st.success(f"✅ Lead '{first_name} {last_name}' aggiornato con successo!")
                        
                        # Log attività
                        self.db.log_activity(
                            user_id=self.current_user['user_id'],
                            action='update_lead',
                            entity_type='lead',
                            entity_id=lead_data['id'],
                            details=f"Aggiornato lead: {first_name} {last_name}"
                        )
                        
                        return lead_data['id']
                    else:
                        st.error("❌ Errore durante l'aggiornamento del lead")
                        return None
            
            elif cancel_button:
                st.info("❌ Operazione annullata")
                return None
        
        return None

def render_lead_form_wrapper(lead_data: Optional[Dict] = None, mode: str = "create"):
    """Wrapper per renderizzare il form lead"""
    form = LeadForm()
    return form.render_lead_form(lead_data, mode)

# Test della classe
if __name__ == "__main__":
    st.set_page_config(
        page_title="Test Lead Form",
        page_icon="📝",
        layout="wide"
    )
    
    st.title("🧪 Test Lead Form")
    
    # Test form nuovo lead
    st.markdown("### Test Form Nuovo Lead")
    lead_id = render_lead_form_wrapper()
    
    if lead_id:
        st.success(f"✅ Lead creato con ID: {lead_id}")
        
        # Test form modifica lead
        st.markdown("### Test Form Modifica Lead")
        lead_data = {
            'id': lead_id,
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': 'mario.rossi@example.com',
            'phone': '+39 123 456 789',
            'company': 'Azienda Test',
            'position': 'Manager',
            'state_name': 'Contattato',
            'priority_name': 'Alta',
            'category_name': 'Caldo',
            'source_name': 'Website',
            'assigned_first_name': 'Admin',
            'assigned_last_name': 'User',
            'budget': 5000.0,
            'expected_close_date': '2025-12-31',
            'notes': 'Lead di test per sviluppo'
        }
        
        updated_id = render_lead_form_wrapper(lead_data, "edit")
        if updated_id:
            st.success(f"✅ Lead aggiornato con ID: {updated_id}")
