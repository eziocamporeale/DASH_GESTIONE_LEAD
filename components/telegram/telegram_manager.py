#!/usr/bin/env python3
"""
📱 TELEGRAM MANAGER - Dashboard Gestione Lead
Componente per gestione notifiche Telegram nella Dashboard Lead
Gestisce invio messaggi, configurazione bot e logging
Creato da Ezio Camporeale
"""

import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import json
import time
import uuid

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramManager:
    """Gestore per le notifiche Telegram nel Dashboard Lead"""
    
    def __init__(self):
        """Inizializza il gestore Telegram"""
        self.bot_token = None
        self.chat_id = None
        self.is_configured = False
        self.supabase_manager = None
        # Non inizializzare Supabase qui per evitare loop infinito
        # self._init_supabase()
        self._load_configuration()
        logger.info("✅ TelegramManager Lead inizializzato")
    
    def _init_supabase(self):
        """Inizializza la connessione Supabase"""
        try:
            from database.database_manager import DatabaseManager
            self.supabase_manager = DatabaseManager()
            logger.info("✅ Supabase inizializzato per TelegramManager Lead")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Supabase per TelegramManager Lead: {e}")
            self.supabase_manager = None
    
    def _load_configuration(self):
        """Carica la configurazione Telegram dal database"""
        try:
            # Inizializza Supabase solo se necessario
            if not self.supabase_manager:
                self._init_supabase()
            
            if not self.supabase_manager:
                logger.warning("❌ Supabase non disponibile per caricamento configurazione Lead")
                return
            
            # Recupera configurazione Telegram
            response = self.supabase_manager.supabase.table('telegram_config').select('*').execute()
            
            if response.data and len(response.data) > 0:
                config = response.data[0]  # Prendi la prima configurazione
                self.bot_token = config.get('bot_token')
                self.chat_id = config.get('chat_id')
                self.is_configured = bool(self.bot_token and self.chat_id)
                
                if self.is_configured:
                    logger.info("✅ Configurazione Telegram Lead caricata dal database")
                else:
                    logger.warning("⚠️ Configurazione Telegram Lead incompleta")
            else:
                logger.info("📋 Nessuna configurazione Telegram Lead trovata")
                
        except Exception as e:
            logger.error(f"❌ Errore caricamento configurazione Telegram Lead: {e}")
    
    def save_configuration(self, bot_token: str, chat_id: str) -> Tuple[bool, str]:
        """Salva la configurazione Telegram nel database"""
        try:
            if not self.supabase_manager:
                return False, "❌ Supabase non disponibile"
            
            config_data = {
                'bot_token': bot_token,
                'chat_id': chat_id,
                'is_active': True,
                'updated_at': datetime.now().isoformat()
            }
            
            # Controlla se esiste già una configurazione
            existing = self.supabase_manager.supabase.table('telegram_config').select('id').execute()
            
            if existing.data and len(existing.data) > 0:
                # Aggiorna configurazione esistente
                config_id = existing.data[0]['id']
                response = self.supabase_manager.supabase.table('telegram_config').update(config_data).eq('id', config_id).execute()
            else:
                # Crea nuova configurazione
                config_data['id'] = str(uuid.uuid4())
                config_data['created_at'] = datetime.now().isoformat()
                response = self.supabase_manager.supabase.table('telegram_config').insert(config_data).execute()
            
            if response.data:
                # Aggiorna configurazione locale
                self.bot_token = bot_token
                self.chat_id = chat_id
                self.is_configured = True
                
                logger.info("✅ Configurazione Telegram Lead salvata nel database")
                return True, "✅ Configurazione Telegram Lead salvata con successo!"
            else:
                return False, "❌ Errore nel salvataggio della configurazione"
                
        except Exception as e:
            logger.error(f"❌ Errore salvataggio configurazione Telegram Lead: {e}")
            return False, f"❌ Errore nel salvataggio: {e}"
    
    def test_connection(self) -> Tuple[bool, str]:
        """Testa la connessione con il bot Telegram"""
        try:
            if not self.is_configured:
                return False, "❌ Configurazione Telegram non completa"
            
            # Test con getMe
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    bot_name = bot_info['result'].get('first_name', 'Bot')
                    logger.info(f"✅ Connessione Telegram Lead OK - Bot: {bot_name}")
                    return True, f"✅ Connessione OK - Bot: {bot_name}"
                else:
                    return False, f"❌ Errore API Telegram: {bot_info.get('description', 'Errore sconosciuto')}"
            else:
                return False, f"❌ Errore HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            return False, "❌ Timeout connessione Telegram"
        except requests.exceptions.RequestException as e:
            return False, f"❌ Errore di rete: {e}"
        except Exception as e:
            logger.error(f"❌ Errore test connessione Telegram Lead: {e}")
            return False, f"❌ Errore test connessione: {e}"
    
    def send_message(self, message: str, parse_mode: str = "Markdown", 
                     disable_web_page_preview: bool = True) -> Tuple[bool, str]:
        """Invia un messaggio al canale/gruppo Telegram"""
        try:
            if not self.is_configured:
                return False, "❌ Configurazione Telegram non completa"
            
            # Prepara il messaggio
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': disable_web_page_preview
            }
            
            # Invia il messaggio
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    message_id = result['result'].get('message_id')
                    logger.info(f"✅ Messaggio Telegram Lead inviato (ID: {message_id})")
                    
                    # Log del messaggio inviato
                    self._log_notification('message_sent', message, 'sent')
                    
                    return True, f"✅ Messaggio inviato con successo!"
                else:
                    error_desc = result.get('description', 'Errore sconosciuto')
                    logger.error(f"❌ Errore invio Telegram Lead: {error_desc}")
                    self._log_notification('message_failed', message, 'failed', error_desc)
                    return False, f"❌ Errore invio: {error_desc}"
            else:
                error_text = response.text
                logger.error(f"❌ Errore HTTP {response.status_code}: {error_text}")
                self._log_notification('message_failed', message, 'failed', error_text)
                return False, f"❌ Errore HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout invio messaggio Telegram Lead")
            self._log_notification('message_failed', message, 'failed', 'Timeout')
            return False, "❌ Timeout invio messaggio"
        except Exception as e:
            logger.error(f"❌ Errore invio messaggio Telegram Lead: {e}")
            self._log_notification('message_failed', message, 'failed', str(e))
            return False, f"❌ Errore invio: {e}"
    
    def send_notification(self, notification_type: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Invia una notifica formattata basata sul tipo"""
        try:
            # Genera il messaggio basato sul tipo
            message = self._format_notification(notification_type, data)
            
            if not message:
                return False, f"❌ Tipo notifica non supportato: {notification_type}"
            
            # Invia il messaggio
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"❌ Errore invio notifica Lead {notification_type}: {e}")
            return False, f"❌ Errore invio notifica: {e}"
    
    def _format_notification(self, notification_type: str, data: Dict[str, Any]) -> Optional[str]:
        """Formatta il messaggio basato sul tipo di notifica"""
        try:
            if notification_type == "new_lead":
                return self._format_new_lead_message(data)
            elif notification_type == "lead_status_changed":
                return self._format_lead_status_changed_message(data)
            elif notification_type == "lead_assigned":
                return self._format_lead_assigned_message(data)
            elif notification_type == "new_task":
                return self._format_new_task_message(data)
            elif notification_type == "task_completed":
                return self._format_task_completed_message(data)
            elif notification_type == "task_due_soon":
                return self._format_task_due_soon_message(data)
            elif notification_type == "new_user":
                return self._format_new_user_message(data)
            elif notification_type == "user_login":
                return self._format_user_login_message(data)
            elif notification_type == "daily_report":
                return self._format_daily_report_message(data)
            else:
                logger.warning(f"⚠️ Tipo notifica Lead non supportato: {notification_type}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Errore formattazione notifica Lead {notification_type}: {e}")
            return None
    
    def _format_new_lead_message(self, data: Dict[str, Any]) -> str:
        """Formatta messaggio per nuovo lead"""
        priority_emoji = {
            "Alta": "🔴",
            "Media": "🟡", 
            "Bassa": "🟢"
        }
        
        priority = data.get('priority', 'Media')
        emoji = priority_emoji.get(priority, "⚪")
        
        return f"""
👤 *NUOVO LEAD INSERITO*

{emoji} *{data.get('nome', 'N/A')}*
📧 Email: {data.get('email', 'N/A')}
📞 Telefono: {data.get('telefono', 'N/A')}
🏢 Broker: {data.get('broker', 'N/A')}
📊 Fonte: {data.get('fonte', 'N/A')}
🔥 Priorità: *{priority}*
📝 Note: {data.get('note', 'N/A')}

👤 Inserito da: {data.get('created_by', 'N/A')}
⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """.strip()
    
    def _format_lead_status_changed_message(self, data: Dict[str, Any]) -> str:
        """Formatta messaggio per cambio stato lead"""
        status_emoji = {
            "Nuovo": "🆕",
            "Contattato": "📞",
            "Qualificato": "✅",
            "Proposta": "📋",
            "Chiuso": "🎯",
            "Perso": "❌"
        }
        
        old_status = data.get('old_status', 'N/A')
        new_status = data.get('new_status', 'N/A')
        emoji = status_emoji.get(new_status, "📊")
        
        return f"""
{emoji} *STATO LEAD AGGIORNATO*

👤 *{data.get('nome', 'N/A')}*
📊 Da: {old_status} → {new_status}
📧 Email: {data.get('email', 'N/A')}
🏢 Broker: {data.get('broker', 'N/A')}

👤 Aggiornato da: {data.get('updated_by', 'N/A')}
⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """.strip()
    
    def _format_lead_assigned_message(self, data: Dict[str, Any]) -> str:
        """Formatta messaggio per assegnazione lead"""
        return f"""
👥 *LEAD ASSEGNATO*

👤 *{data.get('nome', 'N/A')}*
📧 Email: {data.get('email', 'N/A')}
🏢 Broker: {data.get('broker', 'N/A')}

👤 Assegnato a: *{data.get('assigned_to', 'N/A')}*
👤 Assegnato da: {data.get('assigned_by', 'N/A')}

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """.strip()
    
    def _format_new_task_message(self, data: Dict[str, Any]) -> str:
        """Formatta messaggio per nuovo task"""
        priority_emoji = {
            "Bassa": "🟢",
            "Media": "🟡", 
            "Alta": "🟠",
            "Urgente": "🔴"
        }
        
        priority = data.get('priority', 'Media')
        emoji = priority_emoji.get(priority, "⚪")
        
        return f"""
📋 *NUOVO TASK CREATO*

{emoji} *{data.get('title', 'N/A')}*
📄 {data.get('description', 'N/A')}
🔥 Priorità: *{priority}*
📅 Scadenza: {data.get('due_date', 'N/A')}
👥 Assegnato a: {', '.join(data.get('assigned_to', []))}
👤 Creato da: {data.get('created_by', 'N/A')}

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """.strip()
    
    def _format_task_completed_message(self, data: Dict[str, Any]) -> str:
        """Formatta messaggio per task completato"""
        return f"""
✅ *TASK COMPLETATO*

📋 *{data.get('title', 'N/A')}*
👤 Completato da: {data.get('completed_by', 'N/A')}
📅 Completato il: {data.get('completed_at', 'N/A')}

🎉 Ottimo lavoro!
        """.strip()
    
    def _format_task_due_soon_message(self, data: Dict[str, Any]) -> str:
        """Formatta messaggio per task in scadenza"""
        days_left = data.get('days_left', 0)
        urgency = "🚨" if days_left <= 1 else "⚠️"
        
        return f"""
{urgency} *TASK IN SCADENZA*

📋 *{data.get('title', 'N/A')}*
📅 Scade tra: *{days_left} giorni*
👥 Assegnato a: {', '.join(data.get('assigned_to', []))}
🔥 Priorità: {data.get('priority', 'N/A')}

💡 Ricorda di completarlo in tempo!
        """.strip()
    
    def _format_new_user_message(self, data: Dict[str, Any]) -> str:
        """Formatta messaggio per nuovo utente"""
        return f"""
👤 *NUOVO UTENTE REGISTRATO*

📝 Nome: *{data.get('nome', 'N/A')}*
📧 Email: {data.get('email', 'N/A')}
🔑 Ruolo: {data.get('ruolo', 'N/A')}
🏢 Dipartimento: {data.get('dipartimento', 'N/A')}

📅 Registrato il: {data.get('created_at', 'N/A')}
        """.strip()
    
    def _format_user_login_message(self, data: Dict[str, Any]) -> str:
        """Formatta messaggio per login utente"""
        return f"""
🔐 *ACCESSO UTENTE*

👤 *{data.get('nome', 'N/A')}*
📧 Email: {data.get('email', 'N/A')}
🔑 Ruolo: {data.get('ruolo', 'N/A')}

⏰ Accesso: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """.strip()
    
    def _format_daily_report_message(self, data: Dict[str, Any]) -> str:
        """Formatta messaggio per report giornaliero"""
        return f"""
📊 *REPORT GIORNALIERO LEAD*

📅 Data: {data.get('date', 'N/A')}

👤 *LEAD:*
• Totali: {data.get('leads_total', 0)}
• Nuovi oggi: {data.get('leads_new_today', 0)}
• Qualificati: {data.get('leads_qualified', 0)}
• Chiusi: {data.get('leads_closed', 0)}

📋 *TASK:*
• Totali: {data.get('tasks_total', 0)}
• Completati: {data.get('tasks_completed', 0)}
• In corso: {data.get('tasks_in_progress', 0)}

👥 *UTENTI:*
• Attivi oggi: {data.get('users_active_today', 0)}

Buona giornata! 🚀
        """.strip()
    
    def _log_notification(self, notification_type: str, message: str, status: str, error_message: str = None):
        """Logga la notifica nel database"""
        try:
            if not self.supabase_manager:
                return
            
            log_data = {
                'id': str(uuid.uuid4()),
                'notification_type': notification_type,
                'message': message[:1000],  # Limita lunghezza messaggio
                'status': status,
                'error_message': error_message,
                'sent_at': datetime.now().isoformat(),
                'retry_count': 0
            }
            
            self.supabase_manager.supabase.table('notification_logs').insert(log_data).execute()
            
        except Exception as e:
            logger.error(f"❌ Errore logging notifica Lead: {e}")
    
    def get_notification_logs(self, limit: int = 50) -> List[Dict]:
        """Recupera i log delle notifiche"""
        try:
            if not self.supabase_manager:
                return []
            
            response = self.supabase_manager.supabase.table('notification_logs').select('*').order('sent_at', desc=True).limit(limit).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"❌ Errore recupero log notifiche Lead: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Restituisce lo stato del TelegramManager"""
        return {
            'is_configured': self.is_configured,
            'bot_token_set': bool(self.bot_token),
            'chat_id_set': bool(self.chat_id),
            'supabase_available': bool(self.supabase_manager),
            'bot_token': self.bot_token or "",
            'chat_id': self.chat_id or ""
        }
