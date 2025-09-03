#!/usr/bin/env python3
"""
Componente Contact Template per DASH_GESTIONE_LEAD
Gestione template email/SMS
Creato da Ezio Camporeale
"""

import streamlit as st
from typing import Dict, Optional
import sys
from pathlib import Path
from datetime import datetime

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import get_current_user
from config import CUSTOM_COLORS

class ContactTemplate:
    """Gestisce i template di contatto"""
    
    def __init__(self):
        """Inizializza il template di contatto"""
        self.db = DatabaseManager()
        self.current_user = get_current_user()
    
    def render_template_form(self, template_data: Optional[Dict] = None, mode: str = "create"):
        """
        Renderizza il form per creazione/modifica template
        
        Args:
            template_data: Dati del template per modifica (None per nuovo template)
            mode: "create" per nuovo template, "edit" per modifica
        """
        
        # Titolo del form
        title = "📧 Nuovo Template" if mode == "create" else "✏️ Modifica Template"
        st.markdown(f"## {title}")
        
        # Form
        with st.form(f"template_form_{mode}", clear_on_submit=(mode == "create")):
            
            # Informazioni base
            st.markdown("### 📝 Informazioni Template")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    "Nome Template *",
                    value=template_data.get('name', '') if template_data else '',
                    help="Nome identificativo del template"
                )
                
                template_type = st.selectbox(
                    "Tipo *",
                    options=["Email", "SMS", "WhatsApp"],
                    index=["Email", "SMS", "WhatsApp"].index(template_data.get('type', 'Email')) if template_data else 0,
                    help="Tipo di comunicazione"
                )
            
            with col2:
                category = st.selectbox(
                    "Categoria *",
                    options=["Follow-up", "Proposta", "Qualificazione", "Chiusura", "Reminder", "Altro"],
                    index=["Follow-up", "Proposta", "Qualificazione", "Chiusura", "Reminder", "Altro"].index(template_data.get('category', 'Follow-up')) if template_data else 0,
                    help="Categoria del template"
                )
                
                is_active = st.checkbox(
                    "Template Attivo",
                    value=template_data.get('is_active', True) if template_data else True,
                    help="Template disponibile per l'uso"
                )
            
            # Contenuto
            st.markdown("### 📄 Contenuto Template")
            
            subject = st.text_input(
                "Oggetto Email",
                value=template_data.get('subject', '') if template_data else '',
                help="Oggetto dell'email (solo per template email)"
            )
            
            content = st.text_area(
                "Contenuto *",
                value=template_data.get('content', '') if template_data else '',
                height=200,
                help="Contenuto del template. Usa {nome}, {azienda}, {lead_id} per variabili dinamiche"
            )
            
            # Variabili disponibili
            st.markdown("### 🔧 Variabili Disponibili")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **Variabili Lead:**
                - `{nome}` - Nome del lead
                - `{cognome}` - Cognome del lead
                - `{email}` - Email del lead
                - `{telefono}` - Telefono del lead
                - `{azienda}` - Azienda del lead
                - `{posizione}` - Posizione del lead
                """)
            
            with col2:
                st.markdown("""
                **Variabili Sistema:**
                - `{lead_id}` - ID del lead
                - `{data_oggi}` - Data odierna
                - `{utente_nome}` - Nome dell'utente che invia
                - `{utente_email}` - Email dell'utente
                - `{utente_telefono}` - Telefono dell'utente
                """)
            
            # Impostazioni avanzate
            st.markdown("### ⚙️ Impostazioni Avanzate")
            col1, col2 = st.columns(2)
            
            with col1:
                delay_hours = st.number_input(
                    "Ritardo Invio (ore)",
                    min_value=0,
                    max_value=168,  # 1 settimana
                    value=template_data.get('delay_hours', 0) if template_data else 0,
                    help="Ritardo prima dell'invio automatico"
                )
                
                max_retries = st.number_input(
                    "Tentativi Massimi",
                    min_value=1,
                    max_value=5,
                    value=template_data.get('max_retries', 3) if template_data else 3,
                    help="Numero massimo di tentativi di invio"
                )
            
            with col2:
                priority = st.selectbox(
                    "Priorità",
                    options=["Bassa", "Media", "Alta"],
                    index=["Bassa", "Media", "Alta"].index(template_data.get('priority', 'Media')) if template_data else 1,
                    help="Priorità di invio"
                )
                
                # Note
                notes = st.text_area(
                    "Note",
                    value=template_data.get('notes', '') if template_data else '',
                    height=80,
                    help="Note aggiuntive sul template"
                )
            
            # Pulsanti
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                submit_button = st.form_submit_button(
                    "💾 Salva Template" if mode == "create" else "💾 Aggiorna Template",
                    use_container_width=True
                )
            
            with col2:
                cancel_button = st.form_submit_button(
                    "❌ Annulla",
                    use_container_width=True
                )
            
            # Gestione submit
            if submit_button:
                if not name or not content:
                    st.error("❌ Nome e contenuto sono obbligatori!")
                    return None
                
                # Prepara i dati
                form_data = {
                    'name': name.strip(),
                    'type': template_type,
                    'category': category,
                    'subject': subject.strip() if subject else None,
                    'content': content.strip(),
                    'delay_hours': delay_hours,
                    'max_retries': max_retries,
                    'priority': priority,
                    'notes': notes.strip() if notes else None,
                    'is_active': is_active,
                    'created_by': self.current_user['user_id']
                }
                
                # Salva nel database
                if mode == "create":
                    template_id = self.db.create_contact_template(form_data)
                    if template_id:
                        st.success(f"✅ Template '{name}' creato con successo!")
                        
                        # Log attività
                        self.db.log_activity(
                            user_id=self.current_user['user_id'],
                            action='create_template',
                            entity_type='contact_template',
                            entity_id=template_id,
                            details=f"Creato nuovo template: {name}"
                        )
                        
                        return template_id
                    else:
                        st.error("❌ Errore durante la creazione del template")
                        return None
                
                else:  # mode == "edit"
                    if self.db.update_contact_template(template_data['id'], form_data):
                        st.success(f"✅ Template '{name}' aggiornato con successo!")
                        
                        # Log attività
                        self.db.log_activity(
                            user_id=self.current_user['user_id'],
                            action='update_template',
                            entity_type='contact_template',
                            entity_id=template_data['id'],
                            details=f"Aggiornato template: {name}"
                        )
                        
                        return template_data['id']
                    else:
                        st.error("❌ Errore durante l'aggiornamento del template")
                        return None
            
            elif cancel_button:
                st.info("❌ Operazione annullata")
                return None
        
        return None

def render_template_form_wrapper(template_data: Optional[Dict] = None, mode: str = "create"):
    """Wrapper per renderizzare il form template"""
    template = ContactTemplate()
    return template.render_template_form(template_data, mode)

# Test della classe
if __name__ == "__main__":
    st.set_page_config(
        page_title="Test Contact Template",
        page_icon="📧",
        layout="wide"
    )
    
    st.title("🧪 Test Contact Template")
    
    # Test form nuovo template
    st.markdown("### Test Form Nuovo Template")
    template_id = render_template_form_wrapper()
    
    if template_id:
        st.success(f"✅ Template creato con ID: {template_id}")
        
        # Test form modifica template
        st.markdown("### Test Form Modifica Template")
        template_data = {
            'id': template_id,
            'name': 'Follow-up Email',
            'type': 'Email',
            'category': 'Follow-up',
            'subject': 'Follow-up sulla nostra proposta',
            'content': 'Gentile {nome},\n\nGrazie per il suo interesse.\n\nCordiali saluti,\n{utente_nome}',
            'delay_hours': 24,
            'max_retries': 3,
            'priority': 'Media',
            'notes': 'Template per follow-up standard',
            'is_active': True
        }
        
        updated_id = render_template_form_wrapper(template_data, "edit")
        if updated_id:
            st.success(f"✅ Template aggiornato con ID: {updated_id}")
