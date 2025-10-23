#!/usr/bin/env python3
"""
Componente Settings Manager per DASH_GESTIONE_LEAD
Gestione impostazioni sistema
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
from .excel_importer import render_excel_importer
from components.telegram.telegram_settings_ui import TelegramSettingsUI

class SettingsManager:
    """Gestisce le impostazioni del sistema"""
    
    def __init__(self):
        """Inizializza il gestore impostazioni"""
        self.db = DatabaseManager()
        self.current_user = get_current_user()
    
    def render_settings_page(self):
        """Renderizza la pagina principale delle impostazioni"""
        
        st.markdown("## ⚙️ Impostazioni Sistema")
        st.markdown("Gestisci le configurazioni del sistema")
        
        # Tab per diverse categorie di impostazioni
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏢 Azienda", "📧 Notifiche", "📱 Telegram", "🔧 Sistema", "📊 Backup", "📊 Import Excel"])
        
        with tab1:
            self.render_company_settings()
        
        with tab2:
            self.render_notification_settings()
        
        with tab3:
            self.render_telegram_settings()
        
        with tab4:
            self.render_system_settings()
        
        with tab5:
            self.render_backup_settings()
        
        with tab6:
            self.render_excel_import_settings()
    
    def render_company_settings(self):
        """Renderizza le impostazioni aziendali"""
        
        st.markdown("### 🏢 Impostazioni Aziendali")
        
        # Recupera le impostazioni attuali
        settings = self.get_settings_by_category('company')
        
        with st.form("company_settings_form"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input(
                    "Nome Azienda *",
                    value=settings.get('company_name', ''),
                    help="Nome dell'azienda"
                )
                
                company_email = st.text_input(
                    "Email Aziendale *",
                    value=settings.get('company_email', ''),
                    help="Email principale dell'azienda"
                )
                
                company_phone = st.text_input(
                    "Telefono Aziendale",
                    value=settings.get('company_phone', ''),
                    help="Telefono principale dell'azienda"
                )
            
            with col2:
                company_address = st.text_area(
                    "Indirizzo Aziendale",
                    value=settings.get('company_address', ''),
                    height=100,
                    help="Indirizzo completo dell'azienda"
                )
                
                company_website = st.text_input(
                    "Sito Web",
                    value=settings.get('company_website', ''),
                    help="URL del sito web aziendale"
                )
                
                company_logo = st.file_uploader(
                    "Logo Aziendale",
                    type=['png', 'jpg', 'jpeg'],
                    help="Carica il logo dell'azienda"
                )
            
            # Impostazioni fiscali
            st.markdown("#### 📋 Informazioni Fiscali")
            
            col1, col2 = st.columns(2)
            
            with col1:
                vat_number = st.text_input(
                    "Partita IVA",
                    value=settings.get('vat_number', ''),
                    help="Partita IVA dell'azienda"
                )
                
                fiscal_code = st.text_input(
                    "Codice Fiscale",
                    value=settings.get('fiscal_code', ''),
                    help="Codice fiscale dell'azienda"
                )
            
            with col2:
                sdi_code = st.text_input(
                    "Codice SDI",
                    value=settings.get('sdi_code', ''),
                    help="Codice SDI per fatturazione elettronica"
                )
                
                pec_email = st.text_input(
                    "Email PEC",
                    value=settings.get('pec_email', ''),
                    help="Email PEC dell'azienda"
                )
            
            # Pulsanti
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if st.form_submit_button("💾 Salva Impostazioni", use_container_width=True):
                    self.save_company_settings({
                        'company_name': company_name,
                        'company_email': company_email,
                        'company_phone': company_phone,
                        'company_address': company_address,
                        'company_website': company_website,
                        'vat_number': vat_number,
                        'fiscal_code': fiscal_code,
                        'sdi_code': sdi_code,
                        'pec_email': pec_email
                    })
    
    def render_notification_settings(self):
        """Renderizza le impostazioni notifiche"""
        
        st.markdown("### 📧 Impostazioni Notifiche")
        
        # Recupera le impostazioni attuali
        settings = self.get_settings_by_category('notifications')
        
        with st.form("notification_settings_form"):
            
            st.markdown("#### 🔔 Notifiche Email")
            
            col1, col2 = st.columns(2)
            
            with col1:
                email_notifications = st.checkbox(
                    "Abilita Notifiche Email",
                    value=settings.get('email_notifications', True),
                    help="Abilita l'invio di notifiche via email"
                )
                
                smtp_server = st.text_input(
                    "Server SMTP",
                    value=settings.get('smtp_server', ''),
                    help="Server SMTP per l'invio email"
                )
                
                smtp_port = st.number_input(
                    "Porta SMTP",
                    min_value=1,
                    max_value=65535,
                    value=settings.get('smtp_port', 587),
                    help="Porta del server SMTP"
                )
            
            with col2:
                smtp_username = st.text_input(
                    "Username SMTP",
                    value=settings.get('smtp_username', ''),
                    help="Username per l'autenticazione SMTP"
                )
                
                smtp_password = st.text_input(
                    "Password SMTP",
                    value=settings.get('smtp_password', ''),
                    type="password",
                    help="Password per l'autenticazione SMTP"
                )
                
                smtp_use_tls = st.checkbox(
                    "Usa TLS",
                    value=settings.get('smtp_use_tls', True),
                    help="Usa connessione TLS per SMTP"
                )
            
            st.markdown("#### 📱 Notifiche Push")
            
            col1, col2 = st.columns(2)
            
            with col1:
                push_notifications = st.checkbox(
                    "Abilita Notifiche Push",
                    value=settings.get('push_notifications', False),
                    help="Abilita notifiche push nel browser"
                )
                
                notification_sound = st.checkbox(
                    "Suono Notifiche",
                    value=settings.get('notification_sound', True),
                    help="Riproduci suono per le notifiche"
                )
            
            with col2:
                notification_desktop = st.checkbox(
                    "Notifiche Desktop",
                    value=settings.get('notification_desktop', True),
                    help="Mostra notifiche sul desktop"
                )
                
                # Gestisce il caso in cui il valore nel database sia diverso
                current_notification_freq = settings.get('notification_frequency', 'Immediate')
                notification_options = ["Immediate", "Ogni 5 minuti", "Ogni 15 minuti", "Ogni ora"]
                
                try:
                    notification_index = notification_options.index(current_notification_freq)
                except ValueError:
                    notification_index = 0  # Default a Immediate
                
                notification_frequency = st.selectbox(
                    "Frequenza Notifiche",
                    options=notification_options,
                    index=notification_index,
                    help="Frequenza di invio notifiche"
                )
            
            # Pulsanti
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if st.form_submit_button("💾 Salva Notifiche", use_container_width=True):
                    self.save_notification_settings({
                        'email_notifications': email_notifications,
                        'smtp_server': smtp_server,
                        'smtp_port': smtp_port,
                        'smtp_username': smtp_username,
                        'smtp_password': smtp_password,
                        'smtp_use_tls': smtp_use_tls,
                        'push_notifications': push_notifications,
                        'notification_sound': notification_sound,
                        'notification_desktop': notification_desktop,
                        'notification_frequency': notification_frequency
                    })
    
    def render_telegram_settings(self):
        """Renderizza le impostazioni Telegram"""
        try:
            # Inizializza l'interfaccia Telegram
            telegram_ui = TelegramSettingsUI()
            
            # Renderizza le impostazioni Telegram
            telegram_ui.render_telegram_settings()
            
        except Exception as e:
            st.error(f"❌ Errore caricamento impostazioni Telegram: {e}")
            st.info("💡 Assicurati che le tabelle Telegram siano state create nel database")
    
    def render_system_settings(self):
        """Renderizza le impostazioni di sistema"""
        
        st.markdown("### 🔧 Impostazioni Sistema")
        
        # Recupera le impostazioni attuali
        settings = self.get_settings_by_category('system')
        
        with st.form("system_settings_form"):
            
            st.markdown("#### 📊 Interfaccia")
            
            col1, col2 = st.columns(2)
            
            with col1:
                items_per_page = st.number_input(
                    "Elementi per Pagina",
                    min_value=5,
                    max_value=100,
                    value=settings.get('items_per_page', 20),
                    help="Numero di elementi mostrati per pagina"
                )
                
                # Gestisce il tema
                current_theme = settings.get('theme', 'Light')
                theme_options = ["Light", "Dark", "Auto"]
                
                try:
                    theme_index = theme_options.index(current_theme)
                except ValueError:
                    theme_index = 0  # Default a Light
                
                theme = st.selectbox(
                    "Tema",
                    options=theme_options,
                    index=theme_index,
                    help="Tema dell'interfaccia"
                )
                
                # Gestisce la lingua
                current_language = settings.get('language', 'Italiano')
                language_options = ["Italiano", "English", "Español"]
                
                try:
                    language_index = language_options.index(current_language)
                except ValueError:
                    language_index = 0  # Default a Italiano
                
                language = st.selectbox(
                    "Lingua",
                    options=language_options,
                    index=language_index,
                    help="Lingua dell'interfaccia"
                )
            
            with col2:
                auto_refresh = st.checkbox(
                    "Auto Refresh",
                    value=settings.get('auto_refresh', True),
                    help="Aggiorna automaticamente i dati"
                )
                
                refresh_interval = st.number_input(
                    "Intervallo Refresh (secondi)",
                    min_value=30,
                    max_value=3600,
                    value=settings.get('refresh_interval', 300),
                    help="Intervallo di aggiornamento automatico"
                )
                
                show_help_tooltips = st.checkbox(
                    "Mostra Tooltip Aiuto",
                    value=settings.get('show_help_tooltips', True),
                    help="Mostra tooltip di aiuto"
                )
            
            st.markdown("#### 🤖 Automazioni")
            
            col1, col2 = st.columns(2)
            
            with col1:
                auto_assign_leads = st.checkbox(
                    "Assegnazione Automatica Lead",
                    value=settings.get('auto_assign_leads', True),
                    help="Assegna automaticamente i lead"
                )
                
                lead_scoring_enabled = st.checkbox(
                    "Scoring Automatico Lead",
                    value=settings.get('lead_scoring_enabled', True),
                    help="Calcola automaticamente lo score dei lead"
                )
                
                auto_follow_up = st.checkbox(
                    "Follow-up Automatico",
                    value=settings.get('auto_follow_up', True),
                    help="Invia follow-up automatici"
                )
            
            with col2:
                auto_task_creation = st.checkbox(
                    "Creazione Automatica Task",
                    value=settings.get('auto_task_creation', True),
                    help="Crea task automaticamente per i lead"
                )
                
                auto_sequence_trigger = st.checkbox(
                    "Trigger Sequenze Automatiche",
                    value=settings.get('auto_sequence_trigger', True),
                    help="Attiva sequenze automatiche"
                )
                
                auto_cleanup = st.checkbox(
                    "Pulizia Automatica",
                    value=settings.get('auto_cleanup', False),
                    help="Pulisce automaticamente i dati vecchi"
                )
            
            # Pulsanti
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if st.form_submit_button("💾 Salva Sistema", use_container_width=True):
                    self.save_system_settings({
                        'items_per_page': items_per_page,
                        'theme': theme,
                        'language': language,
                        'auto_refresh': auto_refresh,
                        'refresh_interval': refresh_interval,
                        'show_help_tooltips': show_help_tooltips,
                        'auto_assign_leads': auto_assign_leads,
                        'lead_scoring_enabled': lead_scoring_enabled,
                        'auto_follow_up': auto_follow_up,
                        'auto_task_creation': auto_task_creation,
                        'auto_sequence_trigger': auto_sequence_trigger,
                        'auto_cleanup': auto_cleanup
                    })
    
    def render_backup_settings(self):
        """Renderizza le impostazioni backup"""
        
        st.markdown("### 📊 Impostazioni Backup")
        
        # Recupera le impostazioni attuali
        settings = self.get_settings_by_category('backup')
        
        with st.form("backup_settings_form"):
            
            st.markdown("#### 💾 Backup Automatico")
            
            col1, col2 = st.columns(2)
            
            with col1:
                backup_enabled = st.checkbox(
                    "Abilita Backup Automatico",
                    value=settings.get('backup_enabled', True),
                    help="Abilita il backup automatico del database"
                )
                
                # Gestisce il caso in cui il valore nel database sia in minuscolo
                current_frequency = settings.get('backup_frequency', 'Daily')
                frequency_options = ["Daily", "Weekly", "Monthly"]
                
                # Normalizza il valore corrente
                if current_frequency.lower() == 'daily':
                    current_frequency = 'Daily'
                elif current_frequency.lower() == 'weekly':
                    current_frequency = 'Weekly'
                elif current_frequency.lower() == 'monthly':
                    current_frequency = 'Monthly'
                
                try:
                    frequency_index = frequency_options.index(current_frequency)
                except ValueError:
                    frequency_index = 0  # Default a Daily
                
                backup_frequency = st.selectbox(
                    "Frequenza Backup",
                    options=frequency_options,
                    index=frequency_index,
                    help="Frequenza di backup automatico"
                )
                
                backup_time = st.time_input(
                    "Orario Backup",
                    value=datetime.strptime(settings.get('backup_time', '02:00'), '%H:%M').time(),
                    help="Orario per l'esecuzione del backup"
                )
            
            with col2:
                backup_retention_days = st.number_input(
                    "Retention (giorni)",
                    min_value=1,
                    max_value=365,
                    value=settings.get('backup_retention_days', 30),
                    help="Giorni di conservazione dei backup"
                )
                
                backup_compress = st.checkbox(
                    "Comprimi Backup",
                    value=settings.get('backup_compress', True),
                    help="Comprimi i file di backup"
                )
                
                backup_encrypt = st.checkbox(
                    "Cripta Backup",
                    value=settings.get('backup_encrypt', False),
                    help="Cripta i file di backup"
                )
            
            st.markdown("#### 📁 Posizione Backup")
            
            backup_path = st.text_input(
                "Percorso Backup",
                value=settings.get('backup_path', './backups'),
                help="Percorso per salvare i backup"
            )
            
            # Pulsanti
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.form_submit_button("💾 Salva Backup", use_container_width=True):
                    self.save_backup_settings({
                        'backup_enabled': backup_enabled,
                        'backup_frequency': backup_frequency,
                        'backup_time': backup_time.strftime('%H:%M'),
                        'backup_retention_days': backup_retention_days,
                        'backup_compress': backup_compress,
                        'backup_encrypt': backup_encrypt,
                        'backup_path': backup_path
                    })
            
            with col2:
                if st.form_submit_button("🔄 Backup Manuale", use_container_width=True):
                    self.create_manual_backup()
    
    def get_settings_by_category(self, category: str) -> Dict:
        """Ottiene le impostazioni per categoria"""
        settings = self.db.get_settings_by_category(category)
        return {s['key']: s['value'] for s in settings}
    
    def save_company_settings(self, settings_data: Dict):
        """Salva le impostazioni aziendali"""
        for key, value in settings_data.items():
            self.db.update_setting(key, value, f"Impostazione aziendale: {key}")
        
        st.success("✅ Impostazioni aziendali salvate con successo!")
    
    def save_notification_settings(self, settings_data: Dict):
        """Salva le impostazioni notifiche"""
        for key, value in settings_data.items():
            self.db.update_setting(key, value, f"Impostazione notifica: {key}")
        
        st.success("✅ Impostazioni notifiche salvate con successo!")
    
    def save_system_settings(self, settings_data: Dict):
        """Salva le impostazioni di sistema"""
        for key, value in settings_data.items():
            self.db.update_setting(key, value, f"Impostazione sistema: {key}")
        
        st.success("✅ Impostazioni sistema salvate con successo!")
    
    def save_backup_settings(self, settings_data: Dict):
        """Salva le impostazioni backup"""
        for key, value in settings_data.items():
            self.db.update_setting(key, value, f"Impostazione backup: {key}")
        
        st.success("✅ Impostazioni backup salvate con successo!")
    
    def create_manual_backup(self):
        """Crea un backup manuale"""
        try:
            backup_path = self.db.backup_database()
            st.success(f"✅ Backup creato con successo: {backup_path}")
        except Exception as e:
            st.error(f"❌ Errore durante il backup: {e}")
    
    def render_excel_import_settings(self):
        """Renderizza le impostazioni di importazione Excel"""
        render_excel_importer()

def render_settings_wrapper():
    """Wrapper per renderizzare le impostazioni"""
    settings = SettingsManager()
    settings.render_settings_page()
