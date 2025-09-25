-- Schema completo per storage_files
-- Esegui questo nel Supabase SQL Editor


    -- Schema completo per storage_files
    CREATE TABLE IF NOT EXISTS storage_files (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        original_filename VARCHAR(255) NOT NULL,
        file_path TEXT NOT NULL,
        file_size BIGINT NOT NULL DEFAULT 0,
        file_type VARCHAR(100),
        category VARCHAR(50),
        description TEXT,
        uploaded_by INTEGER REFERENCES users(id),
        uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        download_count INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Crea tabella storage_downloads
    CREATE TABLE IF NOT EXISTS storage_downloads (
        id SERIAL PRIMARY KEY,
        file_id INTEGER REFERENCES storage_files(id) ON DELETE CASCADE,
        downloaded_by INTEGER REFERENCES users(id),
        downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Crea indici per performance
    CREATE INDEX IF NOT EXISTS idx_storage_files_category ON storage_files(category);
    CREATE INDEX IF NOT EXISTS idx_storage_files_uploaded_by ON storage_files(uploaded_by);
    CREATE INDEX IF NOT EXISTS idx_storage_files_is_active ON storage_files(is_active);
    CREATE INDEX IF NOT EXISTS idx_storage_downloads_file_id ON storage_downloads(file_id);
    CREATE INDEX IF NOT EXISTS idx_storage_downloads_downloaded_by ON storage_downloads(downloaded_by);
    

-- RLS Policies per storage_files
-- Esegui questo dopo lo schema


    -- Abilita RLS sulla tabella storage_files
    ALTER TABLE storage_files ENABLE ROW LEVEL SECURITY;
    
    -- Policy per SELECT: tutti gli utenti autenticati possono leggere
    DROP POLICY IF EXISTS "storage_files_select_policy" ON storage_files;
    CREATE POLICY "storage_files_select_policy" ON storage_files
        FOR SELECT USING (true);
    
    -- Policy per INSERT: solo Admin possono inserire
    DROP POLICY IF EXISTS "storage_files_insert_policy" ON storage_files;
    CREATE POLICY "storage_files_insert_policy" ON storage_files
        FOR INSERT WITH CHECK (
            EXISTS (
                SELECT 1 FROM users 
                WHERE users.id = auth.uid() 
                AND (users.is_admin = true OR users.role_id = 1)
            )
        );
    
    -- Policy per UPDATE: solo Admin possono aggiornare
    DROP POLICY IF EXISTS "storage_files_update_policy" ON storage_files;
    CREATE POLICY "storage_files_update_policy" ON storage_files
        FOR UPDATE USING (
            EXISTS (
                SELECT 1 FROM users 
                WHERE users.id = auth.uid() 
                AND (users.is_admin = true OR users.role_id = 1)
            )
        );
    
    -- Policy per DELETE: solo Admin possono eliminare
    DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;
    CREATE POLICY "storage_files_delete_policy" ON storage_files
        FOR DELETE USING (
            EXISTS (
                SELECT 1 FROM users 
                WHERE users.id = auth.uid() 
                AND (users.is_admin = true OR users.role_id = 1)
            )
        );
    
    -- Crea tabella storage_downloads se non esiste
    CREATE TABLE IF NOT EXISTS storage_downloads (
        id SERIAL PRIMARY KEY,
        file_id INTEGER REFERENCES storage_files(id) ON DELETE CASCADE,
        downloaded_by INTEGER REFERENCES users(id),
        downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Abilita RLS su storage_downloads
    ALTER TABLE storage_downloads ENABLE ROW LEVEL SECURITY;
    
    -- Policy per storage_downloads: tutti possono inserire download
    DROP POLICY IF EXISTS "storage_downloads_insert_policy" ON storage_downloads;
    CREATE POLICY "storage_downloads_insert_policy" ON storage_downloads
        FOR INSERT WITH CHECK (true);
    
    -- Policy per storage_downloads: tutti possono leggere
    DROP POLICY IF EXISTS "storage_downloads_select_policy" ON storage_downloads;
    CREATE POLICY "storage_downloads_select_policy" ON storage_downloads
        FOR SELECT USING (true);
    