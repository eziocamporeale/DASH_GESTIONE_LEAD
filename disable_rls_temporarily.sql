-- DISABILITA RLS TEMPORANEAMENTE PER TEST
-- ATTENZIONE: Questo rimuove TUTTE le protezioni RLS

-- 1. Disabilita RLS per storage_files
ALTER TABLE storage_files DISABLE ROW LEVEL SECURITY;

-- 2. Disabilita RLS per storage_downloads
ALTER TABLE storage_downloads DISABLE ROW LEVEL SECURITY;

-- 3. Verifica stato
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename IN ('storage_files', 'storage_downloads');

-- 4. PER RIABILITARE RLS DOPO IL TEST:
-- ALTER TABLE storage_files ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE storage_downloads ENABLE ROW LEVEL SECURITY;
