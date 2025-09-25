# 🇪🇸 Importazione Lead Spagnoli

Script per importare lead spagnoli dal file `Spain-1.xlsx` nella dashboard DASH_GESTIONE_LEAD.

## 📁 File Disponibili

### 1. `import_spain_leads.py` - Importazione Completa
- **Scopo**: Importa tutti i 8,703 lead dal file Excel
- **Modalità**: 
  - `--test`: Analizza il file senza importare
  - Senza parametri: Importa tutti i lead (richiede conferma)

### 2. `import_spain_leads_small.py` - Importazione Test
- **Scopo**: Importa solo 10 lead per test
- **Uso**: Per verificare che tutto funzioni prima dell'importazione completa

## 🚀 Come Usare

### Test dell'Analisi (Senza Importazione)
```bash
cd DASH_GESTIONE_LEAD
python3 scripts/import_spain_leads.py --test
```

### Importazione Test (10 Lead)
```bash
cd DASH_GESTIONE_LEAD
python3 scripts/import_spain_leads_small.py
```

### Importazione Completa (8,703 Lead)
```bash
cd DASH_GESTIONE_LEAD
python3 scripts/import_spain_leads.py
```

## 📊 Struttura File Excel

Il file `Spain-1.xlsx` contiene:
- **Colonna 0**: Email
- **Colonna 1**: Email (duplicata)
- **Colonna 2**: Nome
- **Colonna 3**: Cognome
- **Colonna 4**: Paese (SPAIN)
- **Colonna 5**: Telefono
- **Colonne 6-9**: Vuote o con pochi dati

## 🔄 Conversione Dati

Gli script convertono automaticamente:

### Email
- Pulizia e validazione formato
- Conversione in lowercase

### Telefoni
- Formato automatico: `+34XXXXXXXXX`
- Rimozione caratteri speciali
- Aggiunta prefisso spagnolo se mancante

### Dati Dashboard
- **Categoria**: Default (ID: 1)
- **Stato**: Nuovo (ID: 1)
- **Priorità**: Media (ID: 2)
- **Fonte**: Default (ID: 1)
- **Gruppo**: Non assegnato
- **Note**: "Importato da Spain-1.xlsx - Paese: SPAIN"

## ✅ Test Completati

- ✅ Analisi file: 8,703 lead identificati
- ✅ Importazione test: 10/10 lead importati con successo
- ✅ Verifica database: Lead visibili nella dashboard
- ✅ Formato telefoni: Corretto (+34XXXXXXXXX)
- ✅ Formato email: Validato e pulito

## 📋 Esempi Lead Importati

1. **Jenny Chiang** - jennychiang0909@gmail.com - +341123378978
2. **Maria Teresa Alonso Ferrer** - 000francis@gmail.com - +34601123469
3. **Arturo Cabezudo Valbuena** - 0535ar@gmail.com - +34639144727
4. **Semy Atba** - 12021js@gmail.com - +34628280748
5. **Javier Ortega** - 12514policialocal@pajara.es - +34622242070

## ⚠️ Note Importanti

- **Backup**: Assicurati di avere un backup del database prima dell'importazione completa
- **Performance**: L'importazione di 8,703 lead può richiedere alcuni minuti
- **Duplicati**: Gli script non controllano duplicati esistenti
- **Gruppi**: I lead vengono importati senza assegnazione a gruppi

## 🎯 Prossimi Passi

Dopo l'importazione:
1. Assegna i lead ai gruppi appropriati
2. Verifica la qualità dei dati
3. Assegna i lead agli utenti
4. Configura stati e priorità se necessario

