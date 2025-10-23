# 🔧 TROUBLESHOOTING DEPLOY STREAMLIT CLOUD

**Data:** 14 Ottobre 2025  
**App:** Dashboard Gestione Lead  
**URL:** https://github.com/eziocamporeale/DASH_GESTIONE_LEAD

---

## ❌ ERRORE COMUNE: ImportError

### Sintomo
```
ImportError: This app has encountered an error.
File "/mount/src/dash_gestione_lead/app.py", line 21
from components.auth.auth_manager import auth_manager, require_auth, get_current_user
```

### Cause Possibili

#### 1. Cache Non Aggiornata
Streamlit Cloud usa una cache che potrebbe non riflettere i cambiamenti recenti.

**Soluzione:**
```bash
# Forza redeploy modificando requirements.txt
echo "# Updated: $(date)" >> requirements.txt
git add requirements.txt
git commit -m "Force redeploy"
git push origin main
```

#### 2. File Mancanti dopo Pulizia Sicurezza
Se hai eliminato file come `auth_manager_backup.py`, assicurati che i file principali esistano.

**Verifica:**
```bash
ls -la components/auth/
# Deve contenere:
# - auth_manager.py ✅
# - login_form.py ✅
# - __init__.py (opzionale)
```

#### 3. Dipendenze Mancanti
requirements.txt potrebbe non includere tutte le dipendenze.

**Verifica requirements.txt:**
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.15.0
bcrypt>=4.0.0
supabase>=2.3.0
python-dotenv>=1.0.0
openpyxl>=3.1.0
email-validator>=2.0.0
```

---

## ✅ CHECKLIST DEPLOY

### Pre-Deploy
- [ ] Tutti i file sono committati
- [ ] requirements.txt aggiornato
- [ ] Nessun import da file eliminati
- [ ] Test locale funziona: `streamlit run app.py`
- [ ] .gitignore non esclude file necessari

### Durante Deploy
- [ ] Push su GitHub completato
- [ ] Streamlit Cloud ha rilevato il push
- [ ] Build logs non mostrano errori
- [ ] App si riavvia correttamente

### Post-Deploy  
- [ ] Login funziona
- [ ] Database Supabase connesso
- [ ] Permessi utenti corretti
- [ ] Storage file accessibile

---

## 🔄 FORCE REDEPLOY

Se l'app non si aggiorna:

### Metodo 1: Timestamp Requirements
```bash
cd /Users/ezio/Ezio_Root/CREAZIONE\ PROGETTI\ EZIO/DASH_GESTIONE_LEAD
echo "# Force update: $(date)" >> requirements.txt
git add requirements.txt
git commit -m "Force redeploy: Update requirements"
git push origin main
```

### Metodo 2: Reboot da Dashboard
1. Vai su https://share.streamlit.io
2. Click su "Manage app" 
3. Click su "Reboot app"
4. Aspetta il riavvio (~30 secondi)

### Metodo 3: Clear Cache
1. Manage app → Settings
2. Clear cache
3. Reboot app

---

## 🐛 DEBUG REMOTO

### Visualizza Logs
```
1. Streamlit Cloud Dashboard
2. Click app → Manage app
3. Scroll su "Logs"
4. Cerca errori specifici
```

### Test Import Locale
```bash
# Testa gli import localmente
cd /Users/ezio/Ezio_Root/CREAZIONE\ PROGETTI\ EZIO/DASH_GESTIONE_LEAD
python3 -c "from components.auth.auth_manager import auth_manager; print('✅')"
```

### Verifica File Remoto
```bash
# Controlla cosa è su GitHub
git ls-files | grep auth_manager
# Output atteso:
# components/auth/auth_manager.py
```

---

## 🔐 PROBLEMI POST-SECURITY CLEANUP

### File Eliminati per Sicurezza
Questi file NON devono più esistere:
- ❌ change_admin_password.py
- ❌ test_all_logins.py
- ❌ reset_all_passwords.py  
- ❌ CREDENZIALI_RESET.txt
- ❌ auth_manager_backup.py

### File che DEVONO Esistere
Questi file sono necessari:
- ✅ components/auth/auth_manager.py
- ✅ components/auth/login_form.py
- ✅ database/database_manager.py
- ✅ config.py

---

## 🌐 SECRETS STREAMLIT CLOUD

### Configurazione Supabase
Nel dashboard Streamlit Cloud → Settings → Secrets:

```toml
[supabase]
url = "https://YOUR_PROJECT.supabase.co"
key = "YOUR_ANON_KEY"

[database]
type = "supabase"
```

### Verifica Secrets
```python
# In app.py, verifica che secrets esistano:
import streamlit as st

if "supabase" not in st.secrets:
    st.error("⚠️ Secrets Supabase non configurati!")
```

---

## 📊 STATO ATTUALE

### Ultimo Deploy
```
Commit: cd37f3c - Force redeploy: Update requirements timestamp
Branch: main
Status: ✅ Pushed su GitHub
```

### File Critici Presenti
```
✅ app.py
✅ components/auth/auth_manager.py
✅ components/auth/login_form.py  
✅ database/database_manager.py
✅ config.py
✅ requirements.txt
```

### Credenziali Attuali
```
Formato: username123
Admin: admin / admin123 (⚠️ CAMBIARE)
```

---

## 🆘 SUPPORTO

### Se l'errore persiste:

1. **Verifica Build Logs**
   - Streamlit Cloud → Manage app → Logs
   - Cerca traceback completo

2. **Test Locale**
   ```bash
   streamlit run app.py
   ```

3. **Rollback**
   ```bash
   git revert HEAD
   git push origin main
   ```

4. **Ricreare Auth Manager**
   Se necessario, ricrea da template base

---

## ✅ SOLUZIONE APPLICATA

### Azione Eseguita
```bash
# 1. Forzato redeploy con timestamp
echo "# Updated: Mon Oct 14 09:45:00 CEST 2025" >> requirements.txt

# 2. Commit e push
git add requirements.txt
git commit -m "Force redeploy: Update requirements timestamp"
git push origin main
```

### Risultato Atteso
- ⏳ Streamlit Cloud rileva il push
- ⏳ Avvia rebuild (1-2 minuti)
- ⏳ Redeploy app
- ✅ App funzionante con import corretti

---

## 📝 NOTE

- **Tempo deploy:** ~2-3 minuti
- **Cache lifetime:** Varia, può richiedere reboot
- **Logs retention:** 7 giorni su Streamlit Cloud

**Monitorare:** https://share.streamlit.io/dashboard

---

**Creato da:** Ezio Camporeale  
**Data:** 14 Ottobre 2025  
**Status:** ✅ Push completato, attendi redeploy


