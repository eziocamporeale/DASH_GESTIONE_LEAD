#!/usr/bin/env python3
"""
Portal Manager per DASH_GESTIONE_LEAD
Gestione completa dei portali web generati
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import json
import os
from pathlib import Path

class PortalManager:
    """Gestore principale per i portali web generati"""
    
    def __init__(self, db_manager):
        """Inizializza il gestore portali"""
        self.db = db_manager
        self.setup_session_state()
        self.setup_portal_types()
        self.setup_sectors()
        # Storage temporaneo fino a quando Supabase non riconosce le tabelle
        self.temp_storage_file = Path(__file__).parent / "temp_portals.json"
        self.load_temp_storage()
    
    def setup_session_state(self):
        """Inizializza lo stato della sessione"""
        if 'portals_editing' not in st.session_state:
            st.session_state.portals_editing = None
        if 'portals_show_form' not in st.session_state:
            st.session_state.portals_show_form = False
        if 'portals_filter_type' not in st.session_state:
            st.session_state.portals_filter_type = "Tutti"
        if 'portals_filter_sector' not in st.session_state:
            st.session_state.portals_filter_sector = "Tutti"
        if 'portals_filter_status' not in st.session_state:
            st.session_state.portals_filter_status = "Tutti"
    
    def setup_portal_types(self):
        """Definisce i tipi di portali disponibili"""
        self.portal_types = {
            "landing_page": "🎯 Landing Page",
            "business_website": "🏢 Sito Aziendale", 
            "ecommerce": "🛒 E-commerce",
            "portfolio": "💼 Portfolio",
            "blog": "📝 Blog",
            "dashboard": "📊 Dashboard",
            "saas": "⚙️ SaaS Platform"
        }
    
    def setup_sectors(self):
        """Definisce i settori disponibili"""
        self.sectors = {
            "finanza": "💰 Finanza",
            "immobiliare": "🏠 Immobiliare",
            "ecommerce": "🛒 E-commerce",
            "consulenza": "💼 Consulenza",
            "tech": "💻 Tecnologia",
            "salute": "🏥 Salute",
            "educazione": "🎓 Educazione",
            "marketing": "📢 Marketing",
            "altro": "🔧 Altro"
        }
    
    def load_temp_storage(self):
        """Carica i dati dal storage temporaneo"""
        try:
            if self.temp_storage_file.exists():
                with open(self.temp_storage_file, 'r', encoding='utf-8') as f:
                    self.temp_portals = json.load(f)
            else:
                self.temp_portals = []
        except Exception as e:
            st.error(f"❌ Errore caricamento storage temporaneo: {e}")
            self.temp_portals = []
    
    def save_temp_storage(self):
        """Salva i dati nel storage temporaneo"""
        try:
            with open(self.temp_storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.temp_portals, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"❌ Errore salvataggio storage temporaneo: {e}")
    
    def render_portals_page(self):
        """Rende la pagina principale dei portali"""
        st.header("🌐 Generatore Portali Web")
        st.markdown("Crea portali web dedicati per i tuoi progetti di riferimento")
        
        # Statistiche
        self.render_stats()
        
        # Filtri
        self.render_filters()
        
        # Azioni rapide
        self.render_quick_actions()
        
        # Form per aggiungere/modificare
        if st.session_state.portals_show_form:
            self.render_portal_form()
        
        # Tabella dei portali
        self.render_portals_table()
    
    def render_stats(self):
        """Rende le statistiche dei portali"""
        try:
            stats = self.get_portals_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="🌐 Totale Portali",
                    value=stats.get('total_portals', 0),
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="✅ Portali Attivi",
                    value=stats.get('active_portals', 0),
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="🚀 Portali Deployati",
                    value=stats.get('deployed_portals', 0),
                    delta=None
                )
            
            with col4:
                deployment_percentage = 0
                if stats.get('total_portals', 0) > 0:
                    deployment_percentage = round((stats.get('deployed_portals', 0) / stats.get('total_portals', 1)) * 100, 1)
                
                st.metric(
                    label="📈 % Deployati",
                    value=f"{deployment_percentage}%",
                    delta=None
                )
                
        except Exception as e:
            st.error(f"❌ Errore caricamento statistiche: {e}")
    
    def render_filters(self):
        """Rende i filtri per i portali"""
        st.subheader("🔍 Filtri")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_type = st.selectbox(
                "Tipo Portale:",
                ["Tutti"] + list(self.portal_types.values()),
                index=0
            )
            st.session_state.portals_filter_type = filter_type
        
        with col2:
            filter_sector = st.selectbox(
                "Settore:",
                ["Tutti"] + list(self.sectors.values()),
                index=0
            )
            st.session_state.portals_filter_sector = filter_sector
        
        with col3:
            filter_status = st.selectbox(
                "Stato:",
                ["Tutti", "✅ Attivo", "⏸️ Inattivo", "🚀 Deployato", "📝 Bozza"],
                index=0
            )
            st.session_state.portals_filter_status = filter_status
    
    def render_quick_actions(self):
        """Rende le azioni rapide"""
        st.subheader("⚡ Azioni Rapide")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Nuovo Portale", use_container_width=True, type="primary"):
                st.session_state.portals_show_form = True
                st.session_state.portals_editing = None
                st.rerun()
        
        with col2:
            if st.button("🔄 Aggiorna", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("📊 Statistiche", use_container_width=True):
                self.show_detailed_stats()
        
        with col4:
            if st.button("🚀 Deploy Multipli", use_container_width=True):
                self.show_deploy_multiple_modal()
    
    def render_portal_form(self):
        """Rende il form per aggiungere/modificare portali"""
        st.subheader("🌐 Form Portale")
        
        # Recupera dati per modifica
        editing_portal = None
        if st.session_state.portals_editing:
            editing_portal = self.get_portal(st.session_state.portals_editing)
        
        with st.form("portal_form", clear_on_submit=True):
            # Campi del form
            portal_name = st.text_input(
                "🌐 Nome Portale *",
                value=editing_portal.get('portal_name', '') if editing_portal else '',
                placeholder="Es. Portale Finanza ABC",
                help="Inserisci un nome descrittivo per il portale"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                portal_type = st.selectbox(
                    "📋 Tipo Portale *",
                    options=list(self.portal_types.keys()),
                    format_func=lambda x: self.portal_types[x],
                    index=0 if not editing_portal else list(self.portal_types.keys()).index(editing_portal.get('portal_type', 'landing_page'))
                )
            
            with col2:
                sector = st.selectbox(
                    "🏷️ Settore *",
                    options=list(self.sectors.keys()),
                    format_func=lambda x: self.sectors[x],
                    index=0 if not editing_portal else list(self.sectors.keys()).index(editing_portal.get('sector', 'finanza'))
                )
            
            # Informazioni aggiuntive
            st.subheader("📝 Informazioni Progetto")
            
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input(
                    "🏢 Nome Azienda",
                    value=editing_portal.get('company_name', '') if editing_portal else '',
                    placeholder="Es. ABC Finanza SRL"
                )
                
                target_audience = st.text_input(
                    "🎯 Target Audience",
                    value=editing_portal.get('target_audience', '') if editing_portal else '',
                    placeholder="Es. PMI, Privati, etc."
                )
            
            with col2:
                business_goals = st.text_area(
                    "🎯 Obiettivi Business",
                    value=editing_portal.get('business_goals', '') if editing_portal else '',
                    placeholder="Descrivi gli obiettivi del portale...",
                    height=100
                )
            
            # Configurazioni avanzate
            st.subheader("⚙️ Configurazioni Avanzate")
            
            col1, col2 = st.columns(2)
            
            with col1:
                color_scheme = st.selectbox(
                    "🎨 Schema Colori",
                    ["Blu Professionale", "Verde Finanza", "Rosso Energia", "Viola Creativo", "Personalizzato"],
                    index=0 if not editing_portal else 0
                )
                
                include_contact_form = st.checkbox(
                    "📞 Include Form Contatto",
                    value=editing_portal.get('include_contact_form', True) if editing_portal else True
                )
            
            with col2:
                include_analytics = st.checkbox(
                    "📊 Include Analytics",
                    value=editing_portal.get('include_analytics', True) if editing_portal else True
                )
                
                mobile_responsive = st.checkbox(
                    "📱 Mobile Responsive",
                    value=editing_portal.get('mobile_responsive', True) if editing_portal else True
                )
            
            is_active = st.checkbox(
                "✅ Portale Attivo",
                value=editing_portal.get('is_active', True) if editing_portal else True,
                help="Attiva/disattiva il portale"
            )
            
            # Pulsanti
            col1, col2, col3 = st.columns(3)
            
            with col1:
                submitted = st.form_submit_button(
                    "💾 Salva Portale",
                    type="primary"
                )
            
            with col2:
                if st.form_submit_button("❌ Annulla"):
                    st.session_state.portals_show_form = False
                    st.session_state.portals_editing = None
                    st.rerun()
            
            with col3:
                if editing_portal and st.form_submit_button("🗑️ Elimina"):
                    self.delete_portal(editing_portal['id'])
                    st.session_state.portals_show_form = False
                    st.session_state.portals_editing = None
                    st.rerun()
            
            # Gestione submit
            if submitted:
                # Validazione al momento del submit
                validation_errors = []
                if not portal_name.strip():
                    validation_errors.append("❌ Nome portale obbligatorio")
                
                # Mostra errori di validazione se presenti
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                    return  # Non procedere se ci sono errori
                
                if editing_portal:
                    # Modifica portale esistente
                    success = self.update_portal(
                        editing_portal['id'],
                        portal_name.strip(),
                        portal_type,
                        sector,
                        company_name.strip(),
                        target_audience.strip(),
                        business_goals.strip(),
                        color_scheme,
                        include_contact_form,
                        include_analytics,
                        mobile_responsive,
                        is_active
                    )
                    if success:
                        st.success("✅ Portale aggiornato con successo!")
                        st.session_state.portals_show_form = False
                        st.session_state.portals_editing = None
                        st.rerun()
                    else:
                        st.error("❌ Errore aggiornamento portale")
                else:
                    # Crea nuovo portale
                    from components.auth.auth_manager import auth_manager
                    current_user = auth_manager.get_current_user()
                    if not current_user:
                        st.error("❌ Errore: Utente non autenticato")
                        return
                    
                    user_id = current_user.get('user_id')
                    if not user_id:
                        st.error("❌ Errore: ID utente non disponibile")
                        return
                    
                    portal_id = self.create_portal(
                        portal_name.strip(),
                        portal_type,
                        sector,
                        company_name.strip(),
                        target_audience.strip(),
                        business_goals.strip(),
                        color_scheme,
                        include_contact_form,
                        include_analytics,
                        mobile_responsive,
                        user_id
                    )
                    if portal_id:
                        st.success("✅ Portale creato con successo!")
                        st.session_state.portals_show_form = False
                        st.rerun()
                    else:
                        st.error("❌ Errore creazione portale")
    
    def render_portals_table(self):
        """Rende la tabella dei portali"""
        st.subheader("📋 Lista Portali")
        
        try:
            # Applica filtri
            portal_type_filter = None
            if st.session_state.portals_filter_type != "Tutti":
                for key, value in self.portal_types.items():
                    if value == st.session_state.portals_filter_type:
                        portal_type_filter = key
                        break
            
            sector_filter = None
            if st.session_state.portals_filter_sector != "Tutti":
                for key, value in self.sectors.items():
                    if value == st.session_state.portals_filter_sector:
                        sector_filter = key
                        break
            
            # Ottieni portali con filtri
            portals = self.get_portals(
                portal_type=portal_type_filter,
                sector=sector_filter
            )
            
            if not portals:
                st.info("📭 Nessun portale trovato con i filtri selezionati")
                return
            
            # Converti in DataFrame
            df = pd.DataFrame(portals)
            
            # Formatta le colonne
            if not df.empty:
                # Formatta le date
                if 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y %H:%M')
                if 'updated_at' in df.columns:
                    df['updated_at'] = pd.to_datetime(df['updated_at']).dt.strftime('%d/%m/%Y %H:%M')
                
                # Formatta lo stato
                if 'is_active' in df.columns:
                    df['Stato'] = df['is_active'].apply(lambda x: "✅ Attivo" if x else "⏸️ Inattivo")
                
                # Formatta tipo e settore
                if 'portal_type' in df.columns:
                    df['Tipo'] = df['portal_type'].apply(lambda x: self.portal_types.get(x, x))
                if 'sector' in df.columns:
                    df['Settore'] = df['sector'].apply(lambda x: self.sectors.get(x, x))
                
                # Seleziona colonne da mostrare
                display_columns = ['id', 'portal_name', 'Tipo', 'Settore', 'company_name', 'Stato', 'created_at']
                if 'updated_at' in df.columns:
                    display_columns.append('updated_at')
                
                display_df = df[display_columns].copy()
                display_df.columns = ['ID', 'Nome Portale', 'Tipo', 'Settore', 'Azienda', 'Stato', 'Creato il', 'Aggiornato il'] if 'updated_at' in df.columns else ['ID', 'Nome Portale', 'Tipo', 'Settore', 'Azienda', 'Stato', 'Creato il']
                
                # Mostra la tabella
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Azioni per ogni riga
                self.render_portal_actions(df)
                
        except Exception as e:
            st.error(f"❌ Errore caricamento portali: {e}")
    
    def render_portal_actions(self, df: pd.DataFrame):
        """Rende le azioni per ogni portale"""
        st.subheader("🔧 Azioni")
        
        # Selezione portale per azioni
        selected_portal = st.selectbox(
            "Seleziona un portale per le azioni:",
            options=df['portal_name'].tolist(),
            index=0 if not df.empty else None
        )
        
        if selected_portal:
            selected_row = df[df['portal_name'] == selected_portal].iloc[0]
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("✏️ Modifica", key=f"edit_{selected_row['id']}", use_container_width=True):
                    st.session_state.portals_editing = selected_row['id']
                    st.session_state.portals_show_form = True
                    st.rerun()
            
            with col2:
                if st.button("🚀 Genera", key=f"generate_{selected_row['id']}", use_container_width=True):
                    self.generate_portal(selected_row['id'])
                    st.rerun()
            
            with col3:
                if st.button("👁️ Anteprima", key=f"preview_{selected_row['id']}", use_container_width=True):
                    self.preview_portal(selected_row['id'])
            
            with col4:
                if st.button("📥 Download", key=f"download_{selected_row['id']}", use_container_width=True):
                    self.download_portal(selected_row['id'])
            
            with col5:
                if st.button("🗑️ Elimina", key=f"delete_{selected_row['id']}", use_container_width=True):
                    st.session_state['delete_modal_portal'] = selected_row
                    st.rerun()
    
    def get_portals_stats(self):
        """Ottiene le statistiche dei portali"""
        try:
            # Usa storage temporaneo fino a quando Supabase non riconosce le tabelle
            total_portals = len(self.temp_portals)
            active_portals = len([p for p in self.temp_portals if p.get('is_active', True)])
            deployed_portals = len([p for p in self.temp_portals if p.get('deployment_status') == 'deployed'])
            
            return {
                'total_portals': total_portals,
                'active_portals': active_portals,
                'deployed_portals': deployed_portals
            }
            
        except Exception as e:
            st.error(f"❌ Errore caricamento statistiche: {e}")
            return {
                'total_portals': 0,
                'active_portals': 0,
                'deployed_portals': 0
            }
    
    def get_portals(self, portal_type=None, sector=None):
        """Ottiene la lista dei portali"""
        try:
            # Usa storage temporaneo fino a quando Supabase non riconosce le tabelle
            portals = self.temp_portals.copy()
            
            # Applica filtri
            if portal_type:
                portals = [p for p in portals if p.get('portal_type') == portal_type]
            
            if sector:
                portals = [p for p in portals if p.get('sector') == sector]
            
            # Ordina per data di creazione (più recenti prima)
            portals.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return portals
            
        except Exception as e:
            st.error(f"❌ Errore caricamento portali: {e}")
            return []
    
    def get_portal(self, portal_id):
        """Ottiene un portale specifico"""
        try:
            # Usa storage temporaneo fino a quando Supabase non riconosce le tabelle
            for portal in self.temp_portals:
                if portal.get('id') == portal_id:
                    return portal
            return None
            
        except Exception as e:
            st.error(f"❌ Errore caricamento portale: {e}")
            return None
    
    def create_portal(self, portal_name, portal_type, sector, company_name, target_audience, business_goals, color_scheme, include_contact_form, include_analytics, mobile_responsive, user_id):
        """Crea un nuovo portale"""
        try:
            # Usa storage temporaneo fino a quando Supabase non riconosce le tabelle
            import uuid
            from datetime import datetime
            
            portal_id = str(uuid.uuid4())
            portal_data = {
                'id': portal_id,
                'portal_name': portal_name,
                'portal_type': portal_type,
                'sector': sector,
                'company_name': company_name,
                'target_audience': target_audience,
                'business_goals': business_goals,
                'color_scheme': color_scheme,
                'include_contact_form': include_contact_form,
                'include_analytics': include_analytics,
                'mobile_responsive': mobile_responsive,
                'is_active': True,
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Aggiungi al storage temporaneo
            self.temp_portals.append(portal_data)
            self.save_temp_storage()
            
            return portal_id
            
        except Exception as e:
            st.error(f"❌ Errore creazione portale: {e}")
            return None
    
    def update_portal(self, portal_id, portal_name, portal_type, sector, company_name, target_audience, business_goals, color_scheme, include_contact_form, include_analytics, mobile_responsive, is_active):
        """Aggiorna un portale esistente"""
        try:
            # Usa storage temporaneo fino a quando Supabase non riconosce le tabelle
            from datetime import datetime
            
            for i, portal in enumerate(self.temp_portals):
                if portal.get('id') == portal_id:
                    # Aggiorna i dati
                    self.temp_portals[i].update({
                        'portal_name': portal_name,
                        'portal_type': portal_type,
                        'sector': sector,
                        'company_name': company_name,
                        'target_audience': target_audience,
                        'business_goals': business_goals,
                        'color_scheme': color_scheme,
                        'include_contact_form': include_contact_form,
                        'include_analytics': include_analytics,
                        'mobile_responsive': mobile_responsive,
                        'is_active': is_active,
                        'updated_at': datetime.now().isoformat()
                    })
                    
                    self.save_temp_storage()
                    return True
            
            return False
            
        except Exception as e:
            st.error(f"❌ Errore aggiornamento portale: {e}")
            return False
    
    def delete_portal(self, portal_id):
        """Elimina un portale"""
        try:
            # Usa storage temporaneo fino a quando Supabase non riconosce le tabelle
            for i, portal in enumerate(self.temp_portals):
                if portal.get('id') == portal_id:
                    del self.temp_portals[i]
                    self.save_temp_storage()
                    return True
            
            return False
            
        except Exception as e:
            st.error(f"❌ Errore eliminazione portale: {e}")
            return False
    
    def generate_portal(self, portal_id):
        """Genera il codice del portale"""
        try:
            # Ottieni i dati del portale
            portal_data = self.get_portal(portal_id)
            if not portal_data:
                st.error("❌ Portale non trovato")
                return
            
            # Mostra progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔄 Inizializzazione generazione...")
            progress_bar.progress(10)
            
            # Importa il PortalBuilder
            from .portal_builder import PortalBuilder
            builder = PortalBuilder()
            
            status_text.text("🏗️ Costruzione portale...")
            progress_bar.progress(30)
            
            # Genera il portale
            result = builder.build_portal(portal_data)
            
            status_text.text("✅ Generazione completata!")
            progress_bar.progress(100)
            
            if result['success']:
                st.success(f"✅ Portale generato con successo!")
                st.info(f"📁 Directory: {result['portal_dir']}")
                st.info(f"📦 ZIP: {result['zip_path']}")
                st.info(f"👁️ Anteprima: {result['preview_path']}")
                
                # Mostra pulsanti di azione
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📥 Download ZIP", use_container_width=True):
                        with open(result['zip_path'], 'rb') as f:
                            st.download_button(
                                label="Scarica Portale",
                                data=f.read(),
                                file_name=f"{portal_data['portal_name']}.zip",
                                mime="application/zip"
                            )
                
                with col2:
                    if st.button("👁️ Visualizza Anteprima", use_container_width=True):
                        st.markdown(f"### Anteprima: {portal_data['portal_name']}")
                        with open(result['preview_path'], 'r', encoding='utf-8') as f:
                            st.components.v1.html(f.read(), height=600, scrolling=True)
                
                with col3:
                    if st.button("🚀 Deploy", use_container_width=True):
                        st.session_state['deploy_portal_id'] = portal_id
                        st.session_state['deploy_portal_data'] = result
                        st.rerun()
                
            else:
                st.error(f"❌ Errore generazione portale: {result.get('error', 'Errore sconosciuto')}")
            
            # Nascondi progress bar dopo 2 secondi
            import time
            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"❌ Errore durante generazione: {e}")
    
    def preview_portal(self, portal_id):
        """Mostra l'anteprima del portale"""
        st.info("👁️ Funzionalità di anteprima in sviluppo...")
    
    def download_portal(self, portal_id):
        """Scarica il portale generato"""
        st.info("📥 Funzionalità di download in sviluppo...")
    
    def show_detailed_stats(self):
        """Mostra statistiche dettagliate"""
        st.info("📊 Statistiche dettagliate in sviluppo...")
    
    def show_deploy_multiple_modal(self):
        """Mostra il modal per deployment multiplo"""
        st.info("🚀 Deployment multiplo in sviluppo...")
