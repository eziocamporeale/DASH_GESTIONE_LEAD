# 📁 Sezione Storage - DASH_GESTIONE_LEAD

## Panoramica
La sezione Storage permette la gestione centralizzata dei file nel sistema DASH_GESTIONE_LEAD con permessi differenziati per Admin e utenti.

## 🚀 Funzionalità

### Per Amministratori (Admin)
- **⬆️ Upload Multiplo**: Carica più file contemporaneamente (max 10)
- **🏷️ Categorizzazione**: Assegna categorie ai file (Documenti, Immagini, Video, etc.)
- **📝 Descrizioni**: Aggiungi note e descrizioni ai file
- **🗑️ Gestione File**: Elimina file esistenti
- **📊 Statistiche**: Visualizza metriche dettagliate sull'utilizzo
- **🔍 Monitoraggio**: Traccia download e utilizzo

### Per Tutti gli Utenti
- **👀 Visualizzazione**: Vedi tutti i file disponibili
- **⬇️ Download**: Scarica singoli file
- **🔍 Ricerca**: Cerca file per nome
- **🏷️ Filtri**: Filtra per categoria
- **📅 Ordinamento**: File ordinati per data di caricamento

## 🏗️ Architettura

### Database
- **`storage_files`**: Tabella principale per i metadati dei file
- **`storage_downloads`**: Tracciamento dei download
- **RLS**: Row Level Security per controlli di accesso

### File System
```
storage/
├── uploads/          # File caricati
└── temp/            # File temporanei
```

### Componenti
```
components/storage/
├── __init__.py
├── storage_manager.py    # Logica business
└── storage_ui.py         # Interfaccia utente
```

## 📋 Categorie Supportate

| Categoria | Estensioni Supportate |
|-----------|----------------------|
| 📄 Documenti | pdf, doc, docx, txt, rtf, odt |
| 🖼️ Immagini | jpg, jpeg, png, gif, bmp, svg, webp |
| 🎥 Video | mp4, avi, mov, wmv, flv, webm |
| 🎵 Audio | mp3, wav, flac, aac, ogg |
| 📦 Archivi | zip, rar, 7z, tar, gz |
| 📊 Fogli di Calcolo | xls, xlsx, csv, ods |
| 📽️ Presentazioni | ppt, pptx, odp |
| ❓ Altro | Tutti gli altri formati |

## 🔧 Installazione

### 1. Esegui lo Script di Setup
```bash
cd DASH_GESTIONE_LEAD
python create_storage_tables.py
```

### 2. Verifica le Tabelle
Lo script creerà automaticamente:
- Tabella `storage_files`
- Tabella `storage_downloads`
- Indici per ottimizzazione
- Policy RLS per sicurezza

### 3. Avvia l'Applicazione
```bash
streamlit run app.py
```

## 🎯 Utilizzo

### Per Admin

#### Caricare File
1. Vai alla sezione **📁 Storage**
2. Clicca sul tab **⬆️ Carica File**
3. Seleziona uno o più file
4. Scegli la categoria appropriata
5. Aggiungi una descrizione (opzionale)
6. Clicca **🚀 Carica File**

#### Gestire File Esistenti
1. Nel tab **📋 Lista File**
2. Usa i filtri per trovare i file
3. Clicca **🗑️** per eliminare un file
4. Conferma l'eliminazione

#### Visualizzare Statistiche
1. Vai al tab **📊 Statistiche**
2. Visualizza metriche dettagliate
3. Analizza l'utilizzo per categoria

### Per Utenti

#### Scaricare File
1. Vai alla sezione **📁 Storage**
2. Usa i filtri per trovare i file
3. Clicca **⬇️** per scaricare
4. Il file verrà scaricato automaticamente

#### Cercare File
1. Usa la barra di ricerca per nome file
2. Filtra per categoria
3. I risultati si aggiornano in tempo reale

## 🔒 Sicurezza

### Controlli di Accesso
- **RLS**: Row Level Security su tutte le tabelle
- **Permessi**: Solo Admin può caricare/eliminare
- **Validazione**: Controlli sui tipi di file
- **Hash**: Verifica integrità dei file

### Policy Database
- **SELECT**: Tutti possono vedere file attivi
- **INSERT**: Solo Admin può caricare
- **UPDATE**: Solo Admin può modificare
- **DELETE**: Solo Admin può eliminare

## 📊 Monitoraggio

### Metriche Disponibili
- **File Totali**: Numero di file caricati
- **Spazio Utilizzato**: Dimensione totale in bytes
- **Download Count**: Numero di download per file
- **Categorie**: Distribuzione per tipo
- **Utenti**: Chi ha caricato/scaricato cosa

### Log Attività
- **Upload**: Chi, quando, cosa
- **Download**: Chi, quando, da dove
- **Eliminazioni**: Chi, quando, cosa

## 🛠️ Manutenzione

### Pulizia File
- I file eliminati vengono marcati come `is_active = false`
- I file fisici vengono rimossi dal filesystem
- I record di download vengono mantenuti per statistiche

### Backup
- I file sono salvati in `storage/uploads/`
- I metadati sono nel database Supabase
- Considera backup regolari della directory storage

### Monitoraggio Spazio
- Controlla regolarmente le statistiche
- Monitora la crescita dello storage
- Pianifica pulizie periodiche se necessario

## 🐛 Troubleshooting

### Problemi Comuni

#### File Non Caricati
- Verifica i permessi di scrittura su `storage/uploads/`
- Controlla la connessione al database
- Verifica che l'utente sia Admin

#### Download Non Funzionanti
- Verifica che il file esista nel filesystem
- Controlla i permessi di lettura
- Verifica la connessione al database

#### Errori Database
- Esegui `create_storage_tables.py` per ricreare le tabelle
- Verifica le policy RLS
- Controlla i log di Supabase

### Log e Debug
- I log sono visibili nella console Streamlit
- Controlla i log di Supabase per errori database
- Usa `test_storage_functionality()` per test

## 🔄 Aggiornamenti Futuri

### Funzionalità Pianificate
- **Versioning**: Gestione versioni dei file
- **Condivisione**: Link di condivisione temporanei
- **Anteprime**: Anteprima file direttamente nell'UI
- **Notifiche**: Notifiche per nuovi file
- **API**: Endpoint REST per integrazioni

### Miglioramenti
- **Compressione**: Compressione automatica dei file
- **CDN**: Integrazione con CDN per performance
- **Sincronizzazione**: Sync con servizi cloud
- **Backup**: Backup automatico dei file

## 📞 Supporto

Per problemi o domande:
1. Controlla questo README
2. Verifica i log dell'applicazione
3. Controlla la documentazione Supabase
4. Contatta l'amministratore del sistema

---

**Creato da Ezio Camporeale**  
**Versione**: 1.0  
**Data**: $(date +%Y-%m-%d)

