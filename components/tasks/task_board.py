#!/usr/bin/env python3
"""
Componente Task Board per DASH_GESTIONE_LEAD
Board Kanban per gestione task
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
import sys
from pathlib import Path
from datetime import datetime, date

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import get_current_user
from config import CUSTOM_COLORS

class TaskBoard:
    """Gestisce la board Kanban dei task"""
    
    def __init__(self):
        """Inizializza la board task"""
        self.db = DatabaseManager()
        self.current_user = get_current_user()
    
    def render_task_board(self, filters: Dict = None):
        """Renderizza la board Kanban dei task"""
        
        # Selettore di visualizzazione
        view_mode = st.radio(
            "📊 Modalità Visualizzazione:",
            ["📋 Board Kanban", "📅 Vista Settimanale"],
            horizontal=True,
            key="task_view_mode"
        )
        
        # Ottieni tutti i task
        tasks = self.db.get_tasks(filters=filters, limit=100)
        
        if view_mode == "📅 Vista Settimanale":
            self.render_weekly_view(tasks)
            return
        
        if not tasks:
            st.info("📭 Nessun task trovato")
            
            # Mostra azioni rapide quando non ci sono task
            st.markdown("### ⚡ Azioni Rapide")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("📝 Nuovo Task", use_container_width=True, key="new_task_empty_board"):
                    st.session_state['show_task_form'] = True
                    st.session_state['task_form_mode'] = 'create'
                    st.rerun()
            
            with col2:
                st.button("📊 Export Excel", use_container_width=True, disabled=True, help="Nessun dato da esportare")
            
            with col3:
                st.button("📈 Analytics", use_container_width=True, disabled=True, help="Nessun dato per analytics")
            
            with col4:
                st.button("🗑️ Elimina Multipli", use_container_width=True, disabled=True, help="Nessun task da eliminare")
            
            with col5:
                if st.button("🔄 Aggiorna", use_container_width=True, key="refresh_empty_board"):
                    st.rerun()
            
            return
        
        # Ottieni gli stati dei task
        task_states = self.db.get_task_states()
        
        # Organizza i task per stato
        tasks_by_state = {}
        for state in task_states:
            tasks_by_state[state['name']] = []
        
        for task in tasks:
            state_name = task['state_name']
            if state_name in tasks_by_state:
                tasks_by_state[state_name].append(task)
        
        # Header della board compatta
        st.markdown("## 📋 Board Kanban")
        
        # Azioni rapide compatte
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("📝 Nuovo Task", use_container_width=True, key="new_task_board"):
                st.session_state['show_task_form'] = True
                st.session_state['task_form_mode'] = 'create'
                st.rerun()
        
        with col2:
            if st.button("📊 Export Excel", use_container_width=True, key="export_board"):
                # TODO: Implementare export Excel
                st.info("📊 Funzionalità export in sviluppo")
        
        with col3:
            if st.button("📈 Analytics", use_container_width=True, key="analytics_board"):
                # TODO: Implementare analytics
                st.info("📈 Funzionalità analytics in sviluppo")
        
        with col4:
            if st.button("🗑️ Elimina Multipli", use_container_width=True, key="delete_multiple_board"):
                # TODO: Implementare eliminazione multipla
                st.info("🗑️ Funzionalità eliminazione multipla in sviluppo")
        
        with col5:
            if st.button("🔄 Aggiorna", use_container_width=True, key="refresh_board"):
                st.rerun()
        
        # Statistiche rapide
        total_tasks = len(tasks)
        
        # Gestisce le date ISO8601 da Supabase
        overdue_tasks = 0
        for t in tasks:
            if t.get('due_date') and t['state_name'] != 'Completato':
                try:
                    # Gestisce sia formato ISO8601 che semplice
                    if 'T' in str(t['due_date']):
                        due_date = datetime.fromisoformat(str(t['due_date']).replace('Z', '+00:00')).date()
                    else:
                        due_date = datetime.strptime(str(t['due_date']), '%Y-%m-%d').date()
                    if due_date < date.today():
                        overdue_tasks += 1
                except:
                    continue
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Task Totali", total_tasks)
        with col2:
            st.metric("⏰ Task Scaduti", overdue_tasks, delta=f"-{overdue_tasks}" if overdue_tasks > 0 else None)
        with col3:
            completed_tasks = len([t for t in tasks if t['state_name'] == 'Completato'])
            st.metric("✅ Task Completati", completed_tasks)
        with col4:
            in_progress_tasks = len([t for t in tasks if t['state_name'] == 'In Corso'])
            st.metric("🔄 In Corso", in_progress_tasks)
        
        # Board Kanban con colonne collassabili
        st.markdown("### 🎯 Board")
        
        # Inizializza lo stato delle colonne se non esiste
        if 'collapsed_columns' not in st.session_state:
            st.session_state['collapsed_columns'] = {}
        
        # Pulsanti per controllare tutte le colonne
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("📂 Comprimi Tutto", key="collapse_all"):
                for state in task_states:
                    st.session_state['collapsed_columns'][state['name']] = True
                st.rerun()
        
        with col2:
            if st.button("📁 Espandi Tutto", key="expand_all"):
                for state in task_states:
                    st.session_state['collapsed_columns'][state['name']] = False
                st.rerun()
        
        # Crea le colonne per ogni stato
        columns = st.columns(len(task_states), gap="small")
        
        for i, state in enumerate(task_states):
            with columns[i]:
                # Header della colonna collassabile
                state_color = state['color']
                state_name = state['name']
                task_count = len(tasks_by_state[state_name])
                
                # Controlla se la colonna è collassata
                is_collapsed = st.session_state['collapsed_columns'].get(state_name, True)
                
                # Header con pulsante toggle
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div style="background: {state_color}; color: white; padding: 8px; border-radius: 4px; text-align: center; margin-bottom: 8px; font-size: 0.9rem; cursor: pointer;">
                        <strong>{state_name}</strong> ({task_count})
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Pulsante per espandere/comprimere
                    toggle_icon = "📂" if is_collapsed else "📁"
                    if st.button(toggle_icon, key=f"toggle_{state['id']}", help=f"{'Espandi' if is_collapsed else 'Comprimi'} {state_name}"):
                        st.session_state['collapsed_columns'][state_name] = not is_collapsed
                        st.rerun()
                
                # Contenuto della colonna (visibile solo se espansa)
                if not is_collapsed:
                    # Pulsante per aggiungere task in questo stato
                    if st.button(f"➕", key=f"add_task_{state['id']}", help=f"Aggiungi task in {state_name}"):
                        st.session_state['show_task_form'] = True
                        st.session_state['task_form_mode'] = 'create'
                        st.session_state['default_task_state'] = state['id']
                        st.rerun()
                    
                    # Task in questo stato
                    for task in tasks_by_state[state_name]:
                        self.render_task_card(task, state)
                else:
                    # Mostra solo un riassunto compatto
                    if task_count > 0:
                        st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 8px; border-radius: 4px; text-align: center; font-size: 0.8rem; color: #666;">
                            {task_count} task
                        </div>
                        """, unsafe_allow_html=True)
    
    def render_task_card(self, task: Dict, state: Dict):
        """Renderizza una card di task"""
        
        # Determina il colore della priorità
        priority_colors = {
            'Alta': '#DC3545',
            'Media': '#FFC107', 
            'Bassa': '#28A745'
        }
        priority_name = task.get('priority_name', 'N/A')
        priority_color = priority_colors.get(priority_name, '#6C757D')
        
        # Determina se il task è scaduto
        is_overdue = False
        if task.get('due_date'):
            try:
                # Gestisce sia formato ISO8601 che semplice
                if 'T' in str(task['due_date']):
                    due_date = datetime.fromisoformat(str(task['due_date']).replace('Z', '+00:00')).date()
                else:
                    due_date = datetime.strptime(str(task['due_date']), '%Y-%m-%d').date()
                is_overdue = due_date < date.today() and task['state_name'] != 'Completato'
            except:
                is_overdue = False
        
        # Preparo tutti i contenuti prima di renderizzare
        lead_info = ""
        if task.get('lead_first_name') and task.get('lead_last_name'):
            lead_name = f"{task['lead_first_name']} {task['lead_last_name']}"
            client_id = task.get('lead_client_id', 'N/A')
            lead_info = f'<div style="margin: 6px 0; font-size: 14px;">👥 <strong>{lead_name[:15]}{"..." if len(lead_name) > 15 else ""}</strong></div><div style="margin: 6px 0; font-size: 12px; color: #666;">🔢 <strong>Cliente #{client_id}</strong></div>'
        
        # Descrizione del task
        description_info = ""
        if task.get('description') and task['description'].strip():
            description_text = task['description'].strip()
            # Tronca la descrizione se troppo lunga
            if len(description_text) > 50:
                description_text = description_text[:50] + "..."
            description_info = f'<div style="margin: 6px 0; font-size: 13px; color: #666; font-style: italic;">📝 {description_text}</div>'
        
        due_date_info = '<div style="margin: 6px 0; font-size: 14px;">📅 <strong>N/A</strong></div>'
        if task.get('due_date'):
            try:
                if 'T' in str(task['due_date']):
                    due_date = datetime.fromisoformat(str(task['due_date']).replace('Z', '+00:00')).date()
                else:
                    due_date = datetime.strptime(str(task['due_date']), '%Y-%m-%d').date()
                due_date_info = f'<div style="margin: 6px 0; font-size: 14px;">📅 <strong>{due_date.strftime("%d/%m")}</strong></div>'
            except:
                pass
        
        overdue_warning = ""
        if is_overdue:
            overdue_warning = '<div style="margin: 6px 0; font-size: 14px; color: #DC3545;">⚠️ <strong>SCADUTO</strong></div>'
        
        # Card del task con CSS INLINE SEMPLICE
        with st.container():
            # Colori e stili
            border_color = "#DC3545" if is_overdue else priority_color
            background_color = '#fff5f5' if is_overdue else '#ffffff'
            
            # CSS INLINE SEMPLICE - tutto su una riga (senza pulsanti HTML)
            st.markdown(f"""<div style="border:4px solid {border_color};border-radius:16px;padding:20px;margin:16px 0;background:{background_color};box-shadow:0 6px 12px rgba(0,0,0,0.2);min-height:120px;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;"><div style="font-size:1.1rem;font-weight:bold;color:#2c3e50;">{task['title'][:20]}{'...' if len(task['title']) > 20 else ''}</div><div style="background:{priority_color};color:white;padding:4px 8px;border-radius:12px;font-size:10px;text-align:center;font-weight:bold;">{priority_name[:3]}</div></div><hr style="margin:12px 0;border:none;border-top:1px solid #e9ecef;"><div style="margin:12px 0;padding:12px;background:rgba(255,255,255,0.9);border-radius:12px;border-left:4px solid {priority_color};"><div style="margin:6px 0;font-size:14px;">📋 <strong>{task.get('task_type_name', 'N/A')[:8]}{'...' if len(task.get('task_type_name', 'N/A')) > 8 else ''}</strong></div><div style="margin:6px 0;font-size:14px;">👤 <strong>{task['assigned_first_name'][:8]}{'...' if len(task['assigned_first_name']) > 8 else ''}</strong></div>{description_info}{lead_info}{due_date_info}{overdue_warning}</div></div>""", unsafe_allow_html=True)
            
            # Pulsanti Streamlit funzionali fuori dal div HTML
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Modifica", key=f"edit_task_{task['id']}", use_container_width=True):
                    st.session_state['show_task_form'] = True
                    st.session_state['task_form_mode'] = 'edit'
                    st.session_state['edit_task_data'] = task
                    st.rerun()
            
            with col2:
                if st.button("▶️ Avanza", key=f"advance_task_{task['id']}", use_container_width=True):
                    self.advance_task_state(task['id'], task['state_id'])
                    st.rerun()
    
    def advance_task_state(self, task_id: int, current_state_id: int):
        """Avanza lo stato di un task"""
        
        # Ottieni gli stati disponibili
        task_states = self.db.get_task_states()
        
        # Trova il prossimo stato
        current_index = None
        for i, state in enumerate(task_states):
            if state['id'] == current_state_id:
                current_index = i
                break
        
        if current_index is not None and current_index < len(task_states) - 1:
            next_state = task_states[current_index + 1]
            
            # Aggiorna lo stato
            if self.db.update_task_state(task_id, next_state['id']):
                st.success(f"✅ Task avanzato a: {next_state['name']}")
                
                # Log attività
                self.db.log_activity(
                    user_id=self.current_user['user_id'],
                    action='advance_task_state',
                    entity_type='task',
                    entity_id=task_id,
                    details=f"Task avanzato a {next_state['name']}"
                )
            else:
                st.error("❌ Errore durante l'aggiornamento")
        else:
            st.info("ℹ️ Task già nello stato finale")
    
    def render_task_list(self, filters: Dict = None):
        """Renderizza la lista dei task in formato tabella"""
        
        # Ottieni i task
        tasks = self.db.get_tasks(filters=filters, limit=50)
        
        if not tasks:
            st.info("📭 Nessun task trovato")
            
            # Mostra azioni rapide quando non ci sono task
            st.markdown("### ⚡ Azioni Rapide")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("📝 Nuovo Task", use_container_width=True, key="new_task_empty_list"):
                    st.session_state['show_task_form'] = True
                    st.session_state['task_form_mode'] = 'create'
                    st.rerun()
            
            with col2:
                st.button("📊 Export Excel", use_container_width=True, disabled=True, help="Nessun dato da esportare")
            
            with col3:
                st.button("📈 Analytics", use_container_width=True, disabled=True, help="Nessun dato per analytics")
            
            with col4:
                st.button("🗑️ Elimina Multipli", use_container_width=True, disabled=True, help="Nessun task da eliminare")
            
            with col5:
                if st.button("🔄 Aggiorna", use_container_width=True, key="refresh_empty_list"):
                    st.rerun()
            
            return
        
        # Converti in DataFrame
        df = pd.DataFrame(tasks)
        
        # Prepara le colonne per la visualizzazione
        if not df.empty:
            # Formatta le date
            if 'due_date' in df.columns:
                df['due_date'] = pd.to_datetime(df['due_date']).dt.strftime('%d/%m/%Y')
            
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y')
            
            # Combina assigned user
            df['Assegnato a'] = df.apply(
                lambda row: f"{row['assigned_first_name']} {row['assigned_last_name']}" 
                if row['assigned_first_name'] and row['assigned_last_name'] else "-", 
                axis=1
            )
            
            # Combina lead (gestisce campi mancanti)
            df['Lead'] = df.apply(
                lambda row: f"{row.get('lead_first_name', '')} {row.get('lead_last_name', '')}".strip() 
                if row.get('lead_first_name') and row.get('lead_last_name') else "-", 
                axis=1
            )
        
        # Azioni rapide
        st.markdown("### ⚡ Azioni Rapide")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("📝 Nuovo Task", use_container_width=True, key="new_task_list"):
                st.session_state['show_task_form'] = True
                st.session_state['task_form_mode'] = 'create'
                st.rerun()
        
        with col2:
            if st.button("📊 Export Excel", use_container_width=True, key="export_list"):
                # TODO: Implementare export Excel
                st.info("📊 Funzionalità export in sviluppo")
        
        with col3:
            if st.button("📈 Analytics", use_container_width=True, key="analytics_list"):
                # TODO: Implementare analytics
                st.info("📈 Funzionalità analytics in sviluppo")
        
        with col4:
            if st.button("🗑️ Elimina Multipli", use_container_width=True, key="delete_multiple_list"):
                # TODO: Implementare eliminazione multipla
                st.info("🗑️ Funzionalità eliminazione multipla in sviluppo")
        
        with col5:
            if st.button("🔄 Aggiorna", use_container_width=True, key="refresh_list"):
                st.rerun()
        
        # Mostra la tabella
        st.markdown("### 📊 Lista Task")
        
        if not df.empty:
            # Seleziona solo le colonne da mostrare
            display_columns = [
                'title', 'task_type_name', 'state_name', 'priority_name', 
                'Assegnato a', 'Lead', 'due_date', 'created_at'
            ]
            
            # Filtra le colonne disponibili
            available_columns = [col for col in display_columns if col in df.columns]
            display_df = df[available_columns]
            
            # Rinomina le colonne
            column_mapping = {
                'title': '📋 Titolo',
                'task_type_name': '📝 Tipo',
                'state_name': '📈 Stato',
                'priority_name': '⚡ Priorità',
                'Assegnato a': '👤 Assegnato',
                'Lead': '👥 Lead',
                'due_date': '📅 Scadenza',
                'created_at': '📅 Creato'
            }
            
            display_df = display_df.rename(columns=column_mapping)
            
            # Mostra la tabella
            st.dataframe(
                display_df,
                hide_index=True
            )
    
    def render_task_filters(self) -> Dict:
        """Renderizza i filtri per i task"""
        
        st.markdown("### 🔍 Filtri Task")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Filtro stato
            states = self.db.get_task_states()
            state_options = ["Tutti"] + [state['name'] for state in states]
            selected_state = st.selectbox(
                "Stato",
                options=state_options,
                index=0
            )
        
        with col2:
            # Filtro tipo
            types = self.db.get_task_types()
            type_options = ["Tutti"] + [task_type['name'] for task_type in types]
            selected_type = st.selectbox(
                "Tipo",
                options=type_options,
                index=0
            )
        
        with col3:
            # Filtro assegnazione
            users = self.db.get_all_users()
            user_options = ["Tutti"] + [f"{user['first_name']} {user['last_name']}" for user in users]
            selected_user = st.selectbox(
                "Assegnato a",
                options=user_options,
                index=0
            )
        
        with col4:
            # Filtro scadenza
            due_filter = st.selectbox(
                "Scadenza",
                options=["Tutti", "Scaduti", "Oggi", "Questa settimana", "Questo mese"],
                index=0
            )
        
        # Preparazione filtri
        filters = {}
        
        if selected_state != "Tutti":
            state_id = next((state['id'] for state in states if state['name'] == selected_state), None)
            if state_id:
                filters['state_id'] = state_id
        
        if selected_type != "Tutti":
            type_id = next((task_type['id'] for task_type in types if task_type['name'] == selected_type), None)
            if type_id:
                filters['task_type_id'] = type_id
        
        if selected_user != "Tutti":
            user_id = next((user['id'] for user in users if f"{user['first_name']} {user['last_name']}" == selected_user), None)
            if user_id:
                filters['assigned_to'] = user_id
        
        return filters
    
    def render_weekly_view(self, tasks: List[Dict]):
        """Renderizza la vista settimanale dei task organizzati per giorni"""
        
        if not tasks:
            st.info("📭 Nessun task trovato per questa settimana")
            return
        
        # Converti i task in DataFrame per facilitare la manipolazione
        df = pd.DataFrame(tasks)
        
        # Aggiungi colonna giorno della settimana
        if 'due_date' in df.columns:
            df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
            df['giorno_settimana'] = df['due_date'].dt.day_name()
            df['data_formattata'] = df['due_date'].dt.strftime('%d/%m/%Y')
        else:
            st.warning("⚠️ Campo 'due_date' non trovato nei task")
            return
        
        # Ordina i giorni della settimana
        giorni_ordine = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        giorni_italiani = {
            'Monday': 'Lunedì',
            'Tuesday': 'Martedì', 
            'Wednesday': 'Mercoledì',
            'Thursday': 'Giovedì',
            'Friday': 'Venerdì',
            'Saturday': 'Sabato',
            'Sunday': 'Domenica'
        }
        
        # CSS per le card dei giorni
        st.markdown("""
        <style>
        .giorno-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 1rem;
            margin: 0.5rem 0;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .giorno-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }
        .giorno-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        .giorno-title {
            font-size: 1.2rem;
            font-weight: bold;
        }
        .giorno-count {
            background: rgba(255,255,255,0.2);
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        .task-item {
            background: rgba(255,255,255,0.1);
            padding: 0.8rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            border-left: 4px solid #ffd700;
        }
        .task-title {
            font-weight: bold;
            margin-bottom: 0.3rem;
        }
        .task-details {
            font-size: 0.85rem;
            opacity: 0.9;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Raggruppa i task per giorno
        task_per_giorno = {}
        for giorno in giorni_ordine:
            task_per_giorno[giorno] = df[df['giorno_settimana'] == giorno]
        
        # Controlli per espandere/comprimere tutti
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("📖 Espandi Tutto", help="Espandi tutti i giorni"):
                for giorno in giorni_ordine:
                    collapse_key = f"collapse_{giorno.lower()}"
                    st.session_state[collapse_key] = True
                st.rerun()
        
        with col2:
            if st.button("📕 Comprimi Tutto", help="Comprimi tutti i giorni"):
                for giorno in giorni_ordine:
                    collapse_key = f"collapse_{giorno.lower()}"
                    st.session_state[collapse_key] = False
                st.rerun()
        
        with col3:
            st.markdown("**🎛️ Controlli Rapidi**")
        
        st.markdown("---")
        
        # Mostra i giorni della settimana con funzionalità collassabile
        for giorno in giorni_ordine:
            tasks_giorno = task_per_giorno[giorno]
            giorno_italiano = giorni_italiani[giorno]
            
            if not tasks_giorno.empty:
                # Crea una chiave unica per il session state
                collapse_key = f"collapse_{giorno.lower()}"
                
                # Inizializza lo stato se non esiste
                if collapse_key not in st.session_state:
                    st.session_state[collapse_key] = True
                
                is_expanded = st.session_state[collapse_key]
                
                # Icona dinamica basata sullo stato di espansione
                icona_espansione = "📖" if is_expanded else "📕"
                
                # Header del giorno cliccabile
                st.markdown(f"""
                <div class="giorno-card" style="cursor: pointer;" onclick="toggleDay('{collapse_key}')">
                    <div class="giorno-header">
                        <div class="giorno-title">{icona_espansione} {giorno_italiano}</div>
                        <div class="giorno-count">{len(tasks_giorno)} task</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Pulsante invisibile per gestire il click
                if st.button(f"Toggle {giorno_italiano}", key=f"btn_{collapse_key}", help=f"Clicca per espandere/comprimere {giorno_italiano}"):
                    st.session_state[collapse_key] = not st.session_state[collapse_key]
                    st.rerun()
                
                # Mostra i task del giorno solo se espanso
                if is_expanded:
                    for _, task in tasks_giorno.iterrows():
                        stato = task.get('state_name', 'N/A')
                        assegnato = f"{task.get('assigned_first_name', '')} {task.get('assigned_last_name', '')}".strip()
                        if not assegnato:
                            assegnato = "Non assegnato"
                        
                        # Informazioni del lead
                        lead_info = ""
                        if task.get('lead_first_name') and task.get('lead_last_name'):
                            lead_name = f"{task.get('lead_first_name', '')} {task.get('lead_last_name', '')}".strip()
                            client_id = task.get('lead_client_id', 'N/A')
                            lead_info = f" | 👥 {lead_name} (#{client_id})"
                        
                        st.markdown(f"""
                        <div class="task-item">
                            <div class="task-title">📋 {task.get('title', 'N/A')}</div>
                            <div class="task-details">
                                📅 {task.get('data_formattata', 'N/A')} | 
                                👤 {assegnato} | 
                                🏷️ {stato}{lead_info}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Se non ci sono task per nessun giorno
        if all(task_per_giorno[giorno].empty for giorno in giorni_ordine):
            st.info("📭 Nessun task con data di scadenza per questa settimana")

def render_task_board_wrapper():
    """Wrapper per renderizzare la board task"""
    board = TaskBoard()
    
    # Controlla se mostrare il form o la board
    if st.session_state.get('show_task_form', False):
        # Mostra il form
        task_data = st.session_state.get('edit_task_data', None)
        mode = st.session_state.get('task_form_mode', 'create')
        lead_id = st.session_state.get('create_task_for_lead', None)
        
        # Pulsante per tornare alla board
        if st.button("← Torna alla Board Task"):
            st.session_state['show_task_form'] = False
            if 'edit_task_data' in st.session_state:
                del st.session_state['edit_task_data']
            if 'task_form_mode' in st.session_state:
                del st.session_state['task_form_mode']
            if 'create_task_for_lead' in st.session_state:
                del st.session_state['create_task_for_lead']
            st.rerun()
        
        # Importa e renderizza il form
        from components.tasks.task_form import render_task_form_wrapper
        task_id = render_task_form_wrapper(task_data, mode, lead_id)
        
        if task_id:
            # Reset dello stato e torna alla board
            st.session_state['show_task_form'] = False
            if 'edit_task_data' in st.session_state:
                del st.session_state['edit_task_data']
            if 'task_form_mode' in st.session_state:
                del st.session_state['task_form_mode']
            if 'create_task_for_lead' in st.session_state:
                del st.session_state['create_task_for_lead']
            st.rerun()
    
    else:
        # Mostra la board
        # Filtri
        filters = board.render_task_filters()
        
        # Tab per board e lista
        tab1, tab2 = st.tabs(["🎯 Board Kanban", "📊 Lista Task"])
        
        with tab1:
            board.render_task_board(filters)
        
        with tab2:
            board.render_task_list(filters)
    
    def render_weekly_view(self, tasks: List[Dict]):
        """Renderizza la vista settimanale dei task organizzati per giorni"""
        
        if not tasks:
            st.info("📭 Nessun task trovato per questa settimana")
            return
        
        # Converti i task in DataFrame per facilitare la manipolazione
        df = pd.DataFrame(tasks)
        
        # Aggiungi colonna giorno della settimana
        if 'due_date' in df.columns:
            df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
            df['giorno_settimana'] = df['due_date'].dt.day_name()
            df['data_formattata'] = df['due_date'].dt.strftime('%d/%m/%Y')
        else:
            st.warning("⚠️ Campo 'due_date' non trovato nei task")
            return
        
        # Ordina i giorni della settimana
        giorni_ordine = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        giorni_italiani = {
            'Monday': 'Lunedì',
            'Tuesday': 'Martedì', 
            'Wednesday': 'Mercoledì',
            'Thursday': 'Giovedì',
            'Friday': 'Venerdì',
            'Saturday': 'Sabato',
            'Sunday': 'Domenica'
        }
        
        # CSS per le card dei giorni
        st.markdown("""
        <style>
        .giorno-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 1rem;
            margin: 0.5rem 0;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .giorno-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }
        .giorno-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        .giorno-title {
            font-size: 1.2rem;
            font-weight: bold;
        }
        .task-count {
            background: rgba(255,255,255,0.2);
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        .task-item {
            background: rgba(255,255,255,0.9);
            color: #333;
            padding: 0.8rem;
            margin: 0.5rem 0;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .task-title {
            font-weight: bold;
            margin-bottom: 0.3rem;
        }
        .task-meta {
            font-size: 0.8rem;
            color: #666;
        }
        .priority-high { border-left-color: #dc3545; }
        .priority-medium { border-left-color: #ffc107; }
        .priority-low { border-left-color: #28a745; }
        </style>
        """, unsafe_allow_html=True)
        
        # Raggruppa i task per giorno
        task_per_giorno = df.groupby('giorno_settimana')
        
        # Crea le colonne per i giorni della settimana
        cols = st.columns(7)
        
        for i, giorno_eng in enumerate(giorni_ordine):
            with cols[i]:
                giorno_ita = giorni_italiani[giorno_eng]
                
                # Task per questo giorno
                if giorno_eng in task_per_giorno.groups:
                    tasks_giorno = task_per_giorno.get_group(giorno_eng)
                    task_count = len(tasks_giorno)
                else:
                    tasks_giorno = pd.DataFrame()
                    task_count = 0
                
                # Header del giorno
                st.markdown(f"""
                <div class="giorno-card">
                    <div class="giorno-header">
                        <div class="giorno-title">{giorno_ita}</div>
                        <div class="task-count">{task_count} task</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Task del giorno
                if not tasks_giorno.empty:
                    for _, task in tasks_giorno.iterrows():
                        # Determina la classe CSS per la priorità
                        priority_class = ""
                        if 'priority_name' in task and task['priority_name']:
                            if 'alta' in task['priority_name'].lower():
                                priority_class = "priority-high"
                            elif 'media' in task['priority_name'].lower():
                                priority_class = "priority-medium"
                            elif 'bassa' in task['priority_name'].lower():
                                priority_class = "priority-low"
                        
                        # Informazioni del task
                        title = task.get('title', 'N/A')
                        state = task.get('state_name', 'N/A')
                        assigned = task.get('assigned_first_name', '') + ' ' + task.get('assigned_last_name', '')
                        assigned = assigned.strip() if assigned.strip() else 'Non assegnato'
                        
                        # Informazioni del lead
                        lead_info = ""
                        if task.get('lead_first_name') and task.get('lead_last_name'):
                            lead_name = f"{task.get('lead_first_name', '')} {task.get('lead_last_name', '')}".strip()
                            client_id = task.get('lead_client_id', 'N/A')
                            lead_info = f"<br>👥 {lead_name} (#{client_id})"
                        
                        st.markdown(f"""
                        <div class="task-item {priority_class}">
                            <div class="task-title">{title}</div>
                            <div class="task-meta">
                                📋 {state}<br>
                                👤 {assigned}<br>
                                📅 {task.get('data_formattata', 'N/A')}{lead_info}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="text-align: center; color: rgba(255,255,255,0.7); padding: 1rem;">
                        📭 Nessun task
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Statistiche settimanali
        st.markdown("---")
        st.markdown("### 📊 Statistiche Settimanali")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tasks = len(df)
            st.metric("📋 Task Totali", total_tasks)
        
        with col2:
            giorni_con_task = len([g for g in giorni_ordine if g in task_per_giorno.groups])
            st.metric("📅 Giorni Attivi", giorni_con_task)
        
        with col3:
            if 'priority_name' in df.columns:
                alta_priorita = len(df[df['priority_name'].str.contains('alta', case=False, na=False)])
                st.metric("🔴 Alta Priorità", alta_priorita)
            else:
                st.metric("🔴 Alta Priorità", 0)
        
        with col4:
            if 'state_name' in df.columns:
                completati = len(df[df['state_name'].str.contains('completato', case=False, na=False)])
                st.metric("✅ Completati", completati)
            else:
                st.metric("✅ Completati", 0)

# Test della classe
if __name__ == "__main__":
    st.set_page_config(
        page_title="Test Task Board",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("🧪 Test Task Board")
    
    # Test board task
    render_task_board_wrapper()
