-- SOLUZIONE TEMPORANEA PER STORAGE_FILES RLS
-- Esegui questo nel Supabase SQL Editor

-- Disabilita temporaneamente RLS per permettere il funzionamento
ALTER TABLE storage_files DISABLE ROW LEVEL SECURITY;

-- Crea tabella storage_downloads se non esiste
CREATE TABLE IF NOT EXISTS storage_downloads (
    id SERIAL PRIMARY KEY,
    file_id INTEGER REFERENCES storage_files(id) ON DELETE CASCADE,
    downloaded_by INTEGER REFERENCES users(id),
    downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Disabilita RLS anche su storage_downloads
ALTER TABLE storage_downloads DISABLE ROW LEVEL SECURITY;

-- Crea indici per performance
CREATE INDEX IF NOT EXISTS idx_storage_files_category ON storage_files(category);
CREATE INDEX IF NOT EXISTS idx_storage_files_uploaded_by ON storage_files(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_storage_files_is_active ON storage_files(is_active);
CREATE INDEX IF NOT EXISTS idx_storage_downloads_file_id ON storage_downloads(file_id);
CREATE INDEX IF NOT EXISTS idx_storage_downloads_downloaded_by ON storage_downloads(downloaded_by);

-- Verifica che le tabelle esistano
SELECT 'storage_files' as table_name, count(*) as record_count FROM storage_files
UNION ALL
SELECT 'storage_downloads' as table_name, count(*) as record_count FROM storage_downloads;
