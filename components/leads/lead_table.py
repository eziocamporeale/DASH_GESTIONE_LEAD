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
        
        # Sezione filtri collassabile
        with st.expander("🔍 Filtri", expanded=st.session_state.get('filters_expanded', True)):
            # Salva lo stato dell'expander
            st.session_state['filters_expanded'] = True
        
            # Layout migliorato con 3 colonne come nella Dashboard CPA
            col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
            
            with col_filtro1:
                # Filtro stato
                states = self.db.get_lead_states()
                state_options = ["Tutti"] + [state['name'] for state in states]
                selected_state = st.selectbox(
                    "📈 Stato",
                    options=state_options,
                    index=0,
                    help="Filtra per stato del lead"
                )
            
            with col_filtro2:
                # Filtro categoria
                categories = self.db.get_lead_categories()
                category_options = ["Tutte"] + [cat['name'] for cat in categories]
                selected_category = st.selectbox(
                    "🏷️ Categoria",
                    options=category_options,
                    index=0,
                    help="Filtra per categoria del lead"
                )
            
            with col_filtro3:
                # Filtro priorità
                priorities = self.db.get_lead_priorities()
                priority_options = ["Tutte"] + [priority['name'] for priority in priorities]
                selected_priority = st.selectbox(
                    "⚡ Priorità",
                    options=priority_options,
                    index=0,
                    help="Filtra per priorità del lead"
                )
            
            # Seconda riga di filtri
            col_filtro4, col_filtro5, col_filtro6 = st.columns(3)
            
            with col_filtro4:
                # Filtro assegnato a
                users = self.db.get_all_users()
                user_options = ["Tutti"] + [f"{user['first_name']} {user['last_name']}" for user in users]
                selected_user = st.selectbox(
                    "👥 Assegnato a",
                    options=user_options,
                    index=0,
                    help="Filtra per utente assegnato"
                )
            
            with col_filtro5:
                # Filtro fonte
                sources = self.db.get_lead_sources()
                source_options = ["Tutte"] + [source['name'] for source in sources]
                selected_source = st.selectbox(
                    "🔗 Fonte",
                    options=source_options,
                    index=0,
                    help="Filtra per fonte del lead"
                )
            
            with col_filtro6:
                # Filtro azienda
                companies = self.db.get_leads(filters={}, limit=1000)  # Ottieni lead per estrarre aziende
                company_list = list(set([lead.get('company', '') for lead in companies if lead.get('company')]))
                company_options = ["Tutte"] + sorted(company_list)
                selected_company = st.selectbox(
                    "🏢 Azienda",
                    options=company_options,
                    index=0,
                    help="Filtra per azienda"
                )
            
            # Filtro di ricerca testuale migliorato
            st.markdown("---")
            search_term = st.text_input(
                "🔍 Ricerca Avanzata",
                placeholder="Nome, email, azienda, note...",
                help="Cerca nei campi nome, email, azienda e note del lead"
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
            
            if selected_priority != "Tutte":
                priority_id = next((priority['id'] for priority in priorities if priority['name'] == selected_priority), None)
                if priority_id:
                    filters['priority_id'] = priority_id
            
            if selected_user != "Tutti":
                user_id = next((user['id'] for user in users if f"{user['first_name']} {user['last_name']}" == selected_user), None)
                if user_id:
                    filters['assigned_to'] = user_id
            
            if selected_source != "Tutte":
                source_id = next((source['id'] for source in sources if source['name'] == selected_source), None)
                if source_id:
                    filters['source_id'] = source_id
            
            if selected_company != "Tutte":
                filters['company'] = selected_company
            
            if search_term:
                filters['search'] = search_term
            
            return filters
    
    def render_lead_table(self, filters: Dict = None, page_size: int = 20):
        """Renderizza la tabella dei lead"""
        
        # Ottieni il conteggio totale dei lead (senza limite)
        total_leads = self.db.get_leads(filters=filters, limit=10000)  # Limite alto per conteggio
        total_count = len(total_leads)
        
        # Ottieni i lead dal database per la visualizzazione
        leads = self.db.get_leads(filters=filters, limit=page_size)
        
        # Applica filtraggio per ruolo Tester
        if self.current_user and self.current_user.get('role_name') == 'Tester':
            leads = self.db.filter_sensitive_data_for_tester(leads, 'lead')
            st.info("🔒 **Modalità Tester**: I dati sensibili sono stati mascherati per proteggere la privacy dei clienti")
        
        if not leads:
            st.info("📭 Nessun lead trovato con i filtri selezionati")
            # Mostra comunque le azioni rapide anche quando non ci sono lead
            self.render_lead_actions_empty()
            return
        
        # Mostra il conteggio corretto
        if total_count > page_size:
            st.info(f"📊 **Risultati ({total_count} lead trovati)** - Mostrando i primi {page_size}")
        else:
            st.info(f"📊 **Risultati ({total_count} lead trovati)**")
        
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
        
        # Sezione risultati collassabile
        with st.expander(f"📊 Risultati ({len(leads)} lead trovati)", expanded=st.session_state.get('results_expanded', True)):
            # Salva lo stato dell'expander
            st.session_state['results_expanded'] = True
            
            # Tabella con stile
            if not df.empty:
                # Seleziona solo le colonne da mostrare
                display_columns = [
                    'Nome Completo', 'email', 'phone', 'company', 'state_name', 
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
                    'phone': '📞 Telefono',
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
                
                # Mostra la tabella con configurazione colonne avanzata
                st.dataframe(
                    display_df,
                    width='stretch',
                    hide_index=True,
                    height=400,  # Altezza fissa per compattezza
                    column_config={
                        "👤 Nome": st.column_config.TextColumn("Nome", width=150),
                        "📧 Email": st.column_config.TextColumn("Email", width=180),
                        "📞 Telefono": st.column_config.TextColumn("Telefono", width=120),
                        "🏢 Azienda": st.column_config.TextColumn("Azienda", width=120),
                        "📈 Stato": st.column_config.TextColumn("Stato", width=100),
                        "🏷️ Categoria": st.column_config.TextColumn("Categoria", width=100),
                        "⚡ Priorità": st.column_config.TextColumn("Priorità", width=80),
                        "👥 Assegnato": st.column_config.TextColumn("Assegnato", width=120),
                        "💰 Budget": st.column_config.TextColumn("Budget", width=100),
                        "📅 Chiusura": st.column_config.TextColumn("Chiusura", width=100),
                        "📅 Creato": st.column_config.TextColumn("Creato", width=100)
                    }
                )
                
                # Aggiungi pulsanti di azione sotto la tabella
                st.markdown("### ⚡ Azioni Rapide sui Lead")
                
                # Controlla i permessi dell'utente
                can_edit = self.current_user and self.current_user.get('role_name') != 'Tester'
                can_delete = self.current_user and self.current_user.get('role_name') != 'Tester'
                can_create = self.current_user and self.current_user.get('role_name') != 'Tester'
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if can_edit:
                        if st.button("✏️ Modifica Lead Selezionato", use_container_width=True):
                            st.info("👆 Seleziona un lead nella sezione 'Dettagli Lead' qui sotto per modificarlo")
                    else:
                        st.button("✏️ Modifica Lead Selezionato", disabled=True, 
                                 help="Non disponibile per il ruolo Tester", use_container_width=True)
                
                with col2:
                    if can_create:
                        if st.button("📝 Nuovo Lead", use_container_width=True):
                            st.session_state['show_lead_form'] = True
                            st.session_state['lead_form_mode'] = 'create'
                            st.rerun()
                    else:
                        st.button("📝 Nuovo Lead", disabled=True, 
                                 help="Non disponibile per il ruolo Tester", use_container_width=True)
                
                with col3:
                    if can_delete:
                        if st.button("🗑️ Elimina Lead Selezionato", use_container_width=True):
                            st.info("👆 Seleziona un lead nella sezione 'Dettagli Lead' qui sotto per eliminarlo")
                    else:
                        st.button("🗑️ Elimina Lead Selezionato", disabled=True, 
                                 help="Non disponibile per il ruolo Tester", use_container_width=True)
                
                # Messaggio informativo per Tester
                if not can_edit and not can_delete and not can_create:
                    st.info("🔒 **Modalità Tester**: Le azioni di modifica, creazione e eliminazione sono disabilitate per proteggere i dati")
                
                # Dettagli lead selezionato (come nella Dashboard CPA)
                self.render_lead_details_section(df)
                
                # Azioni sui lead (usa il DataFrame originale con tutti i dati)
                self.render_lead_actions(df)
    
    def render_lead_details_section(self, df: pd.DataFrame):
        """Renderizza la sezione dettagli lead selezionato (come nella Dashboard CPA)"""
        
        if df.empty:
            return
        
        # Sezione dettagli lead collassabile
        with st.expander("👤 Dettagli Lead", expanded=st.session_state.get('details_expanded', False)):
            # Salva lo stato dell'expander
            st.session_state['details_expanded'] = True
        
            # Selezione lead per visualizzare i dettagli
            lead_names = []
            for _, row in df.iterrows():
                if 'first_name' in row and 'last_name' in row:
                    name = f"{row['first_name']} {row['last_name']}".strip()
                elif 'name' in row:
                    name = row['name']
                else:
                    name = f"Lead ID {row.get('id', 'N/A')}"
                lead_names.append(name)
            
            if not lead_names:
                st.info("Nessun lead disponibile per i dettagli")
                return
            
            lead_selezionato = st.selectbox(
                "Seleziona un lead per visualizzare i dettagli completi:",
                options=lead_names,
                index=0
            )
        
            if lead_selezionato:
                # Trova il lead selezionato
                lead_dettagli = None
                for _, row in df.iterrows():
                    if 'first_name' in row and 'last_name' in row:
                        name = f"{row['first_name']} {row['last_name']}".strip()
                    elif 'name' in row:
                        name = row['name']
                    else:
                        name = f"Lead ID {row.get('id', 'N/A')}"
                    
                    if name == lead_selezionato:
                        lead_dettagli = row
                        break
                
                if lead_dettagli is not None:
                    # Applica filtraggio per ruolo Tester anche ai dettagli
                    if self.current_user and self.current_user.get('role_name') == 'Tester':
                        lead_dettagli = self.db.filter_sensitive_data_for_tester([lead_dettagli], 'lead')[0]
                    
                    # Mostra dettagli completi in due colonne
                    col_det1, col_det2 = st.columns(2)
                    
                    with col_det1:
                        st.markdown("**📋 Informazioni Base**")
                        st.write(f"**Nome:** {lead_dettagli.get('first_name', '')} {lead_dettagli.get('last_name', '')}")
                        st.write(f"**Email:** {lead_dettagli.get('email', 'Non specificato')}")
                        st.write(f"**Telefono:** {lead_dettagli.get('phone', 'Non specificato')}")
                        st.write(f"**Azienda:** {lead_dettagli.get('company', 'Non specificato')}")
                        st.write(f"**Posizione:** {lead_dettagli.get('position', 'Non specificato')}")
                    
                    with col_det2:
                        st.markdown("**📊 Informazioni Commerciali**")
                        st.write(f"**Stato:** {lead_dettagli.get('state_name', 'Non specificato')}")
                        st.write(f"**Categoria:** {lead_dettagli.get('category_name', 'Non specificato')}")
                        st.write(f"**Priorità:** {lead_dettagli.get('priority_name', 'Non specificato')}")
                        st.write(f"**Fonte:** {lead_dettagli.get('source_name', 'Non specificato')}")
                        st.write(f"**Assegnato a:** {lead_dettagli.get('assigned_first_name', '')} {lead_dettagli.get('assigned_last_name', '')}")
                    
                    # Informazioni aggiuntive
                    col_det3, col_det4 = st.columns(2)
                    
                    with col_det3:
                        st.markdown("**💰 Informazioni Finanziarie**")
                        budget = lead_dettagli.get('budget')
                        if budget and str(budget).strip() and str(budget).strip() != 'nan':
                            try:
                                budget_num = float(budget)
                                if budget_num > 0:
                                    st.write(f"**Budget:** €{budget_num:,.2f}")
                                else:
                                    st.write("**Budget:** Non specificato")
                            except (ValueError, TypeError):
                                st.write("**Budget:** Non specificato")
                        else:
                            st.write("**Budget:** Non specificato")
                        
                        expected_close = lead_dettagli.get('expected_close_date')
                        if expected_close:
                            try:
                                close_date = pd.to_datetime(expected_close).strftime('%d/%m/%Y')
                                st.write(f"**Data Chiusura Prevista:** {close_date}")
                            except:
                                st.write("**Data Chiusura Prevista:** Non specificato")
                        else:
                            st.write("**Data Chiusura Prevista:** Non specificato")
                    
                    with col_det4:
                        st.markdown("**📅 Informazioni Sistema**")
                        created_at = lead_dettagli.get('created_at')
                        if created_at:
                            try:
                                created_date = pd.to_datetime(created_at).strftime('%d/%m/%Y %H:%M')
                                st.write(f"**Creato il:** {created_date}")
                            except:
                                st.write("**Creato il:** Non specificato")
                        else:
                            st.write("**Creato il:** Non specificato")
                        
                        updated_at = lead_dettagli.get('updated_at')
                        if updated_at:
                            try:
                                updated_date = pd.to_datetime(updated_at).strftime('%d/%m/%Y %H:%M')
                                st.write(f"**Modificato il:** {updated_date}")
                            except:
                                st.write("**Modificato il:** Non specificato")
                        else:
                            st.write("**Modificato il:** Non specificato")
                    
                    # Note
                    notes = lead_dettagli.get('notes')
                    if notes and str(notes).strip():
                        st.markdown("**📝 Note**")
                        st.info(notes)
    
    def render_lead_actions_empty(self):
        """Renderizza le azioni rapide quando non ci sono lead"""
        
        st.markdown("### ⚡ Azioni Rapide")
        
        # Controlla i permessi dell'utente
        can_create = self.current_user and self.current_user.get('role_name') != 'Tester'
        
        col_azione1, col_azione2, col_azione3 = st.columns(3)
        
        with col_azione1:
            if can_create:
                if st.button("📝 Nuovo Lead", help="Crea un nuovo lead"):
                    st.session_state['show_lead_form'] = True
                    st.session_state['lead_form_mode'] = 'create'
                    st.rerun()
            else:
                st.button("📝 Nuovo Lead", disabled=True, help="Non disponibile per il ruolo Tester")
        
        with col_azione2:
            st.button("📊 Esporta", disabled=True, help="Nessun dato da esportare")
        
        with col_azione3:
            if st.button("🔄 Aggiorna", help="Aggiorna i dati dalla tabella"):
                st.rerun()
    
    def render_lead_actions(self, df: pd.DataFrame):
        """Renderizza le azioni sui lead con layout migliorato"""
        
        st.markdown("### ⚡ Azioni Rapide")
        
        # Controlla i permessi dell'utente
        can_export = self.current_user and self.current_user.get('role_name') != 'Tester'
        
        col_azione1, col_azione2, col_azione3 = st.columns(3)
        
        with col_azione1:
            if can_export:
                if st.button("📊 Esporta", help="Esporta i dati filtrati in formato CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="💾 CSV",
                        data=csv,
                        file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.button("📊 Esporta", disabled=True, help="Non disponibile per il ruolo Tester")
        
        with col_azione2:
            if st.button("🔄 Aggiorna", help="Aggiorna i dati dalla tabella"):
                st.rerun()
        
        with col_azione3:
            if st.button("📈 Grafici", help="Mostra grafici riassuntivi"):
                st.session_state.show_lead_charts = True
                st.rerun()
        
        # Azioni sui lead (solo quando si seleziona un lead)
        if len(df) > 0:
            st.markdown("### ⚡ Azioni sui Lead")
            st.info("💡 **Seleziona un lead dalla sezione 'Dettagli Lead' per visualizzare le azioni disponibili**")
        
        # Azioni aggiuntive
        col_azione4, col_azione5 = st.columns(2)
        
        with col_azione4:
            if st.button("📝 Nuovo Lead", help="Crea un nuovo lead"):
                st.session_state['show_lead_form'] = True
                st.session_state['lead_form_mode'] = 'create'
                st.rerun()
        
        with col_azione5:
            if st.button("📊 Analytics", help="Mostra analytics avanzate"):
                st.session_state['show_lead_analytics'] = True
                st.rerun()
    
    def render_lead_details(self, lead_id: int):
        """Renderizza i dettagli di un lead specifico"""
        
        lead = self.db.get_lead(lead_id)
        if not lead:
            st.error("❌ Lead non trovato")
            return
        
        # Gestisce sia formato Supabase (name) che SQLite (first_name + last_name)
        if 'name' in lead and lead['name']:
            lead_name = lead['name']
        elif 'first_name' in lead and 'last_name' in lead:
            lead_name = f"{lead['first_name']} {lead['last_name']}"
        else:
            lead_name = f"Lead ID {lead_id}"
        
        st.markdown(f"## 👤 Dettagli Lead: {lead_name}")
        
        # Informazioni principali
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Informazioni Base")
            st.markdown(f"**Nome:** {lead_name}")
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
            # Gestisce il nome dell'utente assegnato
            if 'assigned_first_name' in lead and 'assigned_last_name' in lead and lead['assigned_first_name']:
                assigned_name = f"{lead['assigned_first_name']} {lead['assigned_last_name']}"
            else:
                assigned_name = "Non assegnato"
            st.markdown(f"**Assegnato a:** {assigned_name}")
        
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
            # Gestisce il nome dell'utente creatore
            if 'created_first_name' in lead and 'created_last_name' in lead and lead['created_first_name']:
                created_name = f"{lead['created_first_name']} {lead['created_last_name']}"
            else:
                created_name = "Sistema"
            st.markdown(f"**Creato da:** {created_name}")
        
        # Note
        if lead['notes']:
            st.markdown("### 📝 Note")
            st.text_area("Note del lead", value=lead['notes'], height=100, disabled=True)
        
        # Separatore visivo
        st.markdown("---")
        
        # Azioni - SEMPRE VISIBILI
        st.markdown("### ⚡ Azioni")
        
        # Controlla i permessi dell'utente
        can_edit = self.current_user and self.current_user.get('role_name') != 'Tester'
        can_delete = self.current_user and self.current_user.get('role_name') != 'Tester'
        
        # Mostra sempre i pulsanti, anche se disabilitati per Tester
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if can_edit:
                if st.button("✏️ Modifica Lead", key=f"edit_{lead_id}", use_container_width=True):
                    st.session_state['show_lead_form'] = True
                    st.session_state['lead_form_mode'] = 'edit'
                    st.session_state['edit_lead_data'] = lead
                    st.rerun()
            else:
                st.button("✏️ Modifica Lead", key=f"edit_{lead_id}", disabled=True, 
                         help="Non disponibile per il ruolo Tester", use_container_width=True)
        
        with col2:
            if st.button("✅ Creare Task", key=f"task_{lead_id}", use_container_width=True):
                st.session_state['create_task_for_lead'] = lead_id
                st.rerun()
        
        with col3:
            if can_delete:
                if st.button("🗑️ Elimina Lead", key=f"delete_{lead_id}", use_container_width=True):
                    # Gestisce sia formato Supabase (name) che SQLite (first_name + last_name)
                    if 'name' in lead and lead['name']:
                        lead_name = lead['name']
                    elif 'first_name' in lead and 'last_name' in lead:
                        lead_name = f"{lead['first_name']} {lead['last_name']}"
                    else:
                        lead_name = f"Lead ID {lead_id}"
                    
                    if st.confirm(f"Sei sicuro di voler eliminare il lead {lead_name}?"):
                        if self.db.delete_lead(lead_id):
                            st.success("✅ Lead eliminato con successo!")
                            st.rerun()
                        else:
                            st.error("❌ Errore durante l'eliminazione")
            else:
                st.button("🗑️ Elimina Lead", key=f"delete_{lead_id}", disabled=True, 
                         help="Non disponibile per il ruolo Tester", use_container_width=True)
        
        # Messaggio informativo per Tester
        if not can_edit and not can_delete:
            st.info("🔒 **Modalità Tester**: Le azioni di modifica e eliminazione sono disabilitate per proteggere i dati")
    
    def show_delete_lead_modal(self, df: pd.DataFrame):
        """Mostra il modal per eliminare lead selezionati"""
        
        # Controlla i permessi dell'utente
        can_delete = self.current_user and self.current_user.get('role_name') != 'Tester'
        
        if not can_delete:
            st.info("🔒 **Modalità Tester**: L'eliminazione di lead non è disponibile per proteggere i dati")
            return
        
        st.markdown("### 🗑️ Elimina Lead")
        st.markdown("Seleziona i lead da eliminare:")
        
        # Verifica che il DataFrame abbia le colonne necessarie
        if 'id' not in df.columns:
            st.error("❌ Errore: colonna 'id' non trovata nel DataFrame")
            st.write("Colonne disponibili:", list(df.columns))
            return
        
        # Gestisce sia formato Supabase (name) che SQLite (first_name + last_name)
        if 'name' in df.columns:
            # Formato Supabase: usa la colonna 'name'
            name_column = 'name'
        elif 'first_name' in df.columns and 'last_name' in df.columns:
            # Formato SQLite: combina first_name + last_name
            name_column = 'combined'
        else:
            st.error("❌ Errore: colonne nome non trovate (né 'name' né 'first_name'/'last_name')")
            st.write("Colonne disponibili:", list(df.columns))
            return
        
        # Crea una lista di lead con checkbox
        selected_leads = []
        
        for index, row in df.iterrows():
            lead_id = row['id']
            
            # Determina il nome del lead
            if name_column == 'name':
                lead_name = row['name']
            else:
                lead_name = f"{row['first_name']} {row['last_name']}"
            
            lead_company = row['company'] or 'N/A'
            
            # Checkbox per selezionare il lead
            if st.checkbox(
                f"🗑️ {lead_name} - {lead_company}",
                key=f"delete_lead_{lead_id}",
                help=f"Seleziona per eliminare {lead_name}"
            ):
                selected_leads.append({
                    'id': lead_id,
                    'name': lead_name,
                    'company': lead_company
                })
        
        # Pulsante per confermare l'eliminazione
        if selected_leads:
            st.markdown(f"**Lead selezionati per eliminazione: {len(selected_leads)}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Conferma Eliminazione", type="primary", use_container_width=True):
                    self.delete_selected_leads(selected_leads)
            
            with col2:
                if st.button("❌ Annulla", use_container_width=True):
                    st.rerun()
        else:
            st.info("ℹ️ Seleziona almeno un lead per eliminare")
    
    def delete_selected_leads(self, selected_leads: List[Dict]):
        """Elimina i lead selezionati"""
        
        # Controlla i permessi dell'utente
        can_delete = self.current_user and self.current_user.get('role_name') != 'Tester'
        
        if not can_delete:
            st.error("🔒 **Accesso Negato**: Il ruolo Tester non può eliminare lead per proteggere i dati")
            return
        
        if not selected_leads:
            st.warning("⚠️ Nessun lead selezionato")
            return
        
        # Conferma finale
        lead_names = [lead['name'] for lead in selected_leads]
        confirm_text = f"Sei sicuro di voler eliminare {len(selected_leads)} lead?\n\n"
        confirm_text += "\n".join([f"• {name}" for name in lead_names])
        
        if st.confirm(confirm_text):
            success_count = 0
            error_count = 0
            
            # Elimina ogni lead
            for lead in selected_leads:
                try:
                    if self.db.delete_lead(lead['id']):
                        success_count += 1
                        st.success(f"✅ Eliminato: {lead['name']}")
                    else:
                        error_count += 1
                        st.error(f"❌ Errore eliminazione: {lead['name']}")
                except Exception as e:
                    error_count += 1
                    st.error(f"❌ Errore eliminazione {lead['name']}: {e}")
            
            # Riepilogo finale
            if success_count > 0:
                st.success(f"✅ Eliminazione completata: {success_count} lead eliminati")
                if error_count > 0:
                    st.warning(f"⚠️ {error_count} lead non eliminati per errori")
                st.rerun()
            else:
                st.error("❌ Nessun lead eliminato")
    
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
    
    # Tabella - Mostra tutti i lead (limite aumentato a 1000)
    table.render_lead_table(filters, page_size=1000)

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
