-- Fix per policy RLS di eliminazione storage_files
-- Il problema è che la policy attuale controlla se l'uploader è admin,
-- ma dovrebbe controllare se l'utente corrente è admin

-- 1. Rimuovi la policy esistente
DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;

-- 2. Crea una policy semplificata per DELETE
-- Per ora permettiamo a tutti gli admin di eliminare qualsiasi file
CREATE POLICY "storage_files_delete_policy" ON storage_files
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = (SELECT auth.uid()::integer)
            AND u.is_admin = true
        )
    );

-- 3. Se la conversione UUID->INTEGER non funziona, usa questa versione alternativa:
-- DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;
-- CREATE POLICY "storage_files_delete_policy" ON storage_files
--     FOR DELETE USING (true);  -- Temporaneamente permette a tutti di eliminare

-- 4. Verifica che RLS sia abilitato
ALTER TABLE storage_files ENABLE ROW LEVEL SECURITY;
