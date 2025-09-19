#!/usr/bin/env python3
"""
Applicazione Principale DASH_GESTIONE_LEAD
Dashboard per la gestione dei lead aziendali
Creato da Ezio Camporeale
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from config import APP_TITLE, APP_ICON, PAGE_ICON, CUSTOM_COLORS
from components.auth.auth_manager import auth_manager, require_auth, get_current_user
from components.auth.login_form import render_login_form, render_logout_section
from database.database_manager import DatabaseManager
from components.leads.lead_form import render_lead_form_wrapper
from components.leads.lead_table import render_lead_table_wrapper
from components.tasks.task_form import render_task_form_wrapper
from components.tasks.task_board import render_task_board_wrapper
from components.users.user_form import render_user_form_wrapper
from components.users.user_management import render_user_management_wrapper
from components.users.password_manager import render_password_manager_wrapper
from components.groups.lead_group_management import LeadGroupManagement
from components.contacts.contact_template import render_template_form_wrapper
from components.contacts.contact_sequence import render_sequence_form_wrapper, render_sequence_list_wrapper, render_sequence_stats_wrapper
from components.settings.settings_manager import render_settings_wrapper
from components.broker_links.broker_links_manager import BrokerLinksManager
from components.scripts.scripts_manager import ScriptsManager
from components.ai_assistant.ai_ui_components import render_ai_assistant
from components.storage.storage_ui import render_storage_wrapper

# Configurazione pagina
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS per sidebar compatta
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        width: 250px !important;
    }
    [data-testid="stSidebar"] .stSelectbox {
        font-size: 0.9rem;
    }
    [data-testid="stSidebar"] .stMarkdown {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# CSS personalizzato
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        padding: 2rem 0;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        border-radius: 15px;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.1)"/><circle cx="10" cy="60" r="0.5" fill="rgba(255,255,255,0.1)"/><circle cx="90" cy="40" r="0.5" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    .header-content {
        position: relative;
        z-index: 2;
    }
    .header-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #2E86AB;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2E86AB;
    }
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }
    .chart-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def render_header():
    """Renderizza l'header dell'applicazione"""
    st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <div class="header-title">🎯 DASH_GESTIONE_LEAD</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard():
    """Renderizza la dashboard principale"""
    
    # Inizializza il database manager
    db = DatabaseManager()
    
    # Ottieni statistiche
    lead_stats = db.get_lead_stats()
    task_stats = db.get_task_stats()
    
    # Header della dashboard
    st.markdown("## 📊 Dashboard Principale")
    st.markdown("Panoramica generale sui lead e attività")
    
    # Metriche principali
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Gestisce sia formato Supabase (int) che SQLite (list)
        total_leads = lead_stats['total_leads']
        if isinstance(total_leads, list) and total_leads:
            total_leads = total_leads[0]['count']
        elif not isinstance(total_leads, int):
            total_leads = 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_leads}</div>
            <div class="metric-label">Lead Totali</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Gestisce sia formato Supabase (int) che SQLite (list)
        total_tasks = task_stats['total_tasks']
        if isinstance(total_tasks, list) and total_tasks:
            total_tasks = total_tasks[0]['count']
        elif not isinstance(total_tasks, int):
            total_tasks = 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_tasks}</div>
            <div class="metric-label">Task Totali</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Gestisce sia formato Supabase (int) che SQLite (list)
        overdue_tasks = task_stats['overdue_tasks']
        if isinstance(overdue_tasks, list) and overdue_tasks:
            overdue_tasks = overdue_tasks[0]['count']
        elif not isinstance(overdue_tasks, int):
            overdue_tasks = 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #DC3545;">{overdue_tasks}</div>
            <div class="metric-label">Task Scaduti</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Calcola lead nuovi (stato = 1)
        new_leads = 0
        for state in lead_stats['leads_by_state']:
            if state['name'] == 'Nuovo':
                new_leads = state['count']
                break
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #17A2B8;">{new_leads}</div>
            <div class="metric-label">Lead Nuovi</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Grafici
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Lead per Stato")
        if lead_stats['leads_by_state']:
            df_states = pd.DataFrame(lead_stats['leads_by_state'])
            fig_states = px.pie(
                df_states, 
                values='count', 
                names='name',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_states.update_layout(height=400)
            st.plotly_chart(fig_states, width='stretch')
        else:
            st.info("Nessun dato disponibile")
    
    with col2:
        st.markdown("### 📊 Lead per Fonte")
        if lead_stats['leads_by_source']:
            df_sources = pd.DataFrame(lead_stats['leads_by_source'])
            fig_sources = px.bar(
                df_sources,
                x='name',
                y='count',
                color='count',
                color_continuous_scale='Blues'
            )
            fig_sources.update_layout(height=400, xaxis_title="Fonte", yaxis_title="Numero Lead")
            st.plotly_chart(fig_sources, width='stretch')
        else:
            st.info("Nessun dato disponibile")
    
    # Task recenti
    st.markdown("### ✅ Task Recenti")
    # Per utenti non-Admin, limita ai task dei loro gruppi
    current_user = get_current_user()
    if current_user and current_user.get('role_name') != 'Admin':
        recent_tasks = db.get_tasks_for_user_groups(current_user['user_id'], limit=10)
    else:
        recent_tasks = db.get_tasks(limit=10)
    
    if recent_tasks:
        task_df = pd.DataFrame(recent_tasks)
        
        # Gestisce i campi che potrebbero non essere presenti
        if 'state_name' in task_df.columns:
            task_df['stato'] = task_df['state_name']
        else:
            task_df['stato'] = 'N/A'
        
        if 'assigned_first_name' in task_df.columns and 'assigned_last_name' in task_df.columns:
            task_df['assegnato'] = task_df['assigned_first_name'].fillna('') + ' ' + task_df['assigned_last_name'].fillna('')
        else:
            task_df['assegnato'] = 'Non assegnato'
        
        # Mostra solo le colonne rilevanti
        display_columns = ['title', 'stato', 'assegnato', 'due_date']
        available_columns = [col for col in display_columns if col in task_df.columns]
        display_df = task_df[available_columns].head(5)
        st.dataframe(display_df, width='stretch')
    else:
        st.info("Nessun task disponibile")

def render_leads_page():
    """Renderizza la pagina di gestione lead"""
    st.markdown("## 👥 Gestione Lead")
    st.markdown("Gestisci i lead aziendali")
    
    # Controlla se mostrare il form o la tabella
    if st.session_state.get('show_lead_form', False):
        # Mostra il form
        lead_data = st.session_state.get('edit_lead_data', None)
        mode = st.session_state.get('lead_form_mode', 'create')
        
        # Pulsante per tornare alla tabella
        if st.button("← Torna alla Lista Lead"):
            st.session_state['show_lead_form'] = False
            if 'edit_lead_data' in st.session_state:
                del st.session_state['edit_lead_data']
            if 'lead_form_mode' in st.session_state:
                del st.session_state['lead_form_mode']
            st.rerun()
        
        # Renderizza il form
        lead_id = render_lead_form_wrapper(lead_data, mode)
        
        if lead_id:
            # Reset dello stato e torna alla tabella
            st.session_state['show_lead_form'] = False
            if 'edit_lead_data' in st.session_state:
                del st.session_state['edit_lead_data']
            if 'lead_form_mode' in st.session_state:
                del st.session_state['lead_form_mode']
            st.rerun()
    
    else:
        # Mostra la tabella
        render_lead_table_wrapper()

def render_tasks_page():
    """Renderizza la pagina di gestione task"""
    st.markdown("## ✅ Gestione Task")
    st.markdown("Gestisci le attività e i task")
    
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
        
        # Renderizza il form
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
        render_task_board_wrapper()

def render_users_page():
    """Renderizza la pagina di gestione utenti"""
    # CONTROLLO SICUREZZA: Solo Admin può accedere alla gestione utenti
    auth_manager.require_role(['Admin'])
    
    st.markdown("## 👤 Gestione Utenti")
    st.markdown("Gestisci utenti, ruoli e dipartimenti")
    
    # Controlla se mostrare il form utente, gestione password o la gestione principale
    if st.session_state.get('show_user_form', False):
        # Mostra il form utente
        user_data = st.session_state.get('edit_user_data', None)
        mode = st.session_state.get('user_form_mode', 'create')
        
        # Pulsante per tornare alla gestione
        if st.button("← Torna alla Gestione Utenti"):
            st.session_state['show_user_form'] = False
            if 'edit_user_data' in st.session_state:
                del st.session_state['edit_user_data']
            if 'user_form_mode' in st.session_state:
                del st.session_state['user_form_mode']
            st.rerun()
        
        # Renderizza il form
        user_id = render_user_form_wrapper(user_data, mode)
        
        if user_id:
            # Reset dello stato e torna alla gestione
            st.session_state['show_user_form'] = False
            if 'edit_user_data' in st.session_state:
                del st.session_state['edit_user_data']
            if 'user_form_mode' in st.session_state:
                del st.session_state['user_form_mode']
            st.rerun()
    
    elif st.session_state.get('show_password_form', False):
        # Mostra la gestione password
        render_password_manager_wrapper()
    
    else:
        # Mostra la gestione utenti principale
        render_user_management_wrapper()

def render_groups_page():
    """Renderizza la pagina di gestione gruppi lead"""
    # CONTROLLO SICUREZZA: Solo Admin può accedere alla gestione gruppi
    auth_manager.require_role(['Admin'])
    
    # Inizializza il gestore gruppi
    groups_manager = LeadGroupManagement()
    groups_manager.render_groups_page()

def render_contacts_page():
    """Renderizza la pagina di gestione contatti"""
    st.markdown("## 📞 Gestione Contatti")
    st.markdown("Gestisci template e sequenze di contatto")
    
    # Tab per template e sequenze
    tab1, tab2, tab3 = st.tabs(["📧 Template", "📞 Sequenze", "📊 Statistiche"])
    
    with tab1:
        # Controlla se mostrare il form template
        if st.session_state.get('show_template_form', False):
            template_data = st.session_state.get('edit_template_data', None)
            mode = st.session_state.get('template_form_mode', 'create')
            
            # Pulsante per tornare alla lista
            if st.button("← Torna ai Template"):
                st.session_state['show_template_form'] = False
                if 'edit_template_data' in st.session_state:
                    del st.session_state['edit_template_data']
                if 'template_form_mode' in st.session_state:
                    del st.session_state['template_form_mode']
                st.rerun()
            
            # Renderizza il form
            template_id = render_template_form_wrapper(template_data, mode)
            
            if template_id:
                # Reset dello stato e torna alla lista
                st.session_state['show_template_form'] = False
                if 'edit_template_data' in st.session_state:
                    del st.session_state['edit_template_data']
                if 'template_form_mode' in st.session_state:
                    del st.session_state['template_form_mode']
                st.rerun()
        
        else:
            # Mostra lista template
            st.markdown("### 📧 Template di Contatto")
            
            # Azioni
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("➕ Nuovo Template", use_container_width=True):
                    st.session_state['show_template_form'] = True
                    st.session_state['template_form_mode'] = 'create'
                    st.rerun()
            
            # Placeholder per lista template
            st.info("📧 Lista template in sviluppo...")
    
    with tab2:
        # Controlla se mostrare il form sequenza
        if st.session_state.get('show_sequence_form', False):
            sequence_data = st.session_state.get('edit_sequence_data', None)
            mode = st.session_state.get('sequence_form_mode', 'create')
            
            # Pulsante per tornare alla lista
            if st.button("← Torna alle Sequenze"):
                st.session_state['show_sequence_form'] = False
                if 'edit_sequence_data' in st.session_state:
                    del st.session_state['edit_sequence_data']
                if 'sequence_form_mode' in st.session_state:
                    del st.session_state['sequence_form_mode']
                st.rerun()
            
            # Renderizza il form
            sequence_id = render_sequence_form_wrapper(sequence_data, mode)
            
            if sequence_id:
                # Reset dello stato e torna alla lista
                st.session_state['show_sequence_form'] = False
                if 'edit_sequence_data' in st.session_state:
                    del st.session_state['edit_sequence_data']
                if 'sequence_form_mode' in st.session_state:
                    del st.session_state['sequence_form_mode']
                st.rerun()
        
        else:
            # Mostra lista sequenze
            st.markdown("### 📞 Sequenze di Contatto")
            
            # Azioni
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("➕ Nuova Sequenza", use_container_width=True):
                    st.session_state['show_sequence_form'] = True
                    st.session_state['sequence_form_mode'] = 'create'
                    st.rerun()
            
            # Lista sequenze
            render_sequence_list_wrapper()
    
    with tab3:
        # Statistiche
        st.markdown("### 📊 Statistiche Contatti")
        render_sequence_stats_wrapper()

def render_reports_page():
    """Renderizza la pagina di report e analytics"""
    st.markdown("## 📊 Report e Analytics")
    st.markdown("Report avanzati e analytics")
    
    # Placeholder per il componente report
    st.info("🚧 Componente report in sviluppo...")
    st.markdown("""
    ### Funzionalità previste:
    - 📈 Report personalizzabili
    - 📊 Grafici interattivi
    - 📤 Export dati
    - 📅 Report temporali
    """)

def render_settings_page():
    """Renderizza la pagina di impostazioni"""
    render_settings_wrapper()

def render_broker_links_page():
    """Renderizza la pagina dei link broker"""
    # Inizializza il database manager e auth manager
    db = DatabaseManager()
    broker_manager = BrokerLinksManager(db, auth_manager)
    broker_manager.render_broker_links_page()

def render_scripts_page():
    """Renderizza la pagina degli script"""
    # Inizializza il database manager
    db = DatabaseManager()
    scripts_manager = ScriptsManager(db)
    scripts_manager.render_scripts_page()

def render_portals_page():
    """Renderizza la pagina dei portali web"""
    st.info("🚧 Modulo Portali in sviluppo - Sarà disponibile prossimamente")
    st.markdown("### 🌐 Portali Web")
    st.markdown("Questa funzionalità è attualmente in fase di sviluppo.")

def render_ai_assistant_page():
    """Renderizza la pagina dell'assistente AI"""
    render_ai_assistant()

