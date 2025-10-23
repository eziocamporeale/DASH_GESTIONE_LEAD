# 📱 Sistema Notifiche Telegram - Dashboard Gestione Lead

## 🎯 Panoramica

Sistema di notifiche Telegram completamente integrato nel Dashboard Gestione Lead, basato sull'implementazione del Dashboard Gestione CPA.

## ✅ Implementazione Completata

### 📁 File Creati

1. **`components/telegram/telegram_manager.py`** - Gestore principale per le notifiche Telegram
2. **`components/telegram/telegram_settings_ui.py`** - Interfaccia per configurazione Telegram
3. **`components/telegram/__init__.py`** - Modulo Telegram
4. **`database/telegram_schema.sql`** - Schema SQL per database locale
5. **`database/init_telegram_tables.py`** - Script inizializzazione tabelle locali
6. **`setup_telegram_supabase.sql`** - Script SQL per Supabase
7. **`setup_telegram_supabase.py`** - Script Python per setup Supabase
8. **`test_telegram_integration.py`** - Script di test integrazione

### 🔧 Modifiche ai File Esistenti

1. **`components/settings/settings_manager.py`** - Aggiunto tab Telegram
2. **`components/leads/lead_form.py`** - Integrate notifiche per nuovi lead

## 🚀 Setup e Configurazione

### Passo 1: Creare le Tabelle in Supabase

1. Vai all'interfaccia SQL di Supabase
2. Esegui il contenuto del file `setup_telegram_supabase.sql`
3. Verifica che le tabelle siano state create:
   - `telegram_config`
   - `notification_settings`
   - `notification_logs`

### Passo 2: Configurare il Bot Telegram

1. Crea un bot con @BotFather su Telegram
2. Ottieni il token del bot
3. Aggiungi il bot al tuo canale/gruppo
4. Ottieni il Chat ID del canale/gruppo

### Passo 3: Configurare nella Dashboard

1. Vai alle **Impostazioni** → **📱 Telegram**
2. Inserisci il **Bot Token** e **Chat ID**
3. Testa la connessione
4. Configura le notifiche desiderate

## 📋 Tipi di Notifiche Supportate

### 👤 Lead
- **`lead_new_lead`** - Nuovo lead inserito
- **`lead_status_changed`** - Cambio stato lead
- **`lead_assigned`** - Lead assegnato
- **`lead_daily_report`** - Report giornaliero lead

### 📋 Task
- **`task_new_task`** - Nuovo task creato
- **`task_completed`** - Task completato
- **`task_due_soon`** - Task in scadenza
- **`task_daily_report`** - Report giornaliero task

### 👥 Utenti
- **`user_new_user`** - Nuovo utente registrato
- **`user_login`** - Accesso utente
- **`user_daily_report`** - Report giornaliero utenti

## 🧪 Test e Verifica

### Eseguire i Test

```bash
cd DASH_GESTIONE_LEAD
python3 test_telegram_integration.py
```

### Test Manuale

1. Configura il bot Telegram
2. Crea un nuovo lead
3. Verifica che arrivi la notifica
4. Controlla i log nelle Impostazioni

## 🔧 Utilizzo Programmatico

### Inviare Notifica Personalizzata

```python
from components.telegram.telegram_manager import TelegramManager

telegram_manager = TelegramManager()

# Invia notifica per nuovo lead
success, message = telegram_manager.send_notification('new_lead', {
    'nome': 'Mario Rossi',
    'email': 'mario@example.com',
    'telefono': '+39 123 456 789',
    'broker': 'Test Broker',
    'fonte': 'Website',
    'priority': 'Media',
    'note': 'Lead di test',
    'created_by': 'Admin User'
})

if success:
    print("✅ Notifica inviata!")
else:
    print(f"❌ Errore: {message}")
```

### Inviare Messaggio Diretto

```python
# Invia messaggio diretto
success, message = telegram_manager.send_message("🧪 **Test**\n\nMessaggio di test!")
```

## 📊 Monitoraggio

### Log delle Notifiche

- Vai alle **Impostazioni** → **📱 Telegram** → **📝 Log Notifiche**
- Visualizza tutte le notifiche inviate
- Controlla il tasso di successo
- Identifica eventuali errori

### Statistiche

- **Totale notifiche** inviate
- **Tasso di successo** (%)
- **Notifiche fallite** con dettagli errore
- **Ultime notifiche** inviate

## 🛠️ Risoluzione Problemi

### Bot Non Configurato

```
❌ Configurazione Telegram non completa
```

**Soluzione**: Configura Bot Token e Chat ID nelle Impostazioni

### Errore Connessione

```
❌ Timeout connessione Telegram
```

**Soluzione**: 
- Verifica che il token sia corretto
- Controlla la connessione internet
- Verifica che il bot sia attivo

### Chat ID Non Valido

```
❌ Errore invio: Bad Request: chat not found
```

**Soluzione**:
- Assicurati che il bot sia aggiunto al canale/gruppo
- Verifica che il Chat ID sia corretto (inizia con -100 per i canali)
- Controlla che il bot abbia i permessi per inviare messaggi

### Tabelle Non Trovate

```
❌ Could not find the table 'telegram_config'
```

**Soluzione**: Esegui lo script SQL `setup_telegram_supabase.sql` in Supabase

## 🔄 Sincronizzazione con Dashboard CPA

Il sistema è stato implementato seguendo la stessa struttura del Dashboard Gestione CPA per garantire:

- **Consistenza** nell'interfaccia utente
- **Compatibilità** tra i due sistemi
- **Manutenibilità** del codice
- **Facilità** di aggiornamenti futuri

## 📈 Prossimi Sviluppi

### Funzionalità Future

1. **Notifiche Programmate** - Report automatici giornalieri/settimanali
2. **Template Personalizzati** - Messaggi personalizzabili per tipo
3. **Integrazione Multi-Bot** - Supporto per più bot Telegram
4. **Analytics Avanzate** - Statistiche dettagliate sulle notifiche
5. **Webhook Telegram** - Ricezione messaggi dal bot

### Miglioramenti

1. **Retry Automatico** - Tentativi automatici per notifiche fallite
2. **Rate Limiting** - Controllo frequenza invio messaggi
3. **Caching** - Cache per configurazioni e impostazioni
4. **Batch Notifications** - Invio notifiche in batch

## 📞 Supporto

Per problemi o domande:

1. Controlla i log delle notifiche
2. Verifica la configurazione del bot
3. Testa la connessione
4. Controlla i permessi Supabase

---

**Creato da Ezio Camporeale**  
**Data**: 23 Ottobre 2025  
**Versione**: 1.0
