# 🤖 Assistente AI - Documentazione

## 📋 Panoramica

L'**Assistente AI** è un modulo integrato nella dashboard DASH_GESTIONE_LEAD che utilizza l'API DeepSeek per fornire supporto intelligente a venditori e team marketing.

## 🚀 Funzionalità Principali

### 1. 📝 **Generatore Script Vendita**
- **Script personalizzati** basati sui dati dei lead
- **4 tipi di script** disponibili:
  - Cold Call
  - Follow-up
  - Gestione Obiezioni
  - Chiusura
- **Script per settore** generici
- **Contesto personalizzato** per maggiore precisione

### 2. 💡 **Consigli Marketing**
- **5 tipi di consigli** disponibili:
  - Ottimizzazione Campagne
  - Generazione Lead
  - Performance Team
  - Strategia Contenuti
  - Analisi Competitiva
- **Analisi qualità lead** con insights automatici
- **Insights competitivi** per settore

### 3. 🔍 **Analisi Lead Intelligente**
- **Score di qualità** automatico (0-100)
- **Categorizzazione** (Hot/Warm/Cold)
- **Analisi comparativa** tra lead
- **Analisi trend** nel tempo
- **Raccomandazioni personalizzate**

## 🔧 Configurazione

### API DeepSeek
```python
# config.py
DEEPSEEK_API_KEY = "sk-f7531fb25e8a4ba3ae22d8b33c7d97a1"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
```

### Parametri AI
```python
AI_ASSISTANT_CONFIG = {
    'max_tokens': 2000,
    'temperature': 0.7,
    'timeout': 30,
    'retry_attempts': 3,
    'cache_responses': True,
    'cache_duration_hours': 24
}
```

## 📁 Struttura File

```
components/ai_assistant/
├── __init__.py                 # Export principali
├── ai_core.py                  # Core DeepSeek integration
├── sales_script_generator.py   # Generatore script vendita
├── marketing_advisor.py        # Consigli marketing
├── lead_analyzer.py            # Analisi lead
└── ai_ui_components.py         # Componenti UI Streamlit
```

## 🎯 Utilizzo

### Accesso all'Assistente AI
1. **Login** alla dashboard
2. **Navigazione** → Clicca su "🤖 AI Assistant"
3. **Seleziona funzionalità** dalla tab desiderata

### Generazione Script Vendita
1. **Tab "📝 Script Vendita"**
2. **Seleziona lead** dal dropdown
3. **Scegli tipo script** (Cold Call, Follow-up, etc.)
4. **Aggiungi contesto** personalizzato (opzionale)
5. **Clicca "🚀 Genera Script"**

### Consigli Marketing
1. **Tab "💡 Consigli Marketing"**
2. **Seleziona tipo consiglio**
3. **Scegli periodo analisi** (7-90 giorni)
4. **Clicca "💡 Genera Consigli Marketing"**

### Analisi Lead
1. **Tab "🔍 Analisi Lead"**
2. **Seleziona lead** per analisi singola
3. **Seleziona multiple lead** per confronto
4. **Clicca "🔍 Analizza Lead"**

## 📊 Score Lead Quality

### Calcolo Score (0-100)
- **Informazioni Contatto** (20%): Nome, cognome, email, telefono
- **Informazioni Azienda** (15%): Azienda, settore, website
- **Budget** (25%): Importo indicato
- **Urgenza Timeline** (15%): Parole chiave nelle note
- **Qualità Fonte** (10%): Referral, website, LinkedIn = alta qualità
- **Storico Interazioni** (15%): Contatti effettuati

### Categorizzazione
- **Hot** (80-100): Lead molto interessato
- **Warm** (60-79): Lead moderatamente interessato  
- **Cold** (0-59): Lead poco interessato

## 🔄 Cache e Performance

### Sistema Cache
- **Cache in memoria** per sessione
- **Durata**: 24 ore (configurabile)
- **Hit rate** monitorabile
- **Pulizia manuale** disponibile

### Ottimizzazioni
- **Retry automatico** (3 tentativi)
- **Backoff esponenziale** per timeout
- **Timeout configurabile** (30 secondi)
- **Gestione errori** robusta

## 🛠️ Troubleshooting

### Problemi Comuni

#### ❌ Timeout API
```
Errore: HTTPSConnectionPool timeout
```
**Soluzione**: Aumentare timeout in `AI_ASSISTANT_CONFIG['timeout']`

#### ❌ Chiave API Non Valida
```
Errore: 401 Unauthorized
```
**Soluzione**: Verificare `DEEPSEEK_API_KEY` in `config.py`

#### ❌ Nessun Lead Disponibile
```
Warning: Nessun lead disponibile
```
**Soluzione**: Creare lead nel database prima di usare l'AI

### Test Connessione
```python
# Test manuale
from components.ai_assistant.ai_core import AIAssistant
ai = AIAssistant()
connection_ok = ai.test_connection()
print(f"Connessione: {'OK' if connection_ok else 'ERRORE'}")
```

## 📈 Metriche e Monitoraggio

### Statistiche Cache
- **Risposte in cache**: Numero totale
- **Cache valide**: Risposte non scadute
- **Hit rate**: Percentuale utilizzo cache

### Log AI
- **Connessioni API**: Successi/fallimenti
- **Generazioni**: Tipo e durata
- **Errori**: Dettagli per debugging

## 🔒 Sicurezza e Privacy

### Gestione Dati
- **API Key**: Configurata in `config.py`
- **Dati Lead**: Utilizzati solo per generazione locale
- **Cache**: Solo in memoria, non persistente
- **Log**: Nessun dato sensibile registrato

### Best Practices
- **Non condividere** la chiave API
- **Monitorare** l'uso delle API
- **Pulire cache** regolarmente
- **Verificare** i risultati AI prima dell'uso

## 🚀 Sviluppi Futuri

### Funzionalità Pianificate
- **Analisi sentiment** dei lead
- **Predizione conversioni** con ML
- **Integrazione CRM** esterni
- **API REST** per integrazioni
- **Dashboard analytics** AI

### Miglioramenti
- **Prompt più specifici** per settori
- **Template personalizzabili**
- **Export script** in PDF/Word
- **Cronologia conversazioni**
- **Notifiche** per lead caldi

## 📞 Supporto

### Contatti
- **Sviluppatore**: Ezio Camporeale
- **Progetto**: DASH_GESTIONE_LEAD
- **Versione**: 1.0.0

### Documentazione
- **README principale**: `/README.md`
- **Struttura progetto**: `/STRUTTURA_PROGETTO.md`
- **Stato attuale**: `/STATO_ATTUALE.md`

---

*Documentazione creata da Ezio Camporeale - Assistente AI v1.0.0*
