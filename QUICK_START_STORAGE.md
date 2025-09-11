# 🚀 Quick Start - Sezione Storage

## ⚡ Setup Rapido (5 minuti)

### 1. Crea le Tabelle nel Database
1. Vai su: https://supabase.com/dashboard
2. Seleziona il tuo progetto DASH_GESTIONE_LEAD
3. Clicca su "SQL Editor" (icona `</>`)
4. Clicca "New Query"
5. **Copia e incolla tutto il codice qui sotto:**
6. Clicca "Run"

### 2. Codice SQL da Eseguire
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

-- Policy: solo admin può inserire file
CREATE POLICY "storage_files_insert_policy" ON storage_files
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = uploaded_by 
            AND u.is_admin = true
        )
    );

-- Policy: solo admin può aggiornare i file
CREATE POLICY "storage_files_update_policy" ON storage_files
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = uploaded_by 
            AND u.is_admin = true
        )
    );

-- Policy: solo admin può eliminare i file
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

-- Policy: solo admin può vedere tutti i download
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

### 3. Verifica il Setup
```bash
python3 test_storage_setup.py
```

### 4. Avvia l'App
```bash
streamlit run app.py
```

### 5. Testa la Funzionalità
1. Fai login come **Admin**
2. Vai alla sezione **📁 Storage**
3. Carica un file di test
4. Fai logout e login come utente normale
5. Verifica che puoi scaricare il file

## ✅ Funzionalità Disponibili

### Per Admin:
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

## 🎯 Categorie Supportate
- 📄 **Documenti**: PDF, DOC, TXT, etc.
- 🖼️ **Immagini**: JPG, PNG, GIF, etc.
- 🎥 **Video**: MP4, AVI, MOV, etc.
- 🎵 **Audio**: MP3, WAV, FLAC, etc.
- 📦 **Archivi**: ZIP, RAR, 7Z, etc.
- 📊 **Fogli**: XLS, XLSX, CSV, etc.
- 📽️ **Presentazioni**: PPT, PPTX, etc.

## 🐛 Risoluzione Problemi

### "Tabelle non trovate"
- Riprova a eseguire il codice SQL nel dashboard Supabase
- Verifica che tutte le query siano state eseguite senza errori

### "Permission denied"
- Assicurati di essere loggato come Admin per caricare file
- Verifica che le policy RLS siano state create correttamente

### "File non caricato"
- Controlla che la directory `storage/uploads/` esista
- Verifica i permessi di scrittura

## 📞 Supporto
Se hai problemi, controlla:
1. I log di Supabase nel dashboard
2. I log dell'applicazione Streamlit
3. Il file `SETUP_STORAGE_MANUAL.md` per istruzioni dettagliate

---

**🎉 Una volta completato il setup, la sezione Storage sarà completamente funzionale!**
