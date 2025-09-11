# 🎯 Istruzioni Finali per Storage - DASH_GESTIONE_LEAD

## ⚠️ PROBLEMI RISOLTI:
1. ✅ `column u.role_name does not exist` → Usa `u.is_admin = true`
2. ✅ `operator does not exist: integer = uuid` → Usa `auth.uid()::integer`

## 🚀 Setup Finale (5 minuti)

### 1. Pulisci e Ricrea le Tabelle
1. Vai su: https://supabase.com/dashboard
2. Seleziona il tuo progetto DASH_GESTIONE_LEAD
3. Clicca su "SQL Editor" (icona `</>`)
4. Clicca "New Query"
5. **Copia e incolla tutto il codice qui sotto:**
6. Clicca "Run"

### 2. Codice SQL Finale (Pulizia Completa)
```sql
-- 1. Rimuovi le policy esistenti
DROP POLICY IF EXISTS "storage_files_select_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_insert_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_update_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_downloads_insert_policy" ON storage_downloads;
DROP POLICY IF EXISTS "storage_downloads_select_admin_policy" ON storage_downloads;
DROP POLICY IF EXISTS "storage_downloads_select_user_policy" ON storage_downloads;

-- 2. Disabilita RLS
ALTER TABLE IF EXISTS storage_files DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS storage_downloads DISABLE ROW LEVEL SECURITY;

-- 3. Elimina le tabelle esistenti (se esistono)
DROP TABLE IF EXISTS storage_downloads CASCADE;
DROP TABLE IF EXISTS storage_files CASCADE;

-- 4. Ricrea le tabelle
CREATE TABLE storage_files (
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

CREATE TABLE storage_downloads (
    id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL REFERENCES storage_files(id) ON DELETE CASCADE,
    downloaded_by INTEGER NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- 5. Crea gli indici
CREATE INDEX idx_storage_files_category ON storage_files(category);
CREATE INDEX idx_storage_files_uploaded_by ON storage_files(uploaded_by);
CREATE INDEX idx_storage_files_uploaded_at ON storage_files(uploaded_at);
CREATE INDEX idx_storage_files_is_active ON storage_files(is_active);
CREATE INDEX idx_storage_downloads_file_id ON storage_downloads(file_id);
CREATE INDEX idx_storage_downloads_downloaded_by ON storage_downloads(downloaded_by);
CREATE INDEX idx_storage_downloads_downloaded_at ON storage_downloads(downloaded_at);

-- 6. Abilita RLS
ALTER TABLE storage_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE storage_downloads ENABLE ROW LEVEL SECURITY;

-- 7. Crea le policy corrette
CREATE POLICY "storage_files_select_policy" ON storage_files
    FOR SELECT USING (is_active = true);

CREATE POLICY "storage_files_insert_policy" ON storage_files
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = uploaded_by 
            AND u.is_admin = true
        )
    );

CREATE POLICY "storage_files_update_policy" ON storage_files
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = uploaded_by 
            AND u.is_admin = true
        )
    );

CREATE POLICY "storage_files_delete_policy" ON storage_files
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = uploaded_by 
            AND u.is_admin = true
        )
    );

CREATE POLICY "storage_downloads_insert_policy" ON storage_downloads
    FOR INSERT WITH CHECK (downloaded_by = auth.uid()::integer);

CREATE POLICY "storage_downloads_select_admin_policy" ON storage_downloads
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = downloaded_by 
            AND u.is_admin = true
        )
    );

CREATE POLICY "storage_downloads_select_user_policy" ON storage_downloads
    FOR SELECT USING (downloaded_by = auth.uid()::integer);
```

### 3. Verifica il Setup
```bash
python3 test_storage_setup.py
```

### 4. Avvia l'App
```bash
streamlit run app.py
```

### 5. Testa la Funzionalità
1. Fai login come **Admin** (is_admin = true)
2. Vai alla sezione **📁 Storage**
3. Carica un file di test
4. Fai logout e login come utente normale
5. Verifica che puoi scaricare il file

## ✅ Cosa è stato corretto

1. **Errore `role_name`**: Cambiato da `u.role_name = 'Admin'` a `u.is_admin = true`
2. **Errore UUID/INTEGER**: Cambiato da `auth.uid()` a `auth.uid()::integer`
3. **Pulizia completa**: Script che elimina e ricrea tutto da zero

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
- ✅ **RISOLTO**: Usa `u.is_admin = true`

### "operator does not exist: integer = uuid"
- ✅ **RISOLTO**: Usa `auth.uid()::integer`

### "Tabelle non trovate"
- Esegui il codice SQL di pulizia completa sopra

### "Permission denied"
- Assicurati di essere loggato come Admin (is_admin = true)
- Verifica che le policy RLS siano state create correttamente

## 📞 Supporto
Se hai ancora problemi:
1. Controlla i log di Supabase nel dashboard
2. Verifica che l'utente abbia `is_admin = true` nella tabella users
3. Esegui il test: `python3 test_storage_setup.py`
4. Controlla che le tabelle siano state create correttamente

---

**🎉 Ora la sezione Storage dovrebbe funzionare perfettamente senza errori!**
