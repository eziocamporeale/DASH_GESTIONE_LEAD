# Configurazione DASH_GESTIONE_LEAD
import os
from pathlib import Path

# Percorsi base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
COMPONENTS_DIR = BASE_DIR / "components"
UTILS_DIR = BASE_DIR / "utils"
LOCALES_DIR = BASE_DIR / "locales"

# Database
DATABASE_PATH = DATA_DIR / "leads_database.db"

# Configurazione Supabase
SUPABASE_URL = "https://xjjmpurdjqwjomxmqqks.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhqam1wdXJkanF3am9teG1xcWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY4OTI2NzMsImV4cCI6MjA3MjQ2ODY3M30.grFLiS6zmYGx5wNxuFKND5qHeYc71Nl_Tf8Sp4ce-ao"

# Configurazione database (SQLite per sviluppo locale, Supabase per produzione)
USE_SUPABASE = True  # Cambia a False per usare SQLite locale

# Configurazione app
APP_TITLE = "DASH_GESTIONE_LEAD"
APP_ICON = "🎯"
PAGE_ICON = "🎯"

# Configurazione tema
CUSTOM_COLORS = {
    'primary': '#2E86AB',      # Blu principale
    'secondary': '#A23B72',    # Viola secondario
    'success': '#28A745',      # Verde per successi
    'info': '#17A2B8',         # Azzurro per info
    'warning': '#FFC107',      # Giallo per warning
    'danger': '#DC3545',       # Rosso per errori
    'light': '#F8F9FA',        # Grigio chiaro
    'dark': '#343A40',         # Grigio scuro
    'white': '#FFFFFF',        # Bianco
    'lead_hot': '#DC3545',     # Rosso per lead caldi
    'lead_warm': '#FFC107',    # Giallo per lead tiepidi
    'lead_cold': '#6C757D',    # Grigio per lead freddi
    'neutral': '#6C757D'       # Grigio neutro
}

# Configurazione autenticazione
AUTH_CONFIG = {
    'cookie_name': 'lead_dashboard_auth',
    'cookie_key': 'lead_dashboard_key',
    'cookie_expiry_days': 30,
    'preauthorized': ['admin@example.com']
}

# Configurazione lead
LEAD_STATES = [
    {'id': 1, 'name': 'Nuovo', 'color': '#17A2B8', 'order': 1},
    {'id': 2, 'name': 'Contattato', 'color': '#FFC107', 'order': 2},
    {'id': 3, 'name': 'Qualificato', 'color': '#28A745', 'order': 3},
    {'id': 4, 'name': 'Proposta', 'color': '#FD7E14', 'order': 4},
    {'id': 5, 'name': 'Chiuso', 'color': '#6C757D', 'order': 5},
    {'id': 6, 'name': 'Perso', 'color': '#DC3545', 'order': 6}
]

LEAD_PRIORITIES = [
    {'id': 1, 'name': 'Alta', 'color': '#DC3545'},
    {'id': 2, 'name': 'Media', 'color': '#FFC107'},
    {'id': 3, 'name': 'Bassa', 'color': '#28A745'}
]

LEAD_CATEGORIES = [
    {'id': 1, 'name': 'Caldo', 'color': '#DC3545', 'description': 'Lead molto interessato'},
    {'id': 2, 'name': 'Tiepido', 'color': '#FFC107', 'description': 'Lead moderatamente interessato'},
    {'id': 3, 'name': 'Freddo', 'color': '#6C757D', 'description': 'Lead poco interessato'}
]

# Configurazione ruoli
USER_ROLES = [
    {'id': 1, 'name': 'Admin', 'permissions': ['all']},
    {'id': 2, 'name': 'Manager', 'permissions': ['manage_leads', 'manage_team', 'view_reports']},
    {'id': 3, 'name': 'Setter', 'permissions': ['create_leads', 'edit_leads', 'view_assigned']},
    {'id': 4, 'name': 'Closer', 'permissions': ['edit_leads', 'view_assigned', 'close_deals']},
    {'id': 5, 'name': 'Viewer', 'permissions': ['view_leads', 'view_reports']}
]

# Configurazione task
TASK_STATES = [
    {'id': 1, 'name': 'Da Fare', 'color': '#17A2B8'},
    {'id': 2, 'name': 'In Corso', 'color': '#FFC107'},
    {'id': 3, 'name': 'Completato', 'color': '#28A745'},
    {'id': 4, 'name': 'Annullato', 'color': '#DC3545'}
]

# Configurazione paginazione
ITEMS_PER_PAGE = 20

# Configurazione backup
BACKUP_DIR = BASE_DIR / "backups"
BACKUP_RETENTION_DAYS = 30

# Configurazione logging
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "logs" / "app.log"

# Configurazione Assistente AI DeepSeek
DEEPSEEK_API_KEY = "sk-f7531fb25e8a4ba3ae22d8b33c7d97a1"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Configurazione AI Assistant
AI_ASSISTANT_CONFIG = {
    'max_tokens': 1500,
    'temperature': 0.7,
    'timeout': 60,
    'retry_attempts': 3,
    'cache_responses': True,
    'cache_duration_hours': 24
}

# Prompt templates per AI Assistant
AI_PROMPTS = {
    'sales_script': """
    Genera uno script di vendita per:
    Lead: {lead_data}
    Settore: {industry}
    Budget: {budget}
    Fonte: {source}
    Stato: {status}
    
    Includi: apertura, presentazione valore, gestione obiezioni, chiusura.
    Risposta in italiano, professionale.
    """,
    
    'marketing_advice': """
    Analizza questi dati marketing e fornisci consigli:
    Lead: {leads_data}
    Campagne: {campaign_data}
    Team: {team_metrics}
    
    Suggerisci: trend, miglioramenti, campagne, ottimizzazioni.
    Risposta in italiano, pratica.
    """,
    
    'lead_analysis': """
    Analizza questo lead:
    Lead: {lead_data}
    Contatti: {contact_history}
    Attività: {recent_activities}
    
    Fornisci: score qualità, probabilità conversione, approccio consigliato.
    Risposta in italiano, dettagliata.
    """
}

# Creazione directory necessarie
def create_directories():
    """Crea le directory necessarie per il funzionamento dell'app"""
    directories = [DATA_DIR, COMPONENTS_DIR, UTILS_DIR, LOCALES_DIR, BACKUP_DIR, LOG_FILE.parent]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Inizializzazione
if __name__ == "__main__":
    create_directories()
    print("✅ Directory create con successo")
