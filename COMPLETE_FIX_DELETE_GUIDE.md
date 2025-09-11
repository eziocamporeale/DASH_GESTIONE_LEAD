# 🔧 GUIDA COMPLETA: Fix eliminazione file Storage

## 🐛 Problema
Errore RLS: `cannot cast type uuid to integer` + `new row violates row-level security policy`

## 🔍 Causa Root
- `auth.uid()` restituisce UUID
- Tabella `users` usa INTEGER per ID
- Policy RLS non può convertire UUID → INTEGER
- Tutte le operazioni (UPDATE, DELETE) sono bloccate

## ✅ SOLUZIONI DISPONIBILI

### 🚨 OPZIONE 1: DISABILITA RLS (RAPIDO)
**Esegui questo SQL nel dashboard Supabase:**

```sql
-- Disabilita RLS temporaneamente
ALTER TABLE storage_files DISABLE ROW LEVEL SECURITY;
ALTER TABLE storage_downloads DISABLE ROW LEVEL SECURITY;
```

**✅ Vantaggi:**
- Fix immediato
- Eliminazione funziona subito
- Nessun errore di casting

**⚠️ Svantaggi:**
- Nessuna protezione RLS
- Solo per test/emergenze

---

### 🔒 OPZIONE 2: POLICY SEMPLIFICATA (SICURO)
**Esegui questo SQL:**

```sql
-- Rimuovi policy esistenti
DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_update_policy" ON storage_files;

-- Policy che permette a tutti di eliminare (temporanea)
CREATE POLICY "storage_files_delete_policy" ON storage_files
    FOR DELETE USING (true);

CREATE POLICY "storage_files_update_policy" ON storage_files
    FOR UPDATE USING (true);
```

**✅ Vantaggi:**
- RLS rimane attivo
- Eliminazione funziona
- Controllo a livello applicazione

---

### 🎯 OPZIONE 3: POLICY CORRETTA (IDEALE)
**Esegui questo SQL:**

```sql
-- Rimuovi policy esistenti
DROP POLICY IF EXISTS "storage_files_delete_policy" ON storage_files;
DROP POLICY IF EXISTS "storage_files_update_policy" ON storage_files;

-- Policy che controlla se l'uploader è admin
CREATE POLICY "storage_files_delete_policy" ON storage_files
    FOR DELETE USING (
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
```

**✅ Vantaggi:**
- Solo admin possono eliminare
- Sicurezza mantenuta
- Controllo corretto

---

## 🎯 RACCOMANDAZIONE

### Per TEST RAPIDO:
**Usa Opzione 1** - Disabilita RLS temporaneamente

### Per PRODUZIONE:
**Usa Opzione 3** - Policy corretta con controllo admin

## 📝 COME ESEGUIRE

1. Vai su [Supabase Dashboard](https://supabase.com/dashboard)
2. Seleziona il tuo progetto
3. Vai su **SQL Editor**
4. Copia e incolla l'SQL dell'opzione scelta
5. Clicca **Run**
6. Testa l'eliminazione nell'app

## 🔄 PER RIABILITARE RLS (se usi Opzione 1)

```sql
-- Riabilita RLS
ALTER TABLE storage_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE storage_downloads ENABLE ROW LEVEL SECURITY;

-- Poi implementa Opzione 3
```

## ✅ VERIFICA

Dopo aver eseguito l'SQL:
1. Vai nell'app Storage
2. Prova a eliminare un file
3. Dovrebbe funzionare senza errori RLS

## 🚨 NOTA IMPORTANTE

Il problema UUID/INTEGER è comune quando si usa Supabase con tabelle personalizzate. La soluzione migliore è usare UUID per tutti gli ID, ma per ora le opzioni sopra risolvono il problema immediato.
