#!/usr/bin/env python3
"""
Componente Contact Sequence per DASH_GESTIONE_LEAD
Gestione sequenze di contatto automatiche
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import get_current_user
from config import CUSTOM_COLORS

class ContactSequence:
    """Gestisce le sequenze di contatto"""
    
    def __init__(self):
        """Inizializza la sequenza di contatto"""
        self.db = DatabaseManager()
        self.current_user = get_current_user()
    
    def render_sequence_form(self, sequence_data: Optional[Dict] = None, mode: str = "create"):
        """
        Renderizza il form per creazione/modifica sequenza
        
        Args:
            sequence_data: Dati della sequenza per modifica (None per nuova sequenza)
            mode: "create" per nuova sequenza, "edit" per modifica
        """
        
        # Titolo del form
        title = "📞 Nuova Sequenza" if mode == "create" else "✏️ Modifica Sequenza"
        st.markdown(f"## {title}")
        
        # Form
        with st.form(f"sequence_form_{mode}", clear_on_submit=(mode == "create")):
            
            # Informazioni base
            st.markdown("### 📝 Informazioni Sequenza")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    "Nome Sequenza *",
                    value=sequence_data.get('name', '') if sequence_data else '',
                    help="Nome identificativo della sequenza"
                )
                
                sequence_type = st.selectbox(
                    "Tipo *",
                    options=["Lead Nascita", "Follow-up", "Qualificazione", "Chiusura", "Custom"],
                    index=["Lead Nascita", "Follow-up", "Qualificazione", "Chiusura", "Custom"].index(sequence_data.get('type', 'Lead Nascita')) if sequence_data else 0,
                    help="Tipo di sequenza"
                )
            
            with col2:
                trigger_event = st.selectbox(
                    "Evento Trigger *",
                    options=["Lead Creato", "Lead Qualificato", "Proposta Inviata", "Follow-up Scaduto", "Manuale"],
                    index=["Lead Creato", "Lead Qualificato", "Proposta Inviata", "Follow-up Scaduto", "Manuale"].index(sequence_data.get('trigger_event', 'Lead Creato')) if sequence_data else 0,
                    help="Evento che attiva la sequenza"
                )
                
                is_active = st.checkbox(
                    "Sequenza Attiva",
                    value=sequence_data.get('is_active', True) if sequence_data else True,
                    help="Sequenza disponibile per l'uso"
                )
            
            # Condizioni
            st.markdown("### 🎯 Condizioni di Attivazione")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Filtri per categoria lead
                lead_categories = self.db.get_lead_categories()
                category_options = [cat['name'] for cat in lead_categories]
                selected_categories = st.multiselect(
                    "Categorie Lead",
                    options=category_options,
                    default=sequence_data.get('categories', []) if sequence_data else [],
                    help="Categorie lead che attivano la sequenza"
                )
                
                # Filtri per fonte lead
                lead_sources = self.db.get_lead_sources()
                source_options = [src['name'] for src in lead_sources]
                selected_sources = st.multiselect(
                    "Fonti Lead",
                    options=source_options,
                    default=sequence_data.get('sources', []) if sequence_data else [],
                    help="Fonti lead che attivano la sequenza"
                )
            
            with col2:
                # Filtri per priorità
                priority_options = ["Alta", "Media", "Bassa"]
                selected_priorities = st.multiselect(
                    "Priorità Lead",
                    options=priority_options,
                    default=sequence_data.get('priorities', []) if sequence_data else [],
                    help="Priorità lead che attivano la sequenza"
                )
                
                # Filtri per budget
                min_budget = st.number_input(
                    "Budget Minimo",
                    min_value=0,
                    value=sequence_data.get('min_budget', 0) if sequence_data else 0,
                    help="Budget minimo per attivare la sequenza"
                )
            
            # Passi della sequenza
            st.markdown("### 📋 Passi della Sequenza")
            
            if mode == "edit" and sequence_data:
                # Mostra passi esistenti
                steps = self.db.get_sequence_steps(sequence_data['id'])
                if steps:
                    st.markdown("**Passi esistenti:**")
                    for i, step in enumerate(steps, 1):
                        st.markdown(f"{i}. **{step['template_name']}** - Ritardo: {step['delay_hours']}h")
            
            # Aggiungi nuovo passo
            st.markdown("#### ➕ Aggiungi Passo")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Seleziona template
                templates = self.db.get_contact_templates()
                template_options = [f"{t['name']} ({t['type']})" for t in templates if t['is_active']]
                selected_template = st.selectbox(
                    "Template",
                    options=[""] + template_options,
                    index=0,
                    help="Template da utilizzare"
                )
            
            with col2:
                # Ritardo
                delay_hours = st.number_input(
                    "Ritardo (ore)",
                    min_value=0,
                    max_value=168,
                    value=24,
                    help="Ritardo prima dell'invio"
                )
            
            with col3:
                # Aggiungi passo
                if st.button("➕ Aggiungi Passo", use_container_width=True):
                    if selected_template:
                        # Estrai template ID dal nome
                        template_name = selected_template.split(" (")[0]
                        template = next((t for t in templates if t['name'] == template_name), None)
                        
                        if template:
                            step_data = {
                                'sequence_id': sequence_data['id'] if sequence_data else None,
                                'template_id': template['id'],
                                'delay_hours': delay_hours,
                                'order_index': 1  # Verrà aggiornato
                            }
                            
                            if self.db.add_sequence_step(step_data):
                                st.success(f"✅ Passo aggiunto: {template_name}")
                                st.rerun()
                            else:
                                st.error("❌ Errore nell'aggiunta del passo")
                        else:
                            st.error("❌ Template non trovato")
                    else:
                        st.error("❌ Seleziona un template")
            
            # Note
            notes = st.text_area(
                "Note",
                value=sequence_data.get('notes', '') if sequence_data else '',
                height=80,
                help="Note aggiuntive sulla sequenza"
            )
            
            # Pulsanti
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                submit_button = st.form_submit_button(
                    "💾 Salva Sequenza" if mode == "create" else "💾 Aggiorna Sequenza",
                    use_container_width=True
                )
            
            with col2:
                cancel_button = st.form_submit_button(
                    "❌ Annulla",
                    use_container_width=True
                )
            
            # Gestione submit
            if submit_button:
                if not name:
                    st.error("❌ Nome sequenza è obbligatorio!")
                    return None
                
                # Prepara i dati
                form_data = {
                    'name': name.strip(),
                    'type': sequence_type,
                    'trigger_event': trigger_event,
                    'categories': selected_categories,
                    'sources': selected_sources,
                    'priorities': selected_priorities,
                    'min_budget': min_budget,
                    'notes': notes.strip() if notes else None,
                    'is_active': is_active,
                    'created_by': self.current_user['user_id']
                }
                
                # Salva nel database
                if mode == "create":
                    sequence_id = self.db.create_contact_sequence(form_data)
                    if sequence_id:
                        st.success(f"✅ Sequenza '{name}' creata con successo!")
                        
                        # Log attività
                        self.db.log_activity(
                            user_id=self.current_user['user_id'],
                            action='create_sequence',
                            entity_type='contact_sequence',
                            entity_id=sequence_id,
                            details=f"Creata nuova sequenza: {name}"
                        )
                        
                        return sequence_id
                    else:
                        st.error("❌ Errore durante la creazione della sequenza")
                        return None
                
                else:  # mode == "edit"
                    if self.db.update_contact_sequence(sequence_data['id'], form_data):
                        st.success(f"✅ Sequenza '{name}' aggiornata con successo!")
                        
                        # Log attività
                        self.db.log_activity(
                            user_id=self.current_user['user_id'],
                            action='update_sequence',
                            entity_type='contact_sequence',
                            entity_id=sequence_data['id'],
                            details=f"Aggiornata sequenza: {name}"
                        )
                        
                        return sequence_data['id']
                    else:
                        st.error("❌ Errore durante l'aggiornamento della sequenza")
                        return None
            
            elif cancel_button:
                st.info("❌ Operazione annullata")
                return None
        
        return None
    
    def render_sequence_list(self):
        """Renderizza la lista delle sequenze"""
        
        sequences = self.db.get_contact_sequences()
        
        if not sequences:
            st.info("📭 Nessuna sequenza trovata")
            return
        
        # Converti in DataFrame
        df = pd.DataFrame(sequences)
        
        # Prepara le colonne per la visualizzazione
        if not df.empty:
            # Formatta le date
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y')
            
            # Formatta stato
            df['Stato'] = df['is_active'].apply(lambda x: "✅ Attiva" if x else "❌ Inattiva")
            
            # Combina categorie (gestisce campo mancante)
            if 'categories' in df.columns:
                df['Categorie'] = df['categories'].apply(lambda x: ", ".join(x) if x else "-")
            else:
                df['Categorie'] = "-"
        
        # Mostra la tabella
        st.markdown("### 📊 Lista Sequenze")
        
        if not df.empty:
            # Seleziona solo le colonne da mostrare
            display_columns = [
                'name', 'type', 'trigger_event', 'Categorie', 'Stato', 'created_at'
            ]
            
            # Filtra le colonne disponibili
            available_columns = [col for col in display_columns if col in df.columns]
            display_df = df[available_columns]
            
            # Rinomina le colonne
            column_mapping = {
                'name': '📞 Nome Sequenza',
                'type': '📋 Tipo',
                'trigger_event': '🎯 Trigger',
                'Categorie': '🏷️ Categorie',
                'Stato': '📈 Stato',
                'created_at': '📅 Creato'
            }
            
            display_df = display_df.rename(columns=column_mapping)
            
            # Mostra la tabella
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
    
    def render_sequence_stats(self):
        """Renderizza le statistiche delle sequenze"""
        
        stats = self.db.get_sequence_stats()
        
        st.markdown("### 📊 Statistiche Sequenze")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sequences = stats['total_sequences'][0]['count'] if stats['total_sequences'] else 0
            st.metric("📞 Sequenze Totali", total_sequences)
        
        with col2:
            active_sequences = stats['active_sequences'][0]['count'] if stats['active_sequences'] else 0
            st.metric("✅ Sequenze Attive", active_sequences)
        
        with col3:
            total_contacts = stats['total_contacts'][0]['count'] if stats['total_contacts'] else 0
            st.metric("📧 Contatti Inviati", total_contacts)
        
        with col4:
            success_rate = stats['success_rate'][0]['rate'] if stats['success_rate'] else 0
            st.metric("📈 Tasso Successo", f"{success_rate:.1f}%")
        
        # Sequenze per tipo
        st.markdown("#### 📋 Sequenze per Tipo")
        if stats['sequences_by_type']:
            type_df = pd.DataFrame(stats['sequences_by_type'])
            st.bar_chart(type_df.set_index('type')['count'])

def render_sequence_form_wrapper(sequence_data: Optional[Dict] = None, mode: str = "create"):
    """Wrapper per renderizzare il form sequenza"""
    sequence = ContactSequence()
    return sequence.render_sequence_form(sequence_data, mode)

def render_sequence_list_wrapper():
    """Wrapper per renderizzare la lista sequenze"""
    sequence = ContactSequence()
    sequence.render_sequence_list()

def render_sequence_stats_wrapper():
    """Wrapper per renderizzare le statistiche sequenze"""
    sequence = ContactSequence()
    sequence.render_sequence_stats()

# Test della classe
if __name__ == "__main__":
    st.set_page_config(
        page_title="Test Contact Sequence",
        page_icon="📞",
        layout="wide"
    )
    
    st.title("🧪 Test Contact Sequence")
    
    # Test form nuova sequenza
    st.markdown("### Test Form Nuova Sequenza")
    sequence_id = render_sequence_form_wrapper()
    
    if sequence_id:
        st.success(f"✅ Sequenza creata con ID: {sequence_id}")
        
        # Test lista sequenze
        st.markdown("### Test Lista Sequenze")
        render_sequence_list_wrapper()
        
        # Test statistiche
        st.markdown("### Test Statistiche")
        render_sequence_stats_wrapper()
