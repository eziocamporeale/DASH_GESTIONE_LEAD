#!/usr/bin/env python3
"""
Componente Task Form per DASH_GESTIONE_LEAD
Form per creazione e modifica task
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

class TaskForm:
    """Gestisce il form per creazione e modifica task"""
    
    def __init__(self):
        """Inizializza il form task"""
        self.db = DatabaseManager()
        self.current_user = get_current_user()
    
    def render_task_form(self, task_data: Optional[Dict] = None, mode: str = "create", lead_id: Optional[int] = None):
        """
        Renderizza il form per creazione/modifica task
        
        Args:
            task_data: Dati del task per modifica (None per nuovo task)
            mode: "create" per nuovo task, "edit" per modifica
            lead_id: ID del lead associato (se specificato)
        """
        
        # Ottieni dati di lookup
        task_states = self.db.get_task_states()
        task_types = self.db.get_task_types()
        lead_priorities = self.db.get_lead_priorities()
        users = self.db.get_all_users()
        leads = self.db.get_leads() if not lead_id else []
        
        # Preparazione dati per selectbox
        states_options = {state['name']: state['id'] for state in task_states}
        types_options = {task_type['name']: task_type['id'] for task_type in task_types}
        priorities_options = {pri['name']: pri['id'] for pri in lead_priorities}
        users_options = {f"{user['first_name']} {user['last_name']}": user['id'] for user in users}
        # Gestisce sia first_name/last_name che name per i leads
        leads_options = {}
        for lead in leads:
            if 'first_name' in lead and 'last_name' in lead:
                # Formato SQLite
                name = f"{lead['first_name']} {lead['last_name']}"
            elif 'name' in lead:
                # Formato Supabase
                name = lead['name']
            else:
                name = "Lead senza nome"
            
            company = lead.get('company', 'N/A')
            leads_options[f"{name} ({company})"] = lead['id']
        
        # Titolo del form
        title = "📋 Nuovo Task" if mode == "create" else "✏️ Modifica Task"
        st.markdown(f"## {title}")
        
        # Form
        with st.form(f"task_form_{mode}", clear_on_submit=(mode == "create")):
            
            # Informazioni base
            st.markdown("### 📝 Informazioni Task")
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input(
                    "Titolo *",
                    value=task_data.get('title', '') if task_data else '',
                    help="Titolo del task"
                )
                
                task_type = st.selectbox(
                    "Tipo Task *",
                    options=list(types_options.keys()),
                    index=list(types_options.keys()).index(task_data.get('type_name', 'Chiamata')) if task_data else 0,
                    help="Tipo di attività"
                )
            
            with col2:
                priority = st.selectbox(
                    "Priorità *",
                    options=list(priorities_options.keys()),
                    index=list(priorities_options.keys()).index(task_data.get('priority_name', 'Media')) if task_data else 1,
                    help="Priorità del task"
                )
                
                state = st.selectbox(
                    "Stato *",
                    options=list(states_options.keys()),
                    index=list(states_options.keys()).index(task_data.get('state_name', 'Da Fare')) if task_data else 0,
                    help="Stato attuale del task"
                )
            
            # Descrizione
            description = st.text_area(
                "Descrizione",
                value=task_data.get('description', '') if task_data else '',
                height=100,
                help="Descrizione dettagliata del task"
            )
            
            # Assegnazione e Lead
            st.markdown("### 👥 Assegnazione e Lead")
            col1, col2 = st.columns(2)
            
            with col1:
                # Assegnazione
                current_assigned = task_data.get('assigned_first_name', '') + ' ' + task_data.get('assigned_last_name', '') if task_data and task_data.get('assigned_first_name') else ''
                assigned_user = st.selectbox(
                    "Assegnato a *",
                    options=[""] + list(users_options.keys()),
                    index=0 if not current_assigned else list(users_options.keys()).index(current_assigned) + 1,
                    help="Utente responsabile del task"
                )
            
            with col2:
                # Lead associato
                if lead_id:
                    # Se è specificato un lead, mostra solo quello
                    lead = self.db.get_lead(lead_id)
                    if lead:
                        # Gestisce sia first_name/last_name che name per i leads
                        if 'first_name' in lead and 'last_name' in lead:
                            lead_name = f"{lead['first_name']} {lead['last_name']}"
                        elif 'name' in lead:
                            lead_name = lead['name']
                        else:
                            lead_name = "Lead senza nome"
                        st.markdown(f"**Lead associato:** {lead_name} ({lead['company'] or 'N/A'})")
                        selected_lead = lead_id
                    else:
                        st.error("Lead non trovato")
                        return None
                else:
                    # Seleziona lead da lista
                    current_lead = task_data.get('lead_id') if task_data else None
                    if current_lead:
                        lead = self.db.get_lead(current_lead)
                        if lead:
                            if 'first_name' in lead and 'last_name' in lead:
                                lead_name = f"{lead['first_name']} {lead['last_name']}"
                            elif 'name' in lead:
                                lead_name = lead['name']
                            else:
                                lead_name = "Lead senza nome"
                            current_lead_name = f"{lead_name} ({lead['company'] or 'N/A'})"
                        else:
                            current_lead_name = ""
                    else:
                        current_lead_name = ""
                    
                    # Trova l'indice corretto per il lead corrente
                    lead_index = 0
                    if current_lead_name and current_lead_name in leads_options.keys():
                        lead_index = list(leads_options.keys()).index(current_lead_name) + 1
                    
                    selected_lead = st.selectbox(
                        "Lead associato",
                        options=[""] + list(leads_options.keys()),
                        index=lead_index,
                        help="Lead associato al task (opzionale)"
                    )
            
            # Date
            st.markdown("### 📅 Date")
            col1, col2 = st.columns(2)
            
            with col1:
                # Data scadenza
                current_due_date = task_data.get('due_date') if task_data else None
                if current_due_date:
                    try:
                        # Gestisce formato ISO8601 di Supabase (2025-09-04T00:00:00+00:00)
                        if 'T' in str(current_due_date):
                            current_due_date = datetime.fromisoformat(str(current_due_date).replace('Z', '+00:00')).date()
                        else:
                            # Formato SQLite (2025-09-04)
                            current_due_date = datetime.strptime(str(current_due_date), '%Y-%m-%d').date()
                    except Exception as e:
                        st.warning(f"⚠️ Errore parsing data: {e}")
                        current_due_date = None
                
                due_date = st.date_input(
                    "Data scadenza",
                    value=current_due_date,
                    help="Data di scadenza del task"
                )
            
            with col2:
                # Data completamento (solo per task completati)
                if task_data and task_data.get('state_name') == 'Completato':
                    completed_at = task_data.get('completed_at')
                    if completed_at:
                        try:
                            # Gestisce formato ISO8601 di Supabase
                            if 'T' in str(completed_at):
                                completed_at = datetime.fromisoformat(str(completed_at).replace('Z', '+00:00')).date()
                            else:
                                # Formato SQLite
                                completed_at = datetime.strptime(str(completed_at), '%Y-%m-%d %H:%M:%S').date()
                        except Exception as e:
                            st.warning(f"⚠️ Errore parsing data completamento: {e}")
                            completed_at = date.today()
                    else:
                        completed_at = date.today()
                    
                    st.date_input(
                        "Data completamento",
                        value=completed_at,
                        disabled=True,
                        help="Data di completamento del task"
                    )
            
            # Pulsanti
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                submit_button = st.form_submit_button(
                    "💾 Salva Task" if mode == "create" else "💾 Aggiorna Task",
                    type="primary"
                )
            
            with col2:
                cancel_button = st.form_submit_button(
                    "❌ Annulla",
                    type="secondary"
                )
            
            # Gestione submit
            if submit_button:
                if not title or not assigned_user:
                    st.error("❌ Titolo e assegnazione sono obbligatori!")
                    return None
                
                # Prepara i dati
                form_data = {
                    'title': title.strip(),
                    'description': description.strip() if description else None,
                    'task_type_id': types_options[task_type],
                    'state_id': states_options[state],
                    'priority_id': priorities_options[priority],
                    'assigned_to': users_options[assigned_user],
                    'lead_id': leads_options[selected_lead] if selected_lead else None,
                    'due_date': due_date.isoformat() if due_date else None,
                    'created_by': self.current_user['user_id']
                }
                
                # Salva nel database
                if mode == "create":
                    task_id = self.db.create_task(form_data)
                    if task_id:
                        st.success(f"✅ Task '{title}' creato con successo!")
                        
                        # Log attività
                        self.db.log_activity(
                            user_id=self.current_user['user_id'],
                            action='create_task',
                            entity_type='task',
                            entity_id=task_id,
                            details=f"Creato nuovo task: {title}"
                        )
                        
                        return task_id
                    else:
                        st.error("❌ Errore durante la creazione del task")
                        return None
                
                else:  # mode == "edit"
                    if self.db.update_task(task_data['id'], form_data):
                        st.success(f"✅ Task '{title}' aggiornato con successo!")
                        
                        # Log attività
                        self.db.log_activity(
                            user_id=self.current_user['user_id'],
                            action='update_task',
                            entity_type='task',
                            entity_id=task_data['id'],
                            details=f"Aggiornato task: {title}"
                        )
                        
                        return task_data['id']
                    else:
                        st.error("❌ Errore durante l'aggiornamento del task")
                        return None
            
            elif cancel_button:
                st.info("❌ Operazione annullata")
                return None
        
        return None

def render_task_form_wrapper(task_data: Optional[Dict] = None, mode: str = "create", lead_id: Optional[int] = None):
    """Wrapper per renderizzare il form task"""
    form = TaskForm()
    return form.render_task_form(task_data, mode, lead_id)

# Test della classe
if __name__ == "__main__":
    st.set_page_config(
        page_title="Test Task Form",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("🧪 Test Task Form")
    
    # Test form nuovo task
    st.markdown("### Test Form Nuovo Task")
    task_id = render_task_form_wrapper()
    
    if task_id:
        st.success(f"✅ Task creato con ID: {task_id}")
        
        # Test form modifica task
        st.markdown("### Test Form Modifica Task")
        task_data = {
            'id': task_id,
            'title': 'Chiamata di follow-up',
            'description': 'Chiamare il cliente per aggiornamento',
            'type_name': 'Chiamata',
            'priority_name': 'Alta',
            'state_name': 'In Corso',
            'assigned_first_name': 'Admin',
            'assigned_last_name': 'User',
            'due_date': '2025-12-31',
            'lead_id': 1
        }
        
        updated_id = render_task_form_wrapper(task_data, "edit")
        if updated_id:
            st.success(f"✅ Task aggiornato con ID: {updated_id}")
