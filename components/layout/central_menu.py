#!/usr/bin/env python3
"""
Componente Menu Centrale per DASH_GESTIONE_LEAD
Menu di navigazione posizionato al centro della dashboard, sempre visibile
Creato da Ezio Camporeale
"""

import streamlit as st
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from components.auth.auth_manager import auth_manager

def render_central_menu(current_page: str = "📊 Dashboard") -> str:
    """
    Renderizza il menu centrale sempre visibile
    
    Args:
        current_page: Pagina corrente selezionata
        
    Returns:
        str: Pagina selezionata
    """
    
    # CSS per il menu centrale sempre visibile
    st.markdown("""
    <style>
    .central-menu {
        position: sticky;
        top: 0;
        z-index: 1000;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 0;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .menu-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    .menu-title {
        text-align: center;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .menu-buttons {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .menu-btn {
        background: rgba(255,255,255,0.2);
        color: white;
        border: 2px solid rgba(255,255,255,0.3);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
    }
    .menu-btn:hover {
        background: rgba(255,255,255,0.3);
        border-color: rgba(255,255,255,0.5);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .menu-btn.active {
        background: rgba(255,255,255,0.9);
        color: #667eea;
        border-color: white;
        font-weight: bold;
    }
    .menu-btn.active:hover {
        background: white;
        color: #667eea;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Container del menu centrale
    st.markdown("""
    <div class="central-menu">
        <div class="menu-container">
            <div class="menu-buttons">
    """, unsafe_allow_html=True)
    
    # Ottieni le opzioni del menu basate sui permessi utente
    current_user = auth_manager.get_current_user()
    menu_options = [
        ("📊 Dashboard", "📊 Dashboard"),
        ("👥 Lead", "👥 Lead"), 
        ("✅ Task", "✅ Task"),
        ("🤖 AI Assistant", "🤖 AI Assistant"),
        ("🌐 Portali", "🌐 Portali"),
        ("📞 Contatti", "📞 Contatti"),
        ("🔗 Broker", "🔗 Broker"),
        ("📝 Script", "📝 Script"),
        ("📊 Report", "📊 Report"),
        ("⚙️ Settings", "⚙️ Settings")
    ]
    
    # Solo Admin può vedere la gestione utenti
    if current_user and current_user.get('role_name') == 'Admin':
        menu_options.insert(3, ("👤 Utenti", "👤 Utenti"))
    
    # Crea i pulsanti del menu direttamente
    cols = st.columns(len(menu_options))
    selected_page = current_page
    
    for i, (display_name, page_value) in enumerate(menu_options):
        with cols[i]:
            is_active = page_value == current_page
            button_type = "primary" if is_active else "secondary"
            
            if st.button(
                display_name, 
                key=f"menu_btn_{page_value}",
                help=f"Vai alla sezione {display_name}",
                use_container_width=True,
                type=button_type
            ):
                # Imposta la nuova pagina direttamente
                selected_page = page_value
                st.session_state['current_page'] = page_value
                st.rerun()
    
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return selected_page

def render_compact_sidebar():
    """
    Renderizza una sidebar compatta solo con info utente e logout
    """
    with st.sidebar:
        st.markdown("### 👤 Utente")
        
        # Informazioni utente
        current_user = auth_manager.get_current_user()
        if current_user:
            st.markdown(f"**👤 {current_user.get('username', 'N/A')}**")
            st.markdown(f"📧 {current_user.get('email', 'N/A')}")
            st.markdown(f"👑 {current_user.get('role_name', 'N/A')}")
            st.markdown(f"🏢 {current_user.get('company', 'N/A')}")
        
        st.markdown("---")
        
        # Pulsante logout
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            auth_manager.logout()
            st.rerun()
