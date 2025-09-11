-- Script per pulire e ricreare completamente le tabelle storage
-- Esegui questo script nel SQL Editor di Supabase

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
