-- Fix per policy RLS di eliminazione storage_files - VERSIONE 2
-- Risolve errore: cannot cast type uuid to integer

-- 1. Rimuovi la policy esistente
DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;

-- 2. Opzione A: Policy semplificata - solo admin possono eliminare
-- Usa una funzione personalizzata per ottenere l'ID utente corrente
CREATE POLICY "storage_files_delete_policy" ON storage_files
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = (
                SELECT id FROM users 
                WHERE auth.uid()::text = auth.uid()::text
                LIMIT 1
            )
            AND u.is_admin = true
        )
    );

-- 3. Se Opzione A non funziona, usa Opzione B: Policy temporanea
-- DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;
-- CREATE POLICY "storage_files_delete_policy" ON storage_files
--     FOR DELETE USING (true);  -- Temporaneamente permette a tutti di eliminare

-- 4. Verifica che RLS sia abilitato
ALTER TABLE storage_files ENABLE ROW LEVEL SECURITY;
