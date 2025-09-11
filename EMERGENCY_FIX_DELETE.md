# 🚨 FIX EMERGENZA: Eliminazione file Storage

## 🐛 Problema Critico
Tutte le operazioni di eliminazione sono bloccate da RLS:
- DELETE fisico: ❌ Bloccato
- UPDATE (soft delete): ❌ Bloccato
- Errore: `new row violates row-level security policy`

## 🔧 Soluzione Immediata

### Opzione A: Disabilita temporaneamente RLS (RAPIDO)
```sql
-- 1. Disabilita RLS temporaneamente
ALTER TABLE storage_files DISABLE ROW LEVEL SECURITY;

-- 2. Ora puoi eliminare i file normalmente
-- 3. Dopo aver testato, riabilita RLS:
-- ALTER TABLE storage_files ENABLE ROW LEVEL SECURITY;
```

### Opzione B: Policy temporanea per tutti (SICURO)
```sql
-- 1. Rimuovi policy esistenti
DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_update_policy" ON storage_files;

-- 2. Policy temporanea - solo admin possono modificare
CREATE POLICY "storage_files_admin_all_policy" ON storage_files
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = (SELECT auth.uid()::integer)
            AND u.is_admin = true
        )
    );
```

### Opzione C: Policy completamente aperta (SOLO PER TEST)
```sql
-- ATTENZIONE: Solo per test, non per produzione!
DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_update_policy" ON storage_files;

CREATE POLICY "storage_files_open_policy" ON storage_files
    FOR ALL USING (true);
```

## 🎯 Raccomandazione
**Usa Opzione A** per test rapidi, poi implementa Opzione B per produzione.

## 📝 Come eseguire
1. Vai su [Supabase Dashboard](https://supabase.com/dashboard)
2. SQL Editor
3. Esegui l'Opzione A
4. Testa l'eliminazione
5. Riabilita RLS quando finito

## ⚠️ Attenzione
- Opzione A: Nessuna protezione RLS
- Opzione B: Solo admin possono modificare (SICURO)
- Opzione C: Tutti possono modificare (NON SICURO)
