-- Script per correggere le policy RLS dello storage
-- Esegui questo script nel SQL Editor di Supabase

-- Rimuovi le policy esistenti (se esistono)
DROP POLICY IF EXISTS "storage_files_select_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_insert_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_update_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_downloads_insert_policy" ON storage_downloads;
DROP POLICY IF EXISTS "storage_downloads_select_admin_policy" ON storage_downloads;
DROP POLICY IF EXISTS "storage_downloads_select_user_policy" ON storage_downloads;

-- Ricrea le policy corrette usando is_admin invece di role_name

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

-- Policy: solo admin può eliminare i file (soft delete)
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
