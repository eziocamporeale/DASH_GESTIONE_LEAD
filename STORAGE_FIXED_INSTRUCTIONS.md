# 🔧 Istruzioni Corrette per Storage - DASH_GESTIONE_LEAD

## ⚠️ PROBLEMA RISOLTO: `column u.role_name does not exist`

Il problema era che le policy RLS usavano `role_name` invece di `is_admin` che è il campo corretto nella tabella `users`.

## 🚀 Setup Corretto (5 minuti)

### 1. Crea le Tabelle nel Database
1. Vai su: https://supabase.com/dashboard
2. Seleziona il tuo progetto DASH_GESTIONE_LEAD
3. Clicca su "SQL Editor" (icona `</>`)
4. Clicca "New Query"
5. **Copia e incolla tutto il codice qui sotto:**
6. Clicca "Run"

### 2. Codice SQL Corretto
```sql
-- Tabella principale per i file
CREATE TABLE IF NOT EXISTS storage_files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    category VARCHAR(50) DEFAULT 'Documenti',
    description TEXT,
    uploaded_by INTEGER NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    download_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indici per ottimizzare le query
CREATE INDEX IF NOT EXISTS idx_storage_files_category ON storage_files(category);
CREATE INDEX IF NOT EXISTS idx_storage_files_uploaded_by ON storage_files(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_storage_files_uploaded_at ON storage_files(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_storage_files_is_active ON storage_files(is_active);

-- Tabella per tracciare i download
CREATE TABLE IF NOT EXISTS storage_downloads (
    id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL REFERENCES storage_files(id) ON DELETE CASCADE,
    downloaded_by INTEGER NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Indici per la tabella download
CREATE INDEX IF NOT EXISTS idx_storage_downloads_file_id ON storage_downloads(file_id);
CREATE INDEX IF NOT EXISTS idx_storage_downloads_downloaded_by ON storage_downloads(downloaded_by);
CREATE INDEX IF NOT EXISTS idx_storage_downloads_downloaded_at ON storage_downloads(downloaded_at);

-- RLS (Row Level Security)
ALTER TABLE storage_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE storage_downloads ENABLE ROW LEVEL SECURITY;

-- Policy: tutti possono vedere i file attivi
CREATE POLICY "storage_files_select_policy" ON storage_files
    FOR SELECT USING (is_active = true);

-- Policy: solo admin può inserire file (CORRETTO: usa is_admin)
CREATE POLICY "storage_files_insert_policy" ON storage_files
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = uploaded_by 
            AND u.is_admin = true
        )
    );

-- Policy: solo admin può aggiornare i file (CORRETTO: usa is_admin)
CREATE POLICY "storage_files_update_policy" ON storage_files
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = uploaded_by 
            AND u.is_admin = true
        )
    );

-- Policy: solo admin può eliminare i file (CORRETTO: usa is_admin)
CREATE POLICY "storage_files_delete_policy" ON storage_files
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = uploaded_by 
            AND u.is_admin = true
        )
    );

-- Policy: tutti possono inserire i propri download
CREATE POLICY "storage_downloads_insert_policy" ON storage_downloads
    FOR INSERT WITH CHECK (downloaded_by = auth.uid());

-- Policy: solo admin può vedere tutti i download (CORRETTO: usa is_admin)
CREATE POLICY "storage_downloads_select_admin_policy" ON storage_downloads
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = downloaded_by 
            AND u.is_admin = true
        )
    );

-- Policy: utenti possono vedere solo i propri download
CREATE POLICY "storage_downloads_select_user_policy" ON storage_downloads
    FOR SELECT USING (downloaded_by = auth.uid());
```

### 3. Se hai già creato le tabelle con errori
Se hai già eseguito il codice precedente e hai ricevuto errori, esegui prima questo script per pulire le policy:

```sql
-- Rimuovi le policy esistenti (se esistono)
DROP POLICY IF EXISTS "storage_files_select_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_insert_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_update_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_downloads_insert_policy" ON storage_downloads;
DROP POLICY IF EXISTS "storage_downloads_select_admin_policy" ON storage_downloads;
DROP POLICY IF EXISTS "storage_downloads_select_user_policy" ON storage_downloads;
```

Poi esegui il codice principale sopra.

### 4. Verifica il Setup
```bash
python3 test_storage_setup.py
```

### 5. Avvia l'App
```bash
streamlit run app.py
```

## ✅ Cosa è stato corretto

1. **Policy RLS**: Cambiato da `u.role_name = 'Admin'` a `u.is_admin = true`
2. **StorageManager**: Aggiornato per usare `is_admin` invece di `role_name`
3. **Storage UI**: Aggiornato per controllare `is_admin` invece di `role_name`

## 🎯 Funzionalità Disponibili

### Per Admin (is_admin = true):
- ⬆️ **Upload Multiplo**: Carica fino a 10 file contemporaneamente
- 🏷️ **Categorizzazione**: Assegna categorie automatiche
- 📝 **Descrizioni**: Aggiungi note ai file
- 🗑️ **Gestione**: Elimina file esistenti
- 📊 **Statistiche**: Visualizza metriche dettagliate

### Per Tutti:
- 👀 **Visualizzazione**: Vedi tutti i file disponibili
- ⬇️ **Download**: Scarica singoli file
- 🔍 **Ricerca**: Cerca per nome file
- 🏷️ **Filtri**: Filtra per categoria

## 🐛 Risoluzione Problemi

### "column u.role_name does not exist"
- ✅ **RISOLTO**: Usa il codice SQL corretto sopra

### "Tabelle non trovate"
- Esegui il codice SQL nel dashboard Supabase
- Verifica che tutte le query siano state eseguite senza errori

### "Permission denied"
- Assicurati di essere loggato come Admin (is_admin = true)
- Verifica che le policy RLS siano state create correttamente

## 📞 Supporto
Se hai ancora problemi:
1. Controlla i log di Supabase nel dashboard
2. Verifica che l'utente abbia `is_admin = true` nella tabella users
3. Esegui il test: `python3 test_storage_setup.py`

---

**🎉 Ora la sezione Storage dovrebbe funzionare perfettamente!**
