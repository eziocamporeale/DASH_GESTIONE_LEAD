#!/usr/bin/env python3
"""
Componente per gestione Script
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

class ScriptsManager:
    """Gestore per gli script testuali"""
    
    def __init__(self, db_manager):
        """Inizializza il gestore"""
        self.db = db_manager
        self.setup_session_state()
        self.setup_script_types()
        self.setup_categories()
    
    def setup_session_state(self):
        """Inizializza lo stato della sessione"""
        if 'scripts_editing' not in st.session_state:
            st.session_state.scripts_editing = None
        if 'scripts_show_form' not in st.session_state:
            st.session_state.scripts_show_form = False
        if 'scripts_filter_type' not in st.session_state:
            st.session_state.scripts_filter_type = "Tutti"
        if 'scripts_filter_category' not in st.session_state:
            st.session_state.scripts_filter_category = "Tutte"
    
    def setup_script_types(self):
        """Definisce i tipi di script disponibili"""
        self.script_types = {
            "chiamata": "📞 Chiamata",
            "email": "📧 Email", 
            "messaggio": "💬 Messaggio",
            "presentazione": "📋 Presentazione",
            "vendita": "🎯 Vendita",
            "supporto": "🆘 Supporto"
        }
    
    def setup_categories(self):
        """Definisce le categorie disponibili"""
        self.categories = {
            "lead_generation": "🚀 Lead Generation",
            "vendita": "💰 Vendita",
            "follow_up": "🔄 Follow-up",
            "supporto": "🆘 Supporto",
            "marketing": "📢 Marketing"
        }
    
    def render_scripts_page(self):
        """Rende la pagina principale degli script"""
        st.header("📝 Gestione Script")
        st.markdown("Gestisci gli script testuali per chiamate e comunicazioni")
        
        # Statistiche
        self.render_stats()
        
        # Filtri
        self.render_filters()
        
        # Azioni rapide
        self.render_quick_actions()
        
        # Form per aggiungere/modificare
        if st.session_state.scripts_show_form:
            self.render_script_form()
        
        # Tabella degli script
        self.render_scripts_table()
    
    def render_stats(self):
        """Rende le statistiche degli script"""
        try:
            stats = self.db.get_scripts_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="📊 Totale Script",
                    value=stats.get('total_scripts', 0),
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="✅ Script Attivi",
                    value=stats.get('active_scripts', 0),
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="⏸️ Script Inattivi",
                    value=stats.get('inactive_scripts', 0),
                    delta=None
                )
            
            with col4:
                active_percentage = 0
                if stats.get('total_scripts', 0) > 0:
                    active_percentage = round((stats.get('active_scripts', 0) / stats.get('total_scripts', 1)) * 100, 1)
                
                st.metric(
                    label="📈 % Attivi",
                    value=f"{active_percentage}%",
                    delta=None
                )
                
        except Exception as e:
            st.error(f"❌ Errore caricamento statistiche: {e}")
    
    def render_filters(self):
        """Rende i filtri per gli script"""
        st.subheader("🔍 Filtri")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_type = st.selectbox(
                "Tipo Script:",
                ["Tutti"] + list(self.script_types.values()),
                index=0
            )
            st.session_state.scripts_filter_type = filter_type
        
        with col2:
            filter_category = st.selectbox(
                "Categoria:",
                ["Tutte"] + list(self.categories.values()),
                index=0
            )
            st.session_state.scripts_filter_category = filter_category
        
        with col3:
            show_inactive = st.checkbox("Mostra anche inattivi", value=False)
            st.session_state.scripts_show_inactive = show_inactive
    
    def render_quick_actions(self):
        """Rende le azioni rapide"""
        st.subheader("⚡ Azioni Rapide")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Nuovo Script", use_container_width=True, type="primary"):
                st.session_state.scripts_show_form = True
                st.session_state.scripts_editing = None
                st.rerun()
        
        with col2:
            if st.button("🔄 Aggiorna", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("📊 Statistiche", use_container_width=True):
                self.show_detailed_stats()
        
        with col4:
            if st.button("🗑️ Elimina Multipli", use_container_width=True):
                self.show_delete_multiple_modal()
    
    def render_script_form(self):
        """Rende il form per aggiungere/modificare script"""
        st.subheader("📝 Form Script")
        
        # Recupera dati per modifica
        editing_script = None
        if st.session_state.scripts_editing:
            editing_script = self.db.get_script(st.session_state.scripts_editing)
        
        with st.form("script_form", clear_on_submit=True):
            # Campi del form
            title = st.text_input(
                "📝 Titolo Script *",
                value=editing_script.get('title', '') if editing_script else '',
                placeholder="Es. Script Chiamata Vendita",
                help="Inserisci un titolo descrittivo per lo script"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                script_type = st.selectbox(
                    "📋 Tipo Script *",
                    options=list(self.script_types.keys()),
                    format_func=lambda x: self.script_types[x],
                    index=0 if not editing_script else list(self.script_types.keys()).index(editing_script.get('script_type', 'chiamata'))
                )
            
            with col2:
                category = st.selectbox(
                    "🏷️ Categoria *",
                    options=list(self.categories.keys()),
                    format_func=lambda x: self.categories[x],
                    index=0 if not editing_script else list(self.categories.keys()).index(editing_script.get('category', 'vendita'))
                )
            
            content = st.text_area(
                "📄 Contenuto Script *",
                value=editing_script.get('content', '') if editing_script else '',
                placeholder="Inserisci qui il contenuto dello script...",
                height=300,
                help="Scrivi il contenuto completo dello script"
            )
            
            is_active = st.checkbox(
                "✅ Script Attivo",
                value=editing_script.get('is_active', True) if editing_script else True,
                help="Attiva/disattiva lo script"
            )
            
            # Validazione
            validation_errors = []
            if not title.strip():
                validation_errors.append("❌ Titolo script obbligatorio")
            
            if not content.strip():
                validation_errors.append("❌ Contenuto script obbligatorio")
            
            # Mostra errori di validazione
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            
            # Pulsanti
            col1, col2, col3 = st.columns(3)
            
            with col1:
                submitted = st.form_submit_button(
                    "💾 Salva Script",
                    type="primary",
                    disabled=len(validation_errors) > 0
                )
            
            with col2:
                if st.form_submit_button("❌ Annulla"):
                    st.session_state.scripts_show_form = False
                    st.session_state.scripts_editing = None
                    st.rerun()
            
            with col3:
                if editing_script and st.form_submit_button("🗑️ Elimina"):
                    self.delete_script(editing_script['id'])
                    st.session_state.scripts_show_form = False
                    st.session_state.scripts_editing = None
                    st.rerun()
            
            # Gestione submit
            if submitted and len(validation_errors) == 0:
                if editing_script:
                    # Modifica script esistente
                    success = self.db.update_script(
                        editing_script['id'],
                        title.strip(),
                        content.strip(),
                        script_type,
                        category,
                        is_active
                    )
                    if success:
                        st.success("✅ Script aggiornato con successo!")
                        st.session_state.scripts_show_form = False
                        st.session_state.scripts_editing = None
                        st.rerun()
                    else:
                        st.error("❌ Errore aggiornamento script")
                else:
                    # Crea nuovo script
                    # Ottieni user_id dalla sessione (UUID per Supabase)
                    user_id = st.session_state.get('user_id', None)  # UUID per Supabase
                    if not user_id:
                        st.error("❌ Errore: ID utente non disponibile")
                        return
                    
                    script_id = self.db.create_script(
                        title.strip(),
                        content.strip(),
                        script_type,
                        category,
                        user_id
                    )
                    if script_id:
                        st.success("✅ Script creato con successo!")
                        st.session_state.scripts_show_form = False
                        st.rerun()
                    else:
                        st.error("❌ Errore creazione script")
    
    def render_scripts_table(self):
        """Rende la tabella degli script"""
        st.subheader("📋 Lista Script")
        
        try:
            # Applica filtri
            script_type_filter = None
            if st.session_state.scripts_filter_type != "Tutti":
                # Trova la chiave dal valore visualizzato
                for key, value in self.script_types.items():
                    if value == st.session_state.scripts_filter_type:
                        script_type_filter = key
                        break
            
            category_filter = None
            if st.session_state.scripts_filter_category != "Tutte":
                # Trova la chiave dal valore visualizzato
                for key, value in self.categories.items():
                    if value == st.session_state.scripts_filter_category:
                        category_filter = key
                        break
            
            # Ottieni script con filtri
            scripts = self.db.get_scripts(
                active_only=not st.session_state.scripts_show_inactive,
                script_type=script_type_filter,
                category=category_filter
            )
            
            if not scripts:
                st.info("📭 Nessuno script trovato con i filtri selezionati")
                return
            
            # Converti in DataFrame
            df = pd.DataFrame(scripts)
            
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
                
                # Formatta tipo e categoria
                if 'script_type' in df.columns:
                    df['Tipo'] = df['script_type'].apply(lambda x: self.script_types.get(x, x))
                if 'category' in df.columns:
                    df['Categoria'] = df['category'].apply(lambda x: self.categories.get(x, x))
                
                # Tronca il contenuto se troppo lungo
                if 'content' in df.columns:
                    df['Contenuto'] = df['content'].apply(lambda x: x[:100] + "..." if len(x) > 100 else x)
                
                # Seleziona colonne da mostrare
                display_columns = ['id', 'title', 'Tipo', 'Categoria', 'Contenuto', 'Stato', 'created_at']
                if 'updated_at' in df.columns:
                    display_columns.append('updated_at')
                
                display_df = df[display_columns].copy()
                display_df.columns = ['ID', 'Titolo', 'Tipo', 'Categoria', 'Contenuto', 'Stato', 'Creato il', 'Aggiornato il'] if 'updated_at' in df.columns else ['ID', 'Titolo', 'Tipo', 'Categoria', 'Contenuto', 'Stato', 'Creato il']
                
                # Mostra la tabella
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Azioni per ogni riga
                self.render_script_actions(df)
                
        except Exception as e:
            st.error(f"❌ Errore caricamento script: {e}")
    
    def render_script_actions(self, df: pd.DataFrame):
        """Rende le azioni per ogni script"""
        st.subheader("🔧 Azioni")
        
        # Selezione script per azioni
        selected_script = st.selectbox(
            "Seleziona uno script per le azioni:",
            options=df['title'].tolist(),
            index=0 if not df.empty else None
        )
        
        if selected_script:
            selected_row = df[df['title'] == selected_script].iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✏️ Modifica", key=f"edit_{selected_row['id']}", use_container_width=True):
                    st.session_state.scripts_editing = selected_row['id']
                    st.session_state.scripts_show_form = True
                    st.rerun()
            
            with col2:
                status_text = "Disattiva" if selected_row.get('is_active', True) else "Attiva"
                if st.button(f"🔄 {status_text}", key=f"toggle_{selected_row['id']}", use_container_width=True):
                    self.toggle_script_status(selected_row['id'])
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Elimina", key=f"delete_{selected_row['id']}", use_container_width=True):
                    self.show_delete_modal(selected_row)
            
            with col4:
                if st.button("📋 Copia Contenuto", key=f"copy_{selected_row['id']}", use_container_width=True):
                    st.write("Contenuto copiato negli appunti!")
                    st.code(selected_row['content'])
    
    def show_delete_modal(self, script: Dict):
        """Mostra il modal di conferma eliminazione"""
        st.warning("⚠️ Conferma Eliminazione")
        st.write(f"Sei sicuro di voler eliminare lo script **{script['title']}**?")
        st.write(f"Tipo: {script.get('script_type', 'N/A')}")
        st.write(f"Categoria: {script.get('category', 'N/A')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Conferma Eliminazione", type="primary"):
                if self.delete_script(script['id']):
                    st.success("✅ Script eliminato con successo!")
                    st.rerun()
                else:
                    st.error("❌ Errore eliminazione script")
        
        with col2:
            if st.button("❌ Annulla"):
                st.rerun()
    
    def show_delete_multiple_modal(self):
        """Mostra il modal per eliminazione multipla"""
        st.warning("⚠️ Eliminazione Multipla")
        st.write("Seleziona gli script da eliminare:")
        
        try:
            scripts = self.db.get_scripts(active_only=False)
            
            if not scripts:
                st.info("📭 Nessuno script da eliminare")
                return
            
            # Checkbox per selezione multipla
            selected_ids = []
            for script in scripts:
                if st.checkbox(
                    f"{script['title']} - {script['script_type']} ({script['category']})",
                    key=f"delete_multiple_{script['id']}"
                ):
                    selected_ids.append(script['id'])
            
            if selected_ids:
                st.write(f"📋 Selezionati {len(selected_ids)} script per eliminazione")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🗑️ Elimina Selezionati", type="primary"):
                        success_count = 0
                        for script_id in selected_ids:
                            if self.delete_script(script_id):
                                success_count += 1
                        
                        if success_count == len(selected_ids):
                            st.success(f"✅ {success_count} script eliminati con successo!")
                        else:
                            st.warning(f"⚠️ {success_count}/{len(selected_ids)} script eliminati")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Annulla"):
                        st.rerun()
            else:
                st.info("📝 Seleziona almeno uno script per eliminare")
                
        except Exception as e:
            st.error(f"❌ Errore caricamento script: {e}")
    
    def show_detailed_stats(self):
        """Mostra statistiche dettagliate"""
        st.subheader("📊 Statistiche Dettagliate")
        
        try:
            stats = self.db.get_scripts_stats()
            scripts = self.db.get_scripts(active_only=False)
            
            # Statistiche generali
            st.write("**Statistiche Generali:**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Totale Script", stats.get('total_scripts', 0))
                st.metric("Script Attivi", stats.get('active_scripts', 0))
            
            with col2:
                st.metric("Script Inattivi", stats.get('inactive_scripts', 0))
                if stats.get('total_scripts', 0) > 0:
                    active_percentage = round((stats.get('active_scripts', 0) / stats.get('total_scripts', 1)) * 100, 1)
                    st.metric("Percentuale Attivi", f"{active_percentage}%")
            
            # Statistiche per tipo
            if stats.get('type_stats'):
                st.write("**Script per Tipo:**")
                type_df = pd.DataFrame([
                    {'Tipo': self.script_types.get(k, k), 'Quantità': v} 
                    for k, v in stats['type_stats'].items()
                ])
                st.dataframe(type_df, use_container_width=True, hide_index=True)
            
            # Statistiche per categoria
            if stats.get('category_stats'):
                st.write("**Script per Categoria:**")
                category_df = pd.DataFrame([
                    {'Categoria': self.categories.get(k, k), 'Quantità': v} 
                    for k, v in stats['category_stats'].items()
                ])
                st.dataframe(category_df, use_container_width=True, hide_index=True)
            
            # Lista dettagliata
            if scripts:
                st.write("**Lista Dettagliata:**")
                df = pd.DataFrame(scripts)
                
                if 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y %H:%M')
                
                st.dataframe(
                    df[['title', 'script_type', 'category', 'is_active', 'created_at']],
                    use_container_width=True,
                    hide_index=True
                )
            
        except Exception as e:
            st.error(f"❌ Errore caricamento statistiche: {e}")
    
    def delete_script(self, script_id: int) -> bool:
        """Elimina un script"""
        try:
            return self.db.delete_script(script_id)
        except Exception as e:
            st.error(f"❌ Errore eliminazione: {e}")
            return False
    
    def toggle_script_status(self, script_id: int) -> bool:
        """Attiva/disattiva un script"""
        try:
            return self.db.toggle_script_status(script_id)
        except Exception as e:
            st.error(f"❌ Errore cambio stato: {e}")
            return False
