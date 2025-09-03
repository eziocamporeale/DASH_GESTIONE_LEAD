#!/usr/bin/env python3
"""
Componente Lead Table per DASH_GESTIONE_LEAD
Tabella per visualizzazione e gestione lead
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

class LeadTable:
    """Gestisce la tabella dei lead con filtri e azioni"""
    
    def __init__(self):
        """Inizializza la tabella lead"""
        self.db = DatabaseManager()
        self.current_user = get_current_user()
    
    def render_filters(self) -> Dict:
        """Renderizza i filtri per la tabella lead"""
        
        st.markdown("### 🔍 Filtri")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Filtro stato
            states = self.db.get_lead_states()
            state_options = ["Tutti"] + [state['name'] for state in states]
            selected_state = st.selectbox(
                "Stato",
                options=state_options,
                index=0
            )
        
        with col2:
            # Filtro categoria
            categories = self.db.get_lead_categories()
            category_options = ["Tutte"] + [cat['name'] for cat in categories]
            selected_category = st.selectbox(
                "Categoria",
                options=category_options,
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
            # Ricerca testuale
            search_term = st.text_input(
                "🔍 Ricerca",
                placeholder="Nome, email, azienda...",
                help="Cerca per nome, email, azienda o note"
            )
        
        # Preparazione filtri
        filters = {}
        
        if selected_state != "Tutti":
            state_id = next((state['id'] for state in states if state['name'] == selected_state), None)
            if state_id:
                filters['state_id'] = state_id
        
        if selected_category != "Tutte":
            category_id = next((cat['id'] for cat in categories if cat['name'] == selected_category), None)
            if category_id:
                filters['category_id'] = category_id
        
        if selected_user != "Tutti":
            user_id = next((user['id'] for user in users if f"{user['first_name']} {user['last_name']}" == selected_user), None)
            if user_id:
                filters['assigned_to'] = user_id
        
        if search_term:
            filters['search'] = search_term
        
        return filters
    
    def render_lead_table(self, filters: Dict = None, page_size: int = 20):
        """Renderizza la tabella dei lead"""
        
        # Ottieni i lead dal database
        leads = self.db.get_leads(filters=filters, limit=page_size)
        
        if not leads:
            st.info("📭 Nessun lead trovato con i filtri selezionati")
            return
        
        # Converti in DataFrame
        df = pd.DataFrame(leads)
        
        # Prepara le colonne per la visualizzazione
        if not df.empty:
            # Formatta le date
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y')
            
            if 'expected_close_date' in df.columns:
                df['expected_close_date'] = pd.to_datetime(df['expected_close_date']).dt.strftime('%d/%m/%Y')
            
            # Formatta il budget
            if 'budget' in df.columns:
                df['budget'] = df['budget'].apply(lambda x: f"€{x:,.2f}" if x and x > 0 else "-")
            
            # Combina nome e cognome (gestisce sia formato Supabase che SQLite)
            if 'first_name' in df.columns and 'last_name' in df.columns:
                df['Nome Completo'] = df['first_name'].fillna('') + ' ' + df['last_name'].fillna('')
            elif 'name' in df.columns:
                df['Nome Completo'] = df['name'].fillna('')
            else:
                df['Nome Completo'] = 'Nome non disponibile'
            
            # Combina assigned user
            df['Assegnato a'] = df.apply(
                lambda row: f"{row['assigned_first_name']} {row['assigned_last_name']}" 
                if row['assigned_first_name'] and row['assigned_last_name'] else "-", 
                axis=1
            )
        
        # Mostra statistiche
        st.markdown(f"### 📊 Risultati ({len(leads)} lead trovati)")
        
        # Tabella con stile
        if not df.empty:
            # Seleziona solo le colonne da mostrare
            display_columns = [
                'Nome Completo', 'email', 'company', 'state_name', 
                'category_name', 'priority_name', 'Assegnato a', 
                'budget', 'expected_close_date', 'created_at'
            ]
            
            # Filtra le colonne disponibili
            available_columns = [col for col in display_columns if col in df.columns]
            display_df = df[available_columns]
            
            # Rinomina le colonne per una migliore visualizzazione
            column_mapping = {
                'Nome Completo': '👤 Nome',
                'email': '📧 Email',
                'company': '🏢 Azienda',
                'state_name': '📈 Stato',
                'category_name': '🏷️ Categoria',
                'priority_name': '⚡ Priorità',
                'Assegnato a': '👥 Assegnato',
                'budget': '💰 Budget',
                'expected_close_date': '📅 Chiusura',
                'created_at': '📅 Creato'
            }
            
            display_df = display_df.rename(columns=column_mapping)
            
            # Mostra la tabella
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Azioni sui lead
            self.render_lead_actions(df)
    
    def render_lead_actions(self, df: pd.DataFrame):
        """Renderizza le azioni sui lead"""
        
        st.markdown("### ⚡ Azioni Rapide")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📝 Nuovo Lead", use_container_width=True):
                st.session_state['show_lead_form'] = True
                st.session_state['lead_form_mode'] = 'create'
                st.rerun()
        
        with col2:
            if st.button("📊 Export Excel", use_container_width=True):
                self.export_to_excel(df)
        
        with col3:
            if st.button("📈 Analytics", use_container_width=True):
                st.session_state['show_lead_analytics'] = True
                st.rerun()
        
        with col4:
            if st.button("🔄 Aggiorna", use_container_width=True):
                st.rerun()
    
    def render_lead_details(self, lead_id: int):
        """Renderizza i dettagli di un lead specifico"""
        
        lead = self.db.get_lead(lead_id)
        if not lead:
            st.error("❌ Lead non trovato")
            return
        
        st.markdown(f"## 👤 Dettagli Lead: {lead['first_name']} {lead['last_name']}")
        
        # Informazioni principali
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Informazioni Base")
            st.markdown(f"**Nome:** {lead['first_name']} {lead['last_name']}")
            st.markdown(f"**Email:** {lead['email'] or 'Non specificato'}")
            st.markdown(f"**Telefono:** {lead['phone'] or 'Non specificato'}")
            st.markdown(f"**Azienda:** {lead['company'] or 'Non specificato'}")
            st.markdown(f"**Posizione:** {lead['position'] or 'Non specificato'}")
        
        with col2:
            st.markdown("### 🏷️ Classificazione")
            st.markdown(f"**Stato:** {lead['state_name']}")
            st.markdown(f"**Categoria:** {lead['category_name']}")
            st.markdown(f"**Priorità:** {lead['priority_name']}")
            st.markdown(f"**Fonte:** {lead['source_name']}")
            st.markdown(f"**Assegnato a:** {lead['assigned_first_name']} {lead['assigned_last_name']}" if lead['assigned_first_name'] else "**Assegnato a:** Non assegnato")
        
        # Informazioni aggiuntive
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💰 Informazioni Commerciali")
            budget = f"€{lead['budget']:,.2f}" if lead['budget'] else "Non specificato"
            st.markdown(f"**Budget:** {budget}")
            st.markdown(f"**Data chiusura prevista:** {lead['expected_close_date'] or 'Non specificato'}")
        
        with col2:
            st.markdown("### 📅 Date")
            st.markdown(f"**Creato il:** {lead['created_at']}")
            st.markdown(f"**Aggiornato il:** {lead['updated_at']}")
            st.markdown(f"**Creato da:** {lead['created_first_name']} {lead['created_last_name']}")
        
        # Note
        if lead['notes']:
            st.markdown("### 📝 Note")
            st.text_area("Note del lead", value=lead['notes'], height=100, disabled=True)
        
        # Azioni
        st.markdown("### ⚡ Azioni")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✏️ Modifica", key=f"edit_{lead_id}"):
                st.session_state['show_lead_form'] = True
                st.session_state['lead_form_mode'] = 'edit'
                st.session_state['edit_lead_data'] = lead
                st.rerun()
        
        with col2:
            if st.button("✅ Creare Task", key=f"task_{lead_id}"):
                st.session_state['create_task_for_lead'] = lead_id
                st.rerun()
        
        with col3:
            if st.button("🗑️ Elimina", key=f"delete_{lead_id}"):
                if st.confirm(f"Sei sicuro di voler eliminare il lead {lead['first_name']} {lead['last_name']}?"):
                    if self.db.delete_lead(lead_id):
                        st.success("✅ Lead eliminato con successo!")
                        st.rerun()
                    else:
                        st.error("❌ Errore durante l'eliminazione")
    
    def export_to_excel(self, df: pd.DataFrame):
        """Esporta i lead in Excel"""
        try:
            # Prepara i dati per l'export
            export_df = df.copy()
            
            # Rinomina le colonne
            column_mapping = {
                'first_name': 'Nome',
                'last_name': 'Cognome',
                'email': 'Email',
                'phone': 'Telefono',
                'company': 'Azienda',
                'position': 'Posizione',
                'state_name': 'Stato',
                'category_name': 'Categoria',
                'priority_name': 'Priorità',
                'source_name': 'Fonte',
                'budget': 'Budget',
                'expected_close_date': 'Data Chiusura Prevista',
                'created_at': 'Data Creazione',
                'notes': 'Note'
            }
            
            export_df = export_df.rename(columns=column_mapping)
            
            # Crea il file Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"leads_export_{timestamp}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                export_df.to_excel(writer, sheet_name='Leads', index=False)
            
            # Download del file
            with open(filename, 'rb') as f:
                st.download_button(
                    label="📥 Scarica Excel",
                    data=f.read(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.success(f"✅ Export completato: {filename}")
            
        except Exception as e:
            st.error(f"❌ Errore durante l'export: {e}")

def render_lead_table_wrapper():
    """Wrapper per renderizzare la tabella lead"""
    table = LeadTable()
    
    # Filtri
    filters = table.render_filters()
    
    # Tabella
    table.render_lead_table(filters)

# Test della classe
if __name__ == "__main__":
    st.set_page_config(
        page_title="Test Lead Table",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("🧪 Test Lead Table")
    
    # Test tabella lead
    render_lead_table_wrapper()
