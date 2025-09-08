# 📊 Modulo Importazione Excel - Dashboard Gestione Lead

## 🎯 Panoramica

Il modulo di importazione Excel permette di importare clienti/lead da file Excel direttamente nella dashboard. Questa funzionalità è integrata nella sezione **Impostazioni** della dashboard.

## 🚀 Funzionalità

### ✅ Caratteristiche Principali

- **Importazione automatica** di clienti da file Excel (.xlsx, .xls)
- **Mapping automatico** delle colonne Excel ai campi del database
- **Validazione dati** prima dell'importazione
- **Gestione duplicati** con opzioni per saltare o aggiornare
- **Creazione automatica** di task per i nuovi lead
- **Log delle attività** per tracciare le importazioni
- **Anteprima dati** prima dell'importazione
- **Progress bar** durante l'importazione

### 📋 Formato File Excel Supportato

| Colonna | Obbligatorio | Descrizione | Esempio |
|---------|--------------|-------------|---------|
| **Nome** | ✅ | Nome del cliente | Mario |
| **Cognome** | ✅ | Cognome del cliente | Rossi |
| Email | ❌ | Email del cliente | mario.rossi@email.com |
| Telefono | ❌ | Numero di telefono | +39 123 456 7890 |
| Azienda | ❌ | Nome dell'azienda | Azienda SRL |
| Posizione | ❌ | Ruolo/Posizione | CEO |
| Fonte | ❌ | Fonte del lead | Website, Telefono, etc. |
| Categoria | ❌ | Categoria del lead | A, B, C |
| Stato | ❌ | Stato del lead | Nuovo, Qualificato, etc. |
| Priorità | ❌ | Priorità del lead | Bassa, Media, Alta |
| Budget | ❌ | Budget stimato | 10000 |
| Data Chiusura | ❌ | Data chiusura prevista | 2024-12-31 |
| Note | ❌ | Note aggiuntive | Cliente interessato |

## 🛠️ Come Utilizzare

### 1. Accedi alle Impostazioni
1. Vai alla sezione **⚙️ Settings** nella dashboard
2. Seleziona il tab **📊 Import Excel**

### 2. Carica il File Excel
1. Clicca su **📁 Carica File Excel**
2. Seleziona il tuo file Excel (.xlsx o .xls)
3. Il sistema leggerà automaticamente il file

### 3. Verifica il Mapping
1. Controlla l'**Anteprima Dati** per verificare che i dati siano corretti
2. Verifica il **Mapping Colonne** automatico
3. Modifica il mapping se necessario

### 4. Configura le Opzioni
1. **Salta Duplicati**: Salta record con email già esistenti
2. **Aggiorna Esistenti**: Aggiorna record esistenti invece di saltarli
3. **Crea Task Automatici**: Crea task automatici per i nuovi lead
4. **Invia Notifiche**: Invia notifiche per i nuovi lead importati

### 5. Importa i Dati
1. Clicca su **🚀 Importa Clienti**
2. Monitora il progresso con la progress bar
3. Verifica i risultati finali

## 🔧 Configurazione Tecnica

### File Coinvolti

```
DASH_GESTIONE_LEAD/
├── components/settings/
│   ├── excel_importer.py          # Modulo principale importazione
│   └── settings_manager.py        # Integrazione nelle impostazioni
├── database/
│   └── database_manager.py        # Metodi database aggiunti
└── test_excel_import.py           # Test del modulo
```

### Dipendenze Aggiuntive

Il modulo utilizza le seguenti librerie Python:
- `pandas` - Per la manipolazione dei dati
- `openpyxl` - Per la lettura dei file Excel
- `streamlit` - Per l'interfaccia utente

### Metodi Database Aggiunti

- `get_lead_by_email()` - Trova lead per email
- `create_lead_source()` - Crea nuove fonti lead
- `create_lead_category()` - Crea nuove categorie lead
- `get_lead_priorities()` - Ottiene le priorità lead
- `log_activity()` - Registra attività nel log

## 🧪 Test e Debugging

### Eseguire i Test

```bash
cd DASH_GESTIONE_LEAD
python3 test_excel_import.py
```

### File di Esempio

Il test crea automaticamente un file `sample_clients.xlsx` con dati di esempio che puoi usare per testare l'importazione.

### Log degli Errori

Gli errori vengono registrati nel log delle attività del database e mostrati nell'interfaccia utente.

## 📊 Risultati dell'Importazione

Dopo l'importazione, il sistema mostra:

- ✅ **Importati**: Numero di lead importati con successo
- 🔄 **Aggiornati**: Numero di lead esistenti aggiornati
- ⏭️ **Saltati**: Numero di duplicati saltati
- ❌ **Errori**: Numero di errori durante l'importazione

## 🔒 Sicurezza

- **Validazione dati**: Tutti i dati vengono validati prima dell'importazione
- **Controllo duplicati**: Gestione intelligente dei duplicati
- **Log attività**: Tracciamento completo delle operazioni
- **Permessi utente**: Solo utenti autorizzati possono importare dati

## 🚨 Limitazioni e Note

1. **Formato date**: Le date devono essere nel formato YYYY-MM-DD
2. **Email duplicate**: Il sistema rileva automaticamente le email duplicate
3. **Campi obbligatori**: Nome e Cognome sono obbligatori
4. **Dimensioni file**: Non ci sono limiti specifici, ma file molto grandi potrebbero richiedere più tempo
5. **Caratteri speciali**: I caratteri speciali vengono gestiti automaticamente

## 🔄 Aggiornamenti Futuri

Funzionalità pianificate:
- Importazione da CSV
- Template Excel scaricabili
- Importazione programmata
- Validazione avanzata dei dati
- Rollback delle importazioni

## 📞 Supporto

Per problemi o domande:
1. Controlla i log delle attività
2. Verifica il formato del file Excel
3. Esegui i test di debug
4. Contatta l'amministratore del sistema

---

**Creato da Ezio Camporeale**  
*Dashboard Gestione Lead v1.0*
