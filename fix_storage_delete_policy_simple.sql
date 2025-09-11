-- Fix per policy RLS di eliminazione storage_files - VERSIONE SEMPLICE
-- Risolve errore: cannot cast type uuid to integer

-- 1. Rimuovi la policy esistente
DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;

-- 2. Policy temporanea - tutti possono eliminare (SOLO PER TEST)
-- ATTENZIONE: Questa policy permette a TUTTI di eliminare file
-- Usa solo per test, poi implementa una policy più sicura
CREATE POLICY "storage_files_delete_policy" ON storage_files
    FOR DELETE USING (true);

-- 3. Verifica che RLS sia abilitato
ALTER TABLE storage_files ENABLE ROW LEVEL SECURITY;

-- 4. DOPO IL TEST, implementa questa policy più sicura:
-- DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;
-- CREATE POLICY "storage_files_delete_policy" ON storage_files
--     FOR DELETE USING (
--         EXISTS (
--             SELECT 1 FROM users u 
--             WHERE u.id = uploaded_by  -- Controlla se l'uploader è admin
--             AND u.is_admin = true
--         )
--     );