def main():
    """Funzione principale dell'applicazione"""
    
    # Verifica autenticazione
    if not auth_manager.is_authenticated():
        render_header()
        user_data = render_login_form()
        if user_data:
            st.rerun()
        return
    
    # Utente autenticato - mostra l'applicazione
    render_header()
    
    # Gestione sidebar temporanea dopo login
    show_sidebar = False
    if st.session_state.get('show_sidebar_temporarily', False):
        show_sidebar = True
        # Decrementa il timer
        timer = st.session_state.get('sidebar_timer', 0)
        if timer > 0:
            st.session_state['sidebar_timer'] = timer - 1
        else:
            # Timer scaduto, nascondi la sidebar
            st.session_state['show_sidebar_temporarily'] = False
            del st.session_state['sidebar_timer']
    
    # Importa il componente del menu centrale
    from components.layout.central_menu import render_central_menu, render_compact_sidebar
    
    # Menu centrale sempre visibile
    page = render_central_menu(st.session_state.get('current_page', '📊 Dashboard'))
    
    # Sidebar compatta solo con info utente (visibile temporaneamente dopo login)
    if show_sidebar:
        render_compact_sidebar()
    
    # Contenuto principale basato sulla pagina selezionata
    if page == "📊 Dashboard":
        render_dashboard()
    elif page == "👥 Lead":
        render_leads_page()
    elif page == "✅ Task":
        render_tasks_page()
    elif page == "🤖 AI Assistant":
        render_ai_assistant_page()
    elif page == "🌐 Portali":
        render_portals_page()
    elif page == "👤 Utenti":
        render_users_page()
    elif page == "👥 Gruppi":
        render_groups_page()
    elif page == "📞 Contatti":
        render_contacts_page()
    elif page == "🔗 Broker":
        render_broker_links_page()
    elif page == "📝 Script":
        render_scripts_page()
    elif page == "📁 Storage":
        render_storage_wrapper()
    elif page == "📊 Report":
        render_reports_page()
    elif page == "⚙️ Settings":
        render_settings_page()

if __name__ == "__main__":
    main()
