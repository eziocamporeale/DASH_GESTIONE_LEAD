#!/usr/bin/env python3
"""
Componente Bulk Task Creator per DASH_GESTIONE_LEAD
Creazione di task in massa per lead selezionati
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import get_current_user
from config import CUSTOM_COLORS

class BulkTaskCreator:
    """Gestisce la creazione di task in massa"""
    
    def __init__(self):
        """Inizializza il creator per task in massa"""
        self.db = DatabaseManager()
        self.current_user = get_current_user()
    
    def render_bulk_task_creator(self):
        """Renderizza l'interfaccia per creazione task in massa"""
        
        st.markdown("## 🚀 Creazione Task in Massa")
        st.markdown("Crea task multipli per i lead selezionati")
        
        # Ottieni dati di lookup
        task_states = self.db.get_task_states()
        task_types = self.db.get_task_types()
        lead_priorities = self.db.get_lead_priorities()
        users = self.db.get_all_users()
        leads = self.db.get_all_leads()
        
        # Preparazione dati per selectbox
        states_options = {state['name']: state['id'] for state in task_states}
        types_options = {task_type['name']: task_type['id'] for task_type in task_types}
        priorities_options = {pri['name']: pri['id'] for pri in lead_priorities}
        users_options = {f"{user['first_name']} {user['last_name']}": user['id'] for user in users}
        
        # Form per configurazione task in massa
        with st.form("bulk_task_form", clear_on_submit=False):
            
            # Configurazione del task
            st.markdown("### ⚙️ Configurazione Task")
            col1, col2 = st.columns(2)
            
            with col1:
                # Titolo del task
                task_title = st.text_input(
                    "Titolo Task *",
                    value="Chiamata di follow-up",
                    help="Titolo che verrà applicato a tutti i task"
                )
                
                # Tipo di task
                task_type = st.selectbox(
                    "Tipo Task *",
                    options=list(types_options.keys()),
                    index=0,
                    help="Tipo di attività per tutti i task"
                )
                
                # Priorità
                priority = st.selectbox(
                    "Priorità *",
                    options=list(priorities_options.keys()),
                    index=1,  # Media di default
                    help="Priorità per tutti i task"
                )
            
            with col2:
                # Stato iniziale
                initial_state = st.selectbox(
                    "Stato Iniziale *",
                    options=list(states_options.keys()),
                    index=0,  # Da Fare di default
                    help="Stato iniziale per tutti i task"
                )
                
                # Assegnazione
                assigned_user = st.selectbox(
                    "Assegnato a *",
                    options=[""] + list(users_options.keys()),
                    index=0,
                    help="Utente responsabile per tutti i task"
                )
                
                # Data di scadenza
                due_date_option = st.selectbox(
                    "Scadenza",
                    options=["Nessuna", "Oggi", "Domani", "Tra 3 giorni", "Tra 1 settimana", "Data specifica"],
                    index=3,  # Tra 3 giorni di default
                    help="Data di scadenza per tutti i task"
                )
            
            # Descrizione
            description = st.text_area(
                "Descrizione",
                value="Task creato automaticamente per follow-up con il cliente",
                height=100,
                help="Descrizione che verrà applicata a tutti i task"
            )
            
            # Calcola data di scadenza
            due_date = None
            if due_date_option != "Nessuna":
                today = date.today()
                if due_date_option == "Oggi":
                    due_date = today
                elif due_date_option == "Domani":
                    due_date = today + timedelta(days=1)
                elif due_date_option == "Tra 3 giorni":
                    due_date = today + timedelta(days=3)
                elif due_date_option == "Tra 1 settimana":
                    due_date = today + timedelta(days=7)
                elif due_date_option == "Data specifica":
                    due_date = st.date_input("Seleziona data", value=today + timedelta(days=3))
            
            st.markdown("---")
            
            # Selezione lead
            st.markdown("### 👥 Selezione Lead")
            
            # Filtri per lead
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Filtro per stato lead
                lead_states = self.db.get_lead_states()
                lead_state_options = ["Tutti"] + [state['name'] for state in lead_states]
                selected_lead_state = st.selectbox(
                    "Stato Lead",
                    options=lead_state_options,
                    index=0,
                    help="Filtra lead per stato"
                )
            
            with col2:
                # Filtro per priorità lead
                lead_priority_options = ["Tutte"] + [priority['name'] for priority in lead_priorities]
                selected_lead_priority = st.selectbox(
                    "Priorità Lead",
                    options=lead_priority_options,
                    index=0,
                    help="Filtra lead per priorità"
                )
            
            with col3:
                # Filtro per categoria lead
                lead_categories = self.db.get_lead_categories()
                lead_category_options = ["Tutte"] + [cat['name'] for cat in lead_categories]
                selected_lead_category = st.selectbox(
                    "Categoria Lead",
                    options=lead_category_options,
                    index=0,
                    help="Filtra lead per categoria"
                )
            
            # Applica filtri ai lead
            filtered_leads = self._filter_leads(leads, selected_lead_state, selected_lead_priority, selected_lead_category, lead_states, lead_priorities, lead_categories)
            
            # Mostra statistiche lead filtrati
            st.info(f"📊 **{len(filtered_leads)} lead** trovati con i filtri applicati")
            
            if len(filtered_leads) == 0:
                st.warning("⚠️ Nessun lead trovato con i filtri selezionati. Modifica i filtri per vedere i lead disponibili.")
                return None
            
            # Selezione lead con checkbox
            st.markdown("#### Seleziona Lead:")
            
            # Opzioni per selezione
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("✅ Seleziona Tutti", use_container_width=True):
                    st.session_state['selected_leads'] = [lead['id'] for lead in filtered_leads]
                    st.rerun()
            
            with col2:
                if st.button("❌ Deseleziona Tutti", use_container_width=True):
                    st.session_state['selected_leads'] = []
                    st.rerun()
            
            # Inizializza selected_leads se non esiste
            if 'selected_leads' not in st.session_state:
                st.session_state['selected_leads'] = []
            
            # Lista lead con checkbox
            selected_count = 0
            for lead in filtered_leads:
                lead_id = lead['id']
                is_selected = lead_id in st.session_state['selected_leads']
                
                # Formatta nome lead
                if 'first_name' in lead and 'last_name' in lead:
                    lead_name = f"{lead['first_name']} {lead['last_name']}"
                elif 'name' in lead:
                    lead_name = lead['name']
                else:
                    lead_name = "Lead senza nome"
                
                company = lead.get('company', 'N/A')
                phone = lead.get('phone', 'N/A')
                
                # Checkbox per selezione
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                
                with col1:
                    if st.checkbox("", value=is_selected, key=f"lead_{lead_id}"):
                        if lead_id not in st.session_state['selected_leads']:
                            st.session_state['selected_leads'].append(lead_id)
                        selected_count += 1
                    else:
                        if lead_id in st.session_state['selected_leads']:
                            st.session_state['selected_leads'].remove(lead_id)
                
                with col2:
                    st.write(f"**{lead_name}**")
                
                with col3:
                    st.write(f"🏢 {company}")
                
                with col4:
                    st.write(f"📞 {phone}")
            
            st.markdown(f"### 📋 Riepilogo")
            st.write(f"**{selected_count} lead selezionati** per la creazione di task")
            
            if due_date:
                st.write(f"**Data scadenza:** {due_date.strftime('%d/%m/%Y')}")
            
            # Pulsanti di azione
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                create_button = st.form_submit_button(
                    "🚀 Crea Task in Massa",
                    use_container_width=True,
                    type="primary"
                )
            
            with col2:
                preview_button = st.form_submit_button(
                    "👁️ Anteprima",
                    use_container_width=True
                )
            
            with col3:
                cancel_button = st.form_submit_button(
                    "❌ Annulla",
                    use_container_width=True
                )
            
            # Gestione azioni
            if create_button:
                if selected_count == 0:
                    st.error("❌ Seleziona almeno un lead per creare i task")
                elif not task_title.strip():
                    st.error("❌ Inserisci un titolo per il task")
                elif not assigned_user:
                    st.error("❌ Seleziona un utente per l'assegnazione")
                else:
                    # Crea i task
                    success_count = self._create_bulk_tasks(
                        selected_leads=st.session_state['selected_leads'],
                        task_title=task_title,
                        task_type=types_options[task_type],
                        priority=priorities_options[priority],
                        state=states_options[initial_state],
                        assigned_user=users_options[assigned_user],
                        description=description,
                        due_date=due_date
                    )
                    
                    if success_count > 0:
                        st.success(f"✅ Creati {success_count} task con successo!")
                        # Reset selezione
                        st.session_state['selected_leads'] = []
                        st.rerun()
                    else:
                        st.error("❌ Errore durante la creazione dei task")
            
            elif preview_button:
                if selected_count == 0:
                    st.warning("⚠️ Seleziona almeno un lead per vedere l'anteprima")
                else:
                    self._show_preview(
                        selected_leads=st.session_state['selected_leads'],
                        filtered_leads=filtered_leads,
                        task_title=task_title,
                        task_type=task_type,
                        priority=priority,
                        initial_state=initial_state,
                        assigned_user=assigned_user,
                        description=description,
                        due_date=due_date
                    )
            
            elif cancel_button:
                st.info("❌ Operazione annullata")
                st.session_state['selected_leads'] = []
                st.rerun()
    
    def _filter_leads(self, leads, selected_lead_state, selected_lead_priority, selected_lead_category, lead_states, lead_priorities, lead_categories):
        """Filtra i lead in base ai criteri selezionati"""
        filtered_leads = leads.copy()
        
        # Filtro per stato
        if selected_lead_state != "Tutti":
            state_id = next((state['id'] for state in lead_states if state['name'] == selected_lead_state), None)
            if state_id:
                filtered_leads = [lead for lead in filtered_leads if lead.get('state_id') == state_id]
        
        # Filtro per priorità
        if selected_lead_priority != "Tutte":
            priority_id = next((priority['id'] for priority in lead_priorities if priority['name'] == selected_lead_priority), None)
            if priority_id:
                filtered_leads = [lead for lead in filtered_leads if lead.get('priority_id') == priority_id]
        
        # Filtro per categoria
        if selected_lead_category != "Tutte":
            category_id = next((cat['id'] for cat in lead_categories if cat['name'] == selected_lead_category), None)
            if category_id:
                filtered_leads = [lead for lead in filtered_leads if lead.get('category_id') == category_id]
        
        return filtered_leads
    
    def _create_bulk_tasks(self, selected_leads, task_title, task_type, priority, state, assigned_user, description, due_date):
        """Crea i task in massa per i lead selezionati"""
        success_count = 0
        
        for lead_id in selected_leads:
            task_data = {
                'title': task_title,
                'description': description,
                'lead_id': lead_id,
                'task_type_id': task_type,
                'priority_id': priority,
                'state_id': state,
                'assigned_to': assigned_user,
                'due_date': due_date.isoformat() if due_date else None,
                'created_by': self.current_user['user_id']
            }
            
            if self.db.create_task(task_data):
                success_count += 1
                
                # Log attività
                self.db.log_activity(
                    user_id=self.current_user['user_id'],
                    action='create_bulk_task',
                    entity_type='task',
                    entity_id=lead_id,
                    details=f"Task creato in massa: {task_title} per lead {lead_id}"
                )
        
        return success_count
    
    def _show_preview(self, selected_leads, filtered_leads, task_title, task_type, priority, initial_state, assigned_user, description, due_date):
        """Mostra un'anteprima dei task che verranno creati"""
        st.markdown("### 👁️ Anteprima Task da Creare")
        
        # Crea DataFrame per l'anteprima
        preview_data = []
        for lead_id in selected_leads:
            lead = next((lead for lead in filtered_leads if lead['id'] == lead_id), None)
            if lead:
                if 'first_name' in lead and 'last_name' in lead:
                    lead_name = f"{lead['first_name']} {lead['last_name']}"
                elif 'name' in lead:
                    lead_name = lead['name']
                else:
                    lead_name = "Lead senza nome"
                
                preview_data.append({
                    'Lead': lead_name,
                    'Azienda': lead.get('company', 'N/A'),
                    'Telefono': lead.get('phone', 'N/A'),
                    'Titolo Task': task_title,
                    'Tipo': task_type,
                    'Priorità': priority,
                    'Stato': initial_state,
                    'Assegnato a': assigned_user,
                    'Scadenza': due_date.strftime('%d/%m/%Y') if due_date else 'Nessuna'
                })
        
        if preview_data:
            df = pd.DataFrame(preview_data)
            st.dataframe(df, use_container_width=True)
            
            st.markdown(f"**Totale task da creare:** {len(preview_data)}")
            st.markdown(f"**Descrizione:** {description}")

def render_bulk_task_creator_wrapper():
    """Wrapper per renderizzare il creator per task in massa"""
    creator = BulkTaskCreator()
    return creator.render_bulk_task_creator()

# Test della classe
if __name__ == "__main__":
    st.set_page_config(
        page_title="Test Bulk Task Creator",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🧪 Test Bulk Task Creator")
    render_bulk_task_creator_wrapper()
