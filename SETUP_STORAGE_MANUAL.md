# 📁 Setup Manuale Storage - DASH_GESTIONE_LEAD

## 🚨 IMPORTANTE: Setup Manuale Richiesto

A causa delle limitazioni dell'API Supabase, le tabelle per lo storage devono essere create manualmente nel dashboard.

## 📋 Istruzioni Passo-Passo

### 1. Accedi al Dashboard Supabase
- Vai su: https://supabase.com/dashboard
- Fai login con le tue credenziali
- Seleziona il progetto DASH_GESTIONE_LEAD

### 2. Apri SQL Editor
- Nella sidebar sinistra, clicca sull'icona `</>` (SQL Editor)
- Clicca su "New Query"

### 3. Copia e Incolla il Codice SQL
Copia tutto il contenuto del file `database/create_storage_simple.sql` e incollalo nell'editor SQL.

### 4. Esegui le Query
- Clicca sul pulsante "Run" (o premi Ctrl+Enter)
- Attendi che tutte le query vengano eseguite con successo

### 5. Verifica le Tabelle Create
Dovresti vedere queste tabelle nella sezione "Table Editor":
- ✅ `storage_files`
- ✅ `storage_downloads`

## 🔧 Codice SQL da Eseguire

```sql
-- Tabella semplificata per la gestione dei file storage
-- Versione semplificata per Supabase
-- Creato da Ezio Camporeale per DASH_GESTIONE_LEAD

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

-- RLS (Row Level Security) per controllare l'accesso ai file
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
            AND u.role_name = 'Admin'
        )
    );

-- Policy: solo admin può aggiornare i file
CREATE POLICY "storage_files_update_policy" ON storage_files
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = uploaded_by 
            AND u.role_name = 'Admin'
        )
    );

-- Policy: solo admin può eliminare i file (soft delete)
CREATE POLICY "storage_files_delete_policy" ON storage_files
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = uploaded_by 
            AND u.role_name = 'Admin'
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
            AND u.role_name = 'Admin'
        )
    );

-- Policy: utenti possono vedere solo i propri download
CREATE POLICY "storage_downloads_select_user_policy" ON storage_downloads
    FOR SELECT USING (downloaded_by = auth.uid());
```

## ✅ Verifica Setup

Dopo aver eseguito le query, verifica che tutto sia corretto:

### 1. Controlla le Tabelle
- Vai a "Table Editor" nel dashboard Supabase
- Dovresti vedere `storage_files` e `storage_downloads`

### 2. Testa l'Applicazione
```bash
cd DASH_GESTIONE_LEAD
streamlit run app.py
```

### 3. Verifica la Sezione Storage
- Fai login come Admin
- Vai alla sezione "📁 Storage"
- Dovresti vedere l'interfaccia senza errori

## 🐛 Risoluzione Problemi

### Errore: "relation does not exist"
- Le tabelle non sono state create correttamente
- Riprova a eseguire le query SQL

### Errore: "permission denied"
- Verifica che l'utente abbia i permessi per creare tabelle
- Controlla che il progetto Supabase sia attivo

### Errore: "duplicate key value"
- Le tabelle potrebbero essere già esistenti
- Usa `DROP TABLE IF EXISTS` prima di creare

## 🚀 Dopo il Setup

Una volta create le tabelle:

1. **Testa l'Upload**: Carica un file di test come Admin
2. **Testa il Download**: Scarica il file come utente normale
3. **Verifica i Permessi**: Assicurati che solo gli Admin possano caricare
4. **Controlla le Statistiche**: Verifica che i contatori funzionino

## 📞 Supporto

Se hai problemi:
1. Controlla i log di Supabase nel dashboard
2. Verifica che tutte le query siano state eseguite
3. Controlla che le policy RLS siano attive
4. Testa con un file piccolo prima

---

**Creato da Ezio Camporeale**  
**Data**: $(date +%Y-%m-%d)
