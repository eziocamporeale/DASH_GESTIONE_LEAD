#!/usr/bin/env python3
"""
Componente Gestione Gruppi Lead per DASH_GESTIONE_LEAD
Gestione completa dei gruppi di venditori e assegnazioni utenti
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

class LeadGroupManagement:
    """Gestisce la creazione e gestione dei gruppi di lead"""
    
    def __init__(self):
        """Inizializza il gestore gruppi"""
        self.db = DatabaseManager()
        self.current_user = get_current_user()
    
    def render_groups_page(self):
        """Renderizza la pagina principale di gestione gruppi"""
        st.markdown("## 👥 Gestione Gruppi Lead")
        
        # Verifica permessi
        if not self.current_user:
            st.error("🔒 Accesso richiesto. Effettua il login per continuare.")
            return
        
        if self.current_user.get('role_name') != 'Admin':
            st.error("🚫 Accesso negato. Solo Admin può gestire i gruppi di venditori.")
            return
        
        # Tabs per diverse funzionalità
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista Gruppi", "➕ Nuovo Gruppo", "👥 Assegnazioni Utenti", "📝 Assegnazioni Lead"])
        
        with tab1:
            self.render_groups_list()
        
        with tab2:
            self.render_create_group_form()
        
        with tab3:
            self.render_user_assignments()
        
        with tab4:
            self.render_lead_assignments()
    
    def render_groups_list(self):
        """Renderizza la lista dei gruppi esistenti"""
        st.markdown("### 📋 Gruppi Esistenti")
        
        try:
            groups = self.db.get_lead_groups()
            
            if not groups:
                st.info("📭 Nessun gruppo trovato. Crea il primo gruppo!")
                return
            
            # Converti in DataFrame per visualizzazione
            df_data = []
            for group in groups:
                # Ottieni statistiche del gruppo
                stats = self.db.get_group_statistics(group['id'])
                
                df_data.append({
                    'ID': group['id'],
                    'Nome': group['name'],
                    'Descrizione': group.get('description', ''),
                    'Colore': group.get('color', '#6C757D'),
                    'Lead': stats.get('total_leads', 0),
                    'Utenti': stats.get('total_users', 0),
                    'Attivo': '✅' if group.get('is_active', True) else '❌',
                    'Creato': group.get('created_at', '')[:10] if group.get('created_at') else ''
                })
            
            df = pd.DataFrame(df_data)
            
            # Mostra la tabella
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            # Azioni sui gruppi
            st.markdown("### ⚙️ Azioni")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Aggiorna Lista", use_container_width=True):
                    st.rerun()
            
            with col2:
                if st.button("📊 Statistiche", use_container_width=True):
                    self.render_group_statistics()
            
            with col3:
                if st.button("🗑️ Gestisci Gruppi", use_container_width=True):
                    self.render_group_management()
                    
        except Exception as e:
            st.error(f"❌ Errore nel caricamento dei gruppi: {e}")
    
    def render_create_group_form(self):
        """Renderizza il form per creare un nuovo gruppo"""
        st.markdown("### ➕ Crea Nuovo Gruppo")
        
        with st.form("create_group_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    "Nome Gruppo *",
                    help="Nome del gruppo di venditori"
                )
                
                description = st.text_area(
                    "Descrizione",
                    help="Descrizione del gruppo e del suo scopo"
                )
            
            with col2:
                color = st.color_picker(
                    "Colore",
                    value="#28A745",
                    help="Colore per identificare il gruppo"
                )
                
                is_active = st.checkbox(
                    "Gruppo Attivo",
                    value=True,
                    help="Se il gruppo è attivo e può essere utilizzato"
                )
            
            # Pulsanti
            col1, col2 = st.columns(2)
            
            with col1:
                submit_button = st.form_submit_button(
                    "💾 Crea Gruppo",
                    use_container_width=True
                )
            
            with col2:
                cancel_button = st.form_submit_button(
                    "❌ Annulla",
                    use_container_width=True
                )
            
            # Gestione submit
            if submit_button:
                if not name.strip():
                    st.error("❌ Il nome del gruppo è obbligatorio!")
                    return
                
                # Prepara i dati
                group_data = {
                    'name': name.strip(),
                    'description': description.strip() if description else '',
                    'color': color,
                    'is_active': is_active,
                    'created_by': self.current_user['user_id']
                }
                
                # Crea il gruppo
                group_id = self.db.create_lead_group(group_data)
                
                if group_id:
                    st.success(f"✅ Gruppo '{name}' creato con successo!")
                    
                    # Log attività
                    self.db.log_activity(
                        user_id=self.current_user['user_id'],
                        action='create',
                        entity_type='lead_group',
                        entity_id=group_id,
                        details=f"Creato gruppo '{name}'"
                    )
                    
                    st.rerun()
                else:
                    st.error("❌ Errore nella creazione del gruppo. Riprova.")
    
    def render_user_assignments(self):
        """Renderizza la gestione delle assegnazioni utenti-gruppi"""
        st.markdown("### 👥 Assegnazioni Utenti-Gruppi")
        
        try:
            # Ottieni tutti i gruppi
            groups = self.db.get_lead_groups()
            if not groups:
                st.info("📭 Nessun gruppo disponibile. Crea prima un gruppo.")
                return
            
            # Ottieni tutti gli utenti
            users = self.db.get_all_users()
            if not users:
                st.info("📭 Nessun utente disponibile.")
                return
            
            # Selezione gruppo
            group_options = {f"{group['name']}": group['id'] for group in groups}
            selected_group_name = st.selectbox(
                "Seleziona Gruppo",
                options=list(group_options.keys()),
                help="Scegli il gruppo per cui gestire le assegnazioni"
            )
            
            if not selected_group_name:
                return
            
            selected_group_id = group_options[selected_group_name]
            selected_group = next((g for g in groups if g['id'] == selected_group_id), None)
            
            if not selected_group:
                st.error("❌ Gruppo non trovato.")
                return
            
            st.markdown(f"**Gruppo Selezionato:** {selected_group['name']}")
            
            # Mostra utenti attualmente assegnati
            st.markdown("### 👥 Utenti Assegnati")
            
            assigned_users = self.db.get_user_lead_groups(0)  # Ottieni tutti per questo gruppo
            # Filtra per il gruppo selezionato
            group_users = [u for u in assigned_users if u.get('group_id') == selected_group_id]
            
            if group_users:
                user_data = []
                for user_group in group_users:
                    # Trova l'utente corrispondente
                    user = next((u for u in users if u['id'] == user_group['user_id']), None)
                    if user:
                        user_data.append({
                            'ID': user['id'],
                            'Nome': f"{user['first_name']} {user['last_name']}",
                            'Username': user['username'],
                            'Ruolo': user.get('role_name', 'N/A'),
                            'Può Gestire': '✅' if user_group.get('can_manage', False) else '❌',
                            'Assegnato': user_group.get('created_at', '')[:10] if user_group.get('created_at') else ''
                        })
                
                if user_data:
                    df_users = pd.DataFrame(user_data)
                    st.dataframe(df_users, use_container_width=True, hide_index=True)
                else:
                    st.info("📭 Nessun utente assegnato a questo gruppo.")
            else:
                st.info("📭 Nessun utente assegnato a questo gruppo.")
            
            # Form per aggiungere utenti
            st.markdown("### ➕ Aggiungi Utente al Gruppo")
            
            with st.form("add_user_to_group_form"):
                # Selezione utente
                available_users = [u for u in users if u['id'] not in [ug['user_id'] for ug in group_users]]
                
                if not available_users:
                    st.info("📭 Tutti gli utenti sono già assegnati a questo gruppo.")
                else:
                    user_options = {f"{user['first_name']} {user['last_name']} ({user['username']})": user['id'] for user in available_users}
                    
                    selected_user_name = st.selectbox(
                        "Seleziona Utente",
                        options=list(user_options.keys()),
                        help="Scegli l'utente da aggiungere al gruppo"
                    )
                    
                    can_manage = st.checkbox(
                        "Può Gestire Gruppo",
                        help="Se l'utente può gestire il gruppo (assegnare lead, modificare gruppo)"
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        add_button = st.form_submit_button(
                            "➕ Aggiungi Utente",
                            use_container_width=True
                        )
                    
                    with col2:
                        cancel_button = st.form_submit_button(
                            "❌ Annulla",
                            use_container_width=True
                        )
                    
                    if add_button:
                        selected_user_id = user_options[selected_user_name]
                        
                        # Assegna l'utente al gruppo
                        success = self.db.assign_user_to_group(
                            user_id=selected_user_id,
                            group_id=selected_group_id,
                            can_manage=can_manage
                        )
                        
                        if success:
                            st.success(f"✅ Utente aggiunto al gruppo '{selected_group['name']}'!")
                            
                            # Log attività
                            self.db.log_activity(
                                user_id=self.current_user['user_id'],
                                action='assign',
                                entity_type='user_group',
                                entity_id=selected_user_id,
                                details=f"Assegnato utente al gruppo '{selected_group['name']}'"
                            )
                            
                            st.rerun()
                        else:
                            st.error("❌ Errore nell'assegnazione dell'utente. Riprova.")
            
            # Rimozione utenti
            if group_users:
                st.markdown("### 🗑️ Rimuovi Utente dal Gruppo")
                
                with st.form("remove_user_from_group_form"):
                    user_to_remove_options = {f"{u['first_name']} {u['last_name']} ({u['username']})": u['id'] for u in users if u['id'] in [ug['user_id'] for ug in group_users]}
                    
                    selected_user_to_remove = st.selectbox(
                        "Seleziona Utente da Rimuovere",
                        options=list(user_to_remove_options.keys()),
                        help="Scegli l'utente da rimuovere dal gruppo"
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        remove_button = st.form_submit_button(
                            "🗑️ Rimuovi Utente",
                            use_container_width=True
                        )
                    
                    with col2:
                        cancel_button = st.form_submit_button(
                            "❌ Annulla",
                            use_container_width=True
                        )
                    
                    if remove_button:
                        user_id_to_remove = user_to_remove_options[selected_user_to_remove]
                        
                        # Rimuovi l'utente dal gruppo
                        success = self.db.remove_user_from_group(
                            user_id=user_id_to_remove,
                            group_id=selected_group_id
                        )
                        
                        if success:
                            st.success(f"✅ Utente rimosso dal gruppo '{selected_group['name']}'!")
                            
                            # Log attività
                            self.db.log_activity(
                                user_id=self.current_user['user_id'],
                                action='unassign',
                                entity_type='user_group',
                                entity_id=user_id_to_remove,
                                details=f"Rimosso utente dal gruppo '{selected_group['name']}'"
                            )
                            
                            st.rerun()
                        else:
                            st.error("❌ Errore nella rimozione dell'utente. Riprova.")
                            
        except Exception as e:
            st.error(f"❌ Errore nella gestione delle assegnazioni: {e}")
    
    def render_lead_assignments(self):
        """Renderizza la gestione delle assegnazioni lead-gruppi"""
        st.markdown("### 📝 Assegnazioni Lead-Gruppi")
        
        try:
            # Ottieni tutti i gruppi
            groups = self.db.get_lead_groups()
            if not groups:
                st.info("📭 Nessun gruppo disponibile. Crea prima un gruppo.")
                return
            
            # Ottieni tutti i lead
            leads = self.db.get_leads(limit=1000)  # Ottieni più lead per la selezione
            if not leads:
                st.info("📭 Nessun lead disponibile.")
                return
            
            # Selezione gruppo
            group_options = {f"{group['name']}": group['id'] for group in groups}
            selected_group_name = st.selectbox(
                "Seleziona Gruppo",
                options=list(group_options.keys()),
                help="Scegli il gruppo a cui assegnare i lead"
            )
            
            if not selected_group_name:
                return
            
            selected_group_id = group_options[selected_group_name]
            selected_group = next((g for g in groups if g['id'] == selected_group_id), None)
            
            if not selected_group:
                st.error("❌ Gruppo non trovato.")
                return
            
            st.markdown(f"**Gruppo Selezionato:** {selected_group['name']}")
            
            # Mostra lead attualmente assegnati al gruppo
            st.markdown("### 📝 Lead Assegnati al Gruppo")
            
            group_leads = [lead for lead in leads if lead.get('group_id') == selected_group_id]
            
            if group_leads:
                lead_data = []
                for lead in group_leads:
                    lead_data.append({
                        'ID': lead['id'],
                        'Nome': lead.get('name', 'N/A'),
                        'Email': lead.get('email', 'N/A'),
                        'Telefono': lead.get('phone', 'N/A'),
                        'Azienda': lead.get('company', 'N/A'),
                        'Stato': lead.get('state_name', 'N/A'),
                        'Assegnato': lead.get('created_at', '')[:10] if lead.get('created_at') else ''
                    })
                
                df_leads = pd.DataFrame(lead_data)
                st.dataframe(df_leads, use_container_width=True, hide_index=True)
            else:
                st.info("📭 Nessun lead assegnato a questo gruppo.")
            
            # Form per assegnare lead al gruppo
            st.markdown("### ➕ Assegna Lead al Gruppo")
            
            with st.form("assign_lead_to_group_form"):
                # Filtra lead non assegnati o assegnati ad altri gruppi
                available_leads = [lead for lead in leads if lead.get('group_id') != selected_group_id]
                
                if not available_leads:
                    st.info("📭 Tutti i lead sono già assegnati a questo gruppo.")
                else:
                    # Selezione lead
                    lead_options = {f"{lead.get('name', 'N/A')} - {lead.get('company', 'N/A')}": lead['id'] for lead in available_leads}
                    
                    selected_lead_name = st.selectbox(
                        "Seleziona Lead",
                        options=list(lead_options.keys()),
                        help="Scegli il lead da assegnare al gruppo"
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        assign_button = st.form_submit_button(
                            "📝 Assegna Lead",
                            use_container_width=True
                        )
                    
                    with col2:
                        cancel_button = st.form_submit_button(
                            "❌ Annulla",
                            use_container_width=True
                        )
                    
                    if assign_button:
                        selected_lead_id = lead_options[selected_lead_name]
                        
                        # Aggiorna il lead con il group_id
                        success = self.db.update_lead(selected_lead_id, {'group_id': selected_group_id})
                        
                        if success:
                            st.success(f"✅ Lead assegnato al gruppo '{selected_group['name']}'!")
                            
                            # Log attività
                            self.db.log_activity(
                                user_id=self.current_user['user_id'],
                                action='assign',
                                entity_type='lead',
                                entity_id=selected_lead_id,
                                details=f"Assegnato lead al gruppo '{selected_group['name']}'"
                            )
                            
                            st.rerun()
                        else:
                            st.error("❌ Errore nell'assegnazione del lead. Riprova.")
            
            # Rimozione lead dal gruppo
            if group_leads:
                st.markdown("### 🗑️ Rimuovi Lead dal Gruppo")
                
                with st.form("remove_lead_from_group_form"):
                    lead_to_remove_options = {f"{lead.get('name', 'N/A')} - {lead.get('company', 'N/A')}": lead['id'] for lead in group_leads}
                    
                    selected_lead_to_remove = st.selectbox(
                        "Seleziona Lead da Rimuovere",
                        options=list(lead_to_remove_options.keys()),
                        help="Scegli il lead da rimuovere dal gruppo"
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        remove_button = st.form_submit_button(
                            "🗑️ Rimuovi Lead",
                            use_container_width=True
                        )
                    
                    with col2:
                        cancel_button = st.form_submit_button(
                            "❌ Annulla",
                            use_container_width=True
                        )
                    
                    if remove_button:
                        lead_id_to_remove = lead_to_remove_options[selected_lead_to_remove]
                        
                        # Rimuovi il group_id dal lead (imposta a None)
                        success = self.db.update_lead(lead_id_to_remove, {'group_id': None})
                        
                        if success:
                            st.success(f"✅ Lead rimosso dal gruppo '{selected_group['name']}'!")
                            
                            # Log attività
                            self.db.log_activity(
                                user_id=self.current_user['user_id'],
                                action='unassign',
                                entity_type='lead',
                                entity_id=lead_id_to_remove,
                                details=f"Rimosso lead dal gruppo '{selected_group['name']}'"
                            )
                            
                            st.rerun()
                        else:
                            st.error("❌ Errore nella rimozione del lead. Riprova.")
                            
        except Exception as e:
            st.error(f"❌ Errore nella gestione delle assegnazioni lead: {e}")
    
    def render_group_statistics(self):
        """Renderizza le statistiche dei gruppi"""
        st.markdown("### 📊 Statistiche Gruppi")
        
        try:
            groups = self.db.get_lead_groups()
            
            if not groups:
                st.info("📭 Nessun gruppo disponibile.")
                return
            
            # Crea grafici per ogni gruppo
            for group in groups:
                with st.expander(f"📈 {group['name']}", expanded=False):
                    stats = self.db.get_group_statistics(group['id'])
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Lead Totali",
                            stats.get('total_leads', 0)
                        )
                    
                    with col2:
                        st.metric(
                            "Utenti Assegnati",
                            stats.get('total_users', 0)
                        )
                    
                    with col3:
                        st.metric(
                            "Stato",
                            "Attivo" if group.get('is_active', True) else "Inattivo"
                        )
                    
                    # Descrizione del gruppo
                    if group.get('description'):
                        st.markdown(f"**Descrizione:** {group['description']}")
                    
        except Exception as e:
            st.error(f"❌ Errore nel caricamento delle statistiche: {e}")
    
    def render_group_management(self):
        """Renderizza la gestione avanzata dei gruppi"""
        st.markdown("### ⚙️ Gestione Avanzata Gruppi")
        
        try:
            groups = self.db.get_lead_groups()
            
            if not groups:
                st.info("📭 Nessun gruppo disponibile.")
                return
            
            # Selezione gruppo per gestione
            group_options = {f"{group['name']}": group['id'] for group in groups}
            selected_group_name = st.selectbox(
                "Seleziona Gruppo da Gestire",
                options=list(group_options.keys()),
                help="Scegli il gruppo da modificare o eliminare"
            )
            
            if not selected_group_name:
                return
            
            selected_group_id = group_options[selected_group_name]
            selected_group = next((g for g in groups if g['id'] == selected_group_id), None)
            
            if not selected_group:
                st.error("❌ Gruppo non trovato.")
                return
            
            # Form di modifica gruppo
            st.markdown(f"### ✏️ Modifica Gruppo: {selected_group['name']}")
            
            with st.form("edit_group_form"):
                new_name = st.text_input(
                    "Nome Gruppo",
                    value=selected_group['name'],
                    help="Nome del gruppo"
                )
                
                new_description = st.text_area(
                    "Descrizione",
                    value=selected_group.get('description', ''),
                    help="Descrizione del gruppo"
                )
                
                new_color = st.color_picker(
                    "Colore",
                    value=selected_group.get('color', '#28A745'),
                    help="Colore del gruppo"
                )
                
                new_is_active = st.checkbox(
                    "Gruppo Attivo",
                    value=selected_group.get('is_active', True),
                    help="Se il gruppo è attivo"
                )
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    update_button = st.form_submit_button(
                        "💾 Aggiorna",
                        use_container_width=True
                    )
                
                with col2:
                    delete_button = st.form_submit_button(
                        "🗑️ Elimina",
                        use_container_width=True
                    )
                
                with col3:
                    cancel_button = st.form_submit_button(
                        "❌ Annulla",
                        use_container_width=True
                    )
                
                if update_button:
                    # Aggiorna il gruppo
                    group_data = {
                        'name': new_name.strip(),
                        'description': new_description.strip(),
                        'color': new_color,
                        'is_active': new_is_active
                    }
                    
                    success = self.db.update_lead_group(selected_group_id, group_data)
                    
                    if success:
                        st.success(f"✅ Gruppo '{new_name}' aggiornato con successo!")
                        
                        # Log attività
                        self.db.log_activity(
                            user_id=self.current_user['user_id'],
                            action='update',
                            entity_type='lead_group',
                            entity_id=selected_group_id,
                            details=f"Aggiornato gruppo '{new_name}'"
                        )
                        
                        st.rerun()
                    else:
                        st.error("❌ Errore nell'aggiornamento del gruppo. Riprova.")
                
                if delete_button:
                    # Conferma eliminazione
                    st.warning("⚠️ Sei sicuro di voler eliminare questo gruppo?")
                    
                    if st.button("🗑️ Conferma Eliminazione", type="primary"):
                        success = self.db.delete_lead_group(selected_group_id)
                        
                        if success:
                            st.success(f"✅ Gruppo '{selected_group['name']}' eliminato con successo!")
                            
                            # Log attività
                            self.db.log_activity(
                                user_id=self.current_user['user_id'],
                                action='delete',
                                entity_type='lead_group',
                                entity_id=selected_group_id,
                                details=f"Eliminato gruppo '{selected_group['name']}'"
                            )
                            
                            st.rerun()
                        else:
                            st.error("❌ Errore nell'eliminazione del gruppo. Riprova.")
                            
        except Exception as e:
            st.error(f"❌ Errore nella gestione del gruppo: {e}")
