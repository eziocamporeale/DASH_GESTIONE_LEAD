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

-- Commenti per documentazione
COMMENT ON TABLE storage_files IS 'Tabella per gestire i file caricati nel sistema storage';
COMMENT ON COLUMN storage_files.filename IS 'Nome del file nel filesystem';
COMMENT ON COLUMN storage_files.original_filename IS 'Nome originale del file caricato';
COMMENT ON COLUMN storage_files.file_path IS 'Percorso completo del file nel filesystem';
COMMENT ON COLUMN storage_files.file_size IS 'Dimensione del file in bytes';
COMMENT ON COLUMN storage_files.file_type IS 'Tipo MIME del file';
COMMENT ON COLUMN storage_files.category IS 'Categoria del file (Documenti, Immagini, Video, etc.)';
COMMENT ON COLUMN storage_files.description IS 'Descrizione opzionale del file';
COMMENT ON COLUMN storage_files.uploaded_by IS 'ID dell''utente che ha caricato il file';
COMMENT ON COLUMN storage_files.download_count IS 'Numero di volte che il file è stato scaricato';
COMMENT ON COLUMN storage_files.is_active IS 'Flag per soft delete del file';

COMMENT ON TABLE storage_downloads IS 'Tabella per tracciare i download dei file';
COMMENT ON COLUMN storage_downloads.file_id IS 'ID del file scaricato';
COMMENT ON COLUMN storage_downloads.downloaded_by IS 'ID dell''utente che ha scaricato il file';
COMMENT ON COLUMN storage_downloads.ip_address IS 'Indirizzo IP del download';
COMMENT ON COLUMN storage_downloads.user_agent IS 'User agent del browser';
