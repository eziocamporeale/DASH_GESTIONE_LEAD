# 🔧 FIX: Policy RLS per eliminazione file Storage

## 🐛 Problema
Errore RLS quando si prova a eliminare un file:
```
{'message': 'new row violates row-level security policy for table "storage_files"', 'code': '42501'}
```

## 🔍 Causa
La policy RLS per DELETE controlla se l'utente che ha caricato il file è admin, ma non controlla se l'utente corrente è admin.

## ✅ Soluzione

### Opzione 1: Policy semplificata (RACCOMANDATO)
Esegui questo SQL nel dashboard Supabase:

```sql
-- 1. Rimuovi la policy esistente
DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;

-- 2. Crea policy semplificata - solo admin possono eliminare
CREATE POLICY "storage_files_delete_policy" ON storage_files
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = (SELECT auth.uid()::integer)
            AND u.is_admin = true
        )
    );
```

### Opzione 2: Policy temporanea (se Opzione 1 non funziona)
Se la conversione UUID->INTEGER non funziona:

```sql
-- 1. Rimuovi la policy esistente
DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;

-- 2. Policy temporanea - tutti possono eliminare (ATTENZIONE: solo per test)
CREATE POLICY "storage_files_delete_policy" ON storage_files
    FOR DELETE USING (true);
```

## 🎯 Come eseguire

1. Vai su [Supabase Dashboard](https://supabase.com/dashboard)
2. Seleziona il tuo progetto
3. Vai su **SQL Editor**
4. Incolla il SQL dell'Opzione 1
5. Clicca **Run**

## ✅ Verifica
Dopo aver eseguito il SQL, prova a eliminare un file dall'interfaccia. Dovrebbe funzionare senza errori RLS.

## 🔒 Sicurezza
- **Opzione 1**: Solo admin possono eliminare (SICURO)
- **Opzione 2**: Tutti possono eliminare (SOLO PER TEST)

## 📝 Note
- La policy attuale controlla `uploaded_by` invece di `auth.uid()`
- Questo causa il problema perché non verifica l'utente corrente
- La nuova policy verifica correttamente l'utente loggato
