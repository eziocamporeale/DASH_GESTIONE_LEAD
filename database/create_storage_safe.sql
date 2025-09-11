-- Script SICURO per creare le tabelle storage
-- Funziona anche se le tabelle non esistono ancora
-- Creato da Ezio Camporeale per DASH_GESTIONE_LEAD

-- 1. Crea le tabelle (se non esistono)
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

CREATE TABLE IF NOT EXISTS storage_downloads (
    id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL REFERENCES storage_files(id) ON DELETE CASCADE,
    downloaded_by INTEGER NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- 2. Crea gli indici (se non esistono)
CREATE INDEX IF NOT EXISTS idx_storage_files_category ON storage_files(category);
CREATE INDEX IF NOT EXISTS idx_storage_files_uploaded_by ON storage_files(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_storage_files_uploaded_at ON storage_files(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_storage_files_is_active ON storage_files(is_active);
CREATE INDEX IF NOT EXISTS idx_storage_downloads_file_id ON storage_downloads(file_id);
CREATE INDEX IF NOT EXISTS idx_storage_downloads_downloaded_by ON storage_downloads(downloaded_by);
CREATE INDEX IF NOT EXISTS idx_storage_downloads_downloaded_at ON storage_downloads(downloaded_at);

-- 3. Abilita RLS
ALTER TABLE storage_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE storage_downloads ENABLE ROW LEVEL SECURITY;

-- 4. Rimuovi le policy esistenti (se esistono) - SICURO
DO $$ 
BEGIN
    -- Rimuovi policy storage_files
    IF EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'storage_files' AND policyname = 'storage_files_select_policy') THEN
        DROP POLICY "storage_files_select_policy" ON storage_files;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'storage_files' AND policyname = 'storage_files_insert_policy') THEN
        DROP POLICY "storage_files_insert_policy" ON storage_files;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'storage_files' AND policyname = 'storage_files_update_policy') THEN
        DROP POLICY "storage_files_update_policy" ON storage_files;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'storage_files' AND policyname = 'storage_files_delete_policy') THEN
        DROP POLICY "storage_files_delete_policy" ON storage_files;
    END IF;
    
    -- Rimuovi policy storage_downloads
    IF EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'storage_downloads' AND policyname = 'storage_downloads_insert_policy') THEN
        DROP POLICY "storage_downloads_insert_policy" ON storage_downloads;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'storage_downloads' AND policyname = 'storage_downloads_select_admin_policy') THEN
        DROP POLICY "storage_downloads_select_admin_policy" ON storage_downloads;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'storage_downloads' AND policyname = 'storage_downloads_select_user_policy') THEN
        DROP POLICY "storage_downloads_select_user_policy" ON storage_downloads;
    END IF;
END $$;

-- 5. Crea le policy corrette
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
