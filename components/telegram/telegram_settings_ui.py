#!/usr/bin/env python3
"""
📱 TELEGRAM SETTINGS UI - Dashboard Gestione Lead
Interfaccia per configurazione notifiche Telegram nelle Impostazioni
Creato da Ezio Camporeale
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramSettingsUI:
    """Interfaccia per configurazione Telegram nel Dashboard Lead"""
    
    def __init__(self):
        """Inizializza l'interfaccia Telegram"""
        self.telegram_manager = None
        self.supabase_manager = None
        self._init_managers()
    
    def _init_managers(self):
        """Inizializza i manager necessari"""
        try:
            from components.telegram.telegram_manager import TelegramManager
            from database.database_manager import DatabaseManager
            
            self.telegram_manager = TelegramManager()
            self.supabase_manager = DatabaseManager()
            
            logger.info("✅ TelegramSettingsUI Lead inizializzato correttamente")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione TelegramSettingsUI Lead: {e}")
            st.error(f"❌ Errore inizializzazione: {e}")
    
    def render_telegram_settings(self):
        """Rende l'interfaccia principale per le impostazioni Telegram"""
        st.header("📱 Configurazione Notifiche Telegram")
        st.info("🤖 **BOT TELEGRAM**: Sistema di notifiche automatiche per tutti gli eventi della dashboard Lead")
        
        # Tab per organizzare le impostazioni
        tab_config, tab_notifications, tab_logs = st.tabs([
            "⚙️ Configurazione Bot", "🔔 Impostazioni Notifiche", "📝 Log Notifiche"
        ])
        
        with tab_config:
            self._render_config_tab()
        
        with tab_notifications:
            self._render_notification_toggles_tab()
        
        with tab_logs:
            self._render_notification_logs_tab()
    
    def _render_config_tab(self):
        """Rende il tab per la configurazione del bot"""
        st.subheader("⚙️ Configurazione Bot Telegram")
        
        if not self.telegram_manager:
            st.error("❌ TelegramManager non disponibile")
            return
        
        # Mostra stato attuale
        status = self.telegram_manager.get_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Stato Attuale:**")
            if status['is_configured']:
                st.success("✅ Bot configurato e operativo")
                st.info(f"🔗 Chat ID: `{status['chat_id']}`")
            else:
                st.warning("⚠️ Bot non configurato")
        
        with col2:
            st.markdown("**🔧 Configurazione:**")
            
            # Form per configurazione
            with st.form("telegram_config_form"):
                bot_token = st.text_input(
                    "🤖 Bot Token",
                    value=status['bot_token'] or "",
                    type="password",
                    help="Token del bot ottenuto da @BotFather"
                )
                
                chat_id = st.text_input(
                    "💬 Chat ID",
                    value=status['chat_id'] or "",
                    help="ID del canale o gruppo dove inviare le notifiche"
                )
                
                submitted = st.form_submit_button("💾 Salva Configurazione", type="primary")
                
                if submitted:
                    if bot_token and chat_id:
                        success, message = self.telegram_manager.save_configuration(bot_token, chat_id)
                        if success:
                            st.success("✅ Configurazione salvata con successo!")
                            st.rerun()
                        else:
                            st.error(f"❌ Errore salvataggio: {message}")
                    else:
                        st.error("❌ Inserisci sia Bot Token che Chat ID")
        
        # Test connessione
        if status['is_configured']:
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🧪 Test Connessione", use_container_width=True):
                    success, message = self.telegram_manager.test_connection()
                    if success:
                        st.success("✅ Connessione riuscita!")
                    else:
                        st.error(f"❌ Errore connessione: {message}")
            
            with col2:
                if st.button("📤 Invia Test", use_container_width=True):
                    success, message = self.telegram_manager.send_message("🧪 **Test Notifica Lead**\n\nQuesta è una notifica di test dal sistema Dashboard Lead!")
                    if success:
                        st.success("✅ Messaggio di test inviato!")
                    else:
                        st.error(f"❌ Errore invio: {message}")
            
            with col3:
                if st.button("🗑️ Reset Config", use_container_width=True):
                    if st.session_state.get('confirm_reset', False):
                        self.telegram_manager.bot_token = None
                        self.telegram_manager.chat_id = None
                        self.telegram_manager.is_configured = False
                        st.success("✅ Configurazione resettata!")
                        st.rerun()
                    else:
                        st.session_state.confirm_reset = True
                        st.warning("⚠️ Clicca di nuovo per confermare il reset")
    
    def _render_notification_toggles_tab(self):
        """Rende il tab per le impostazioni delle notifiche"""
        st.subheader("🔔 Impostazioni Notifiche")
        st.info("🎛️ **CONTROLLO NOTIFICHE**: Abilita/disabilita le notifiche per ogni tipo di evento")
        
        # Carica impostazioni attuali
        notification_settings = self._load_notification_settings()
        
        # Organizza le notifiche per categoria
        st.markdown("### 👤 Lead")
        col1, col2 = st.columns(2)
        
        with col1:
            lead_new = st.checkbox(
                "🆕 Nuovo lead inserito",
                value=notification_settings.get('lead_new_lead', True),
                key="lead_new_lead"
            )
            lead_status = st.checkbox(
                "📊 Cambio stato lead",
                value=notification_settings.get('lead_status_changed', True),
                key="lead_status_changed"
            )
        
        with col2:
            lead_assigned = st.checkbox(
                "👥 Lead assegnato",
                value=notification_settings.get('lead_assigned', True),
                key="lead_assigned"
            )
            lead_daily = st.checkbox(
                "📊 Report giornaliero lead",
                value=notification_settings.get('lead_daily_report', False),
                key="lead_daily_report"
            )
        
        st.markdown("### 📋 Task")
        col1, col2 = st.columns(2)
        
        with col1:
            task_new = st.checkbox(
                "🆕 Nuovo task creato",
                value=notification_settings.get('task_new_task', True),
                key="task_new_task"
            )
            task_completed = st.checkbox(
                "✅ Task completato",
                value=notification_settings.get('task_completed', True),
                key="task_completed"
            )
        
        with col2:
            task_due = st.checkbox(
                "⏰ Task in scadenza",
                value=notification_settings.get('task_due_soon', True),
                key="task_due_soon"
            )
            task_daily = st.checkbox(
                "📊 Report giornaliero task",
                value=notification_settings.get('task_daily_report', False),
                key="task_daily_report"
            )
        
        st.markdown("### 👥 Utenti")
        col1, col2 = st.columns(2)
        
        with col1:
            user_new = st.checkbox(
                "🆕 Nuovo utente registrato",
                value=notification_settings.get('user_new_user', True),
                key="user_new_user"
            )
            user_login = st.checkbox(
                "🔐 Accesso utente",
                value=notification_settings.get('user_login', False),
                key="user_login"
            )
        
        with col2:
            user_daily = st.checkbox(
                "📊 Report giornaliero utenti",
                value=notification_settings.get('user_daily_report', False),
                key="user_daily_report"
            )
        
        # Pulsante salva
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("💾 Salva Impostazioni Notifiche", type="primary", use_container_width=True):
                settings = {
                    # Lead
                    'lead_new_lead': lead_new,
                    'lead_status_changed': lead_status,
                    'lead_assigned': lead_assigned,
                    'lead_daily_report': lead_daily,
                    
                    # Task
                    'task_new_task': task_new,
                    'task_completed': task_completed,
                    'task_due_soon': task_due,
                    'task_daily_report': task_daily,
                    
                    # Utenti
                    'user_new_user': user_new,
                    'user_login': user_login,
                    'user_daily_report': user_daily,
                }
                
                self._save_notification_settings(settings)
    
    def _render_notification_logs_tab(self):
        """Rende il tab per i log delle notifiche"""
        st.subheader("📝 Log Notifiche")
        st.info("📊 **STORICO NOTIFICHE**: Visualizza le notifiche inviate e i loro stati")
        
        if not self.telegram_manager:
            st.error("❌ TelegramManager non disponibile")
            return
        
        # Recupera i log delle notifiche
        logs = self.telegram_manager.get_notification_logs(limit=50)
        
        if logs:
            st.success(f"📋 **{len(logs)} notifiche** trovate negli ultimi log")
            
            # Mostra i log in una tabella
            log_data = []
            for log in logs:
                log_data.append({
                    'Data': log.get('sent_at', 'N/A')[:19],  # Rimuove i millisecondi
                    'Tipo': log.get('notification_type', 'N/A'),
                    'Stato': '✅ Successo' if log.get('status') == 'sent' else '❌ Errore',
                    'Messaggio': log.get('message', 'N/A')[:50] + '...' if len(log.get('message', '')) > 50 else log.get('message', 'N/A'),
                    'Errore': log.get('error_message', 'N/A')[:30] + '...' if log.get('error_message') and len(log.get('error_message', '')) > 30 else log.get('error_message', 'N/A')
                })
            
            st.dataframe(log_data, use_container_width=True)
            
            # Statistiche
            col1, col2, col3, col4 = st.columns(4)
            
            successful = sum(1 for log in logs if log.get('status') == 'sent')
            failed = len(logs) - successful
            
            with col1:
                st.metric("📤 Totale", len(logs))
            with col2:
                st.metric("✅ Successo", successful)
            with col3:
                st.metric("❌ Errori", failed)
            with col4:
                success_rate = (successful / len(logs) * 100) if logs else 0
                st.metric("📊 Success Rate", f"{success_rate:.1f}%")
        else:
            st.info("📋 Nessun log di notifiche trovato")
    
    def _load_notification_settings(self) -> Dict[str, bool]:
        """Carica le impostazioni notifiche dal database"""
        try:
            if not self.supabase_manager:
                logger.warning("⚠️ SupabaseManager non disponibile per caricamento impostazioni Lead")
                return self._get_default_notification_settings()
            
            # Recupera tutte le impostazioni notifiche
            response = self.supabase_manager.supabase.table('notification_settings').select('*').execute()
            
            if response.data:
                settings = {}
                for setting in response.data:
                    settings[setting['notification_type']] = setting.get('is_enabled', True)
                logger.info(f"✅ Caricate {len(settings)} impostazioni notifiche Lead dal database")
                return settings
            else:
                logger.info("📋 Nessuna impostazione notifiche Lead trovata, uso default")
                return self._get_default_notification_settings()
                
        except Exception as e:
            logger.error(f"❌ Errore caricamento impostazioni notifiche Lead: {e}")
            return self._get_default_notification_settings()
    
    def _save_notification_settings(self, settings: Dict[str, bool]):
        """Salva le impostazioni notifiche nel database"""
        try:
            if not self.supabase_manager:
                st.error("❌ SupabaseManager non disponibile per salvataggio impostazioni Lead")
                return
            
            # Prepara i dati per l'inserimento/aggiornamento
            settings_data = []
            for notification_type, is_enabled in settings.items():
                settings_data.append({
                    'notification_type': notification_type,
                    'is_enabled': is_enabled,
                    'updated_at': datetime.now().isoformat()
                })
            
            # Usa upsert per inserire o aggiornare
            response = self.supabase_manager.supabase.table('notification_settings').upsert(
                settings_data, 
                on_conflict='notification_type'
            ).execute()
            
            if response.data:
                st.success(f"✅ Impostazioni notifiche Lead salvate con successo! ({len(settings)} impostazioni)")
                logger.info(f"✅ Salvate {len(settings)} impostazioni notifiche Lead nel database")
            else:
                st.error("❌ Errore salvataggio impostazioni notifiche Lead")
                logger.error("❌ Errore salvataggio impostazioni notifiche Lead")
                
        except Exception as e:
            st.error(f"❌ Errore salvataggio impostazioni Lead: {e}")
            logger.error(f"❌ Errore salvataggio impostazioni notifiche Lead: {e}")
    
    def _get_default_notification_settings(self) -> Dict[str, bool]:
        """Restituisce le impostazioni notifiche di default per Lead"""
        return {
            # Lead
            'lead_new_lead': True,
            'lead_status_changed': True,
            'lead_assigned': True,
            'lead_daily_report': False,
            
            # Task
            'task_new_task': True,
            'task_completed': True,
            'task_due_soon': True,
            'task_daily_report': False,
            
            # Utenti
            'user_new_user': True,
            'user_login': False,
            'user_daily_report': False,
        }
