#!/usr/bin/env python3
"""
Script per importare e pulire i dati dal Google Sheet CRM Gemini Trading Limited
Creato da Ezio Camporeale
"""

import pandas as pd
import re
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def clean_phone_number(phone: str) -> str:
    """Pulisce e standardizza il numero di telefono"""
    if pd.isna(phone) or not phone:
        return ""
    
    # Rimuove prefissi come "p:" e spazi
    phone = str(phone).replace("p:", "").replace(" ", "").strip()
    
    # Se inizia con +39, mantieni così
    if phone.startswith("+39"):
        return phone
    
    # Se inizia con 39, aggiungi il +
    if phone.startswith("39"):
        return "+" + phone
    
    # Se inizia con 3, aggiungi +39
    if phone.startswith("3") and len(phone) >= 10:
        return "+39" + phone
    
    return phone

def clean_email(email: str) -> str:
    """Pulisce l'email rimuovendo caratteri extra"""
    if pd.isna(email) or not email:
        return ""
    
    email = str(email).strip()
    
    # Rimuove note aggiuntive dopo l'email
    if " non spunta" in email.lower():
        email = email.split(" non spunta")[0].strip()
    if " contattato" in email.lower():
        email = email.split(" contattato")[0].strip()
    
    return email

def extract_name_from_full_name(full_name: str) -> tuple:
    """Estrae nome e cognome dal nome completo"""
    if pd.isna(full_name) or not full_name:
        return "", ""
    
    full_name = str(full_name).strip()
    
    # Gestisce casi speciali come "G Fabio" -> "Fabio", ""
    if full_name.startswith("G "):
        full_name = full_name[2:].strip()
    
    parts = full_name.split()
    
    if len(parts) == 1:
        return parts[0], ""
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        # Se ci sono più di 2 parti, considera tutto tranne l'ultimo come nome
        return " ".join(parts[:-1]), parts[-1]

def categorize_lead_status(feedback: str) -> str:
    """Categorizza lo stato del lead basato sul feedback"""
    if pd.isna(feedback) or not feedback:
        return "Nuovo"
    
    feedback_lower = str(feedback).lower()
    
    if any(word in feedback_lower for word in ["chiuso", "acquistato", "bonifico", "compra"]):
        return "Chiuso"
    elif any(word in feedback_lower for word in ["meet", "zoom", "call", "fissata"]):
        return "In Contatto"
    elif any(word in feedback_lower for word in ["non risponde", "bloccato", "scomparso"]):
        return "Non Risponde"
    elif any(word in feedback_lower for word in ["perditempo", "senza budget", "coglione"]):
        return "Non Qualificato"
    elif any(word in feedback_lower for word in ["concorrenza", "competitor"]):
        return "Concorrenza"
    else:
        return "Contattato"

def categorize_lead_priority(feedback: str) -> str:
    """Determina la priorità del lead basata sul feedback"""
    if pd.isna(feedback) or not feedback:
        return "Media"
    
    feedback_lower = str(feedback).lower()
    
    if any(word in feedback_lower for word in ["super in target", "imprenditore", "capitale grossi", "3k", "1699"]):
        return "Alta"
    elif any(word in feedback_lower for word in ["chiuso", "acquistato", "bonifico", "800", "500", "1297"]):
        return "Alta"
    elif any(word in feedback_lower for word in ["perditempo", "senza budget", "non risponde", "bloccato"]):
        return "Bassa"
    else:
        return "Media"

def extract_budget_from_feedback(feedback: str) -> Optional[float]:
    """Estrae il budget dal feedback"""
    if pd.isna(feedback) or not feedback:
        return None
    
    feedback_str = str(feedback)
    
    # Cerca numeri seguiti da k (es. 3k = 3000)
    k_match = re.search(r'(\d+)k', feedback_str.lower())
    if k_match:
        return float(k_match.group(1)) * 1000
    
    # Cerca numeri diretti
    number_match = re.search(r'(\d{3,})', feedback_str)
    if number_match:
        return float(number_match.group(1))
    
    return None

def determine_lead_source() -> str:
    """Determina la fonte del lead (dal contesto sembra essere Facebook Ads)"""
    return "Facebook Ads"

def clean_feedback_text(feedback: str) -> str:
    """Pulisce il testo del feedback rimuovendo informazioni sensibili"""
    if pd.isna(feedback) or not feedback:
        return ""
    
    feedback = str(feedback)
    
    # Rimuove informazioni sensibili
    feedback = re.sub(r'\b\d{2,3}\s*anni?\b', '[età]', feedback, flags=re.IGNORECASE)
    feedback = re.sub(r'\b\d{1,2}/\d{1,2}\b', '[data]', feedback)
    feedback = re.sub(r'\b\d{1,2}\s*novembre\b', '[mese]', feedback, flags=re.IGNORECASE)
    feedback = re.sub(r'\b\d{1,2}\s*dicembre\b', '[mese]', feedback, flags=re.IGNORECASE)
    
    return feedback.strip()

def create_cleaned_dataset():
    """Crea il dataset pulito dai dati del Google Sheet"""
    
    # Dati estratti dal Google Sheet (solo i record validi)
    raw_data = [
        {"Nome Completo": "Roberto Loporcaro", "Telefono": "p:+393669754536", "Email": "loporcaroroberto@gmail.com", "Feedback": "chiuso con un servizio da 1297", "Ad Set": "CCC", "Stato": "Contattato", "Note": "fatta meet e chiuso"},
        {"Nome Completo": "Giuseppe Paglionico", "Telefono": "p:+393284149007", "Email": "giuse.pagli@live.it", "Feedback": "Non risponde", "Ad Set": "Contattato", "Stato": "Contattato", "Note": ""},
        {"Nome Completo": "Carlo commesso", "Telefono": "p:+393317146232", "Email": "carlocommesso@gmail.com", "Feedback": "Super in target fa consulenza ha già delle prop e vuole portare clienti target età:sulla 50 ina", "Ad Set": "Contattato", "Stato": "Contattato", "Note": "fatta meet e dobbiamo risentirci"},
        {"Nome Completo": "Massimo Bottaini", "Telefono": "p:+393396604939", "Email": "bottainimassimo@gmail.com", "Feedback": "Sempre in target ma lavoro statale non ha soldi,vuole partire con un nostro servizio il 13 dicembre perchè deve arrivargli la tredicesima", "Ad Set": "Contattato", "Stato": "Contattato", "Note": "fatta meet e dobbiamo risentirci le deve arrivare lo stiipendio"},
        {"Nome Completo": "Ivan Alessandrini", "Telefono": "p:+393289850623", "Email": "ivanooalessandrini@gmail.com", "Feedback": "Da fissare zoom", "Ad Set": "In target nostra concorrenza ha una community", "Stato": "Contattato", "Note": "concorenza non abbiamo fatto meet"},
        {"Nome Completo": "Massimo Marzioni", "Telefono": "p:+393358772660", "Email": "massimomarzioni18@gmail.com", "Feedback": "Super in target,imprenditore àche vuole investire in borsa con capitale molto grossi e vuole mettere in gioco suo figlio per far si che guadagna passivamente con il trading,abbiamo la zoom con il figlio lunedi se facciamo simpatia al figlio compra 2 servizi da 3k nostri ed sempre disposto a reinvestire per qualunque novità proponiamo Target età:58 anni", "Ad Set": "Contattato", "Stato": "Contattato", "Note": "fatta meet e dobbiamo risentirci"},
        {"Nome Completo": "Andreas De Marco", "Telefono": "p:+393201794000", "Email": "andreasdemarco84@gmail.com", "Feedback": "Super in Target lavoro statale classico,ha già 2 prop acquistate con altre aziende domani 15/11 ho la call per quanto mi da risposta,non so quale sia la sua età avrà un 30 anni. chiuso con un prodotto da 500 dopo vari tentativi", "Ad Set": "Contattato", "Stato": "Contattato", "Note": "fatta meet e chiuso"},
        {"Nome Completo": "Antonio Magro", "Telefono": "p:+393495797756", "Email": "amagro74@gmail.com", "Feedback": "Carabiniere super in target con le prop ne ha già 3,è stato chiuso con un nostro prodotto da 1k sto aspettando il bonifico 15/11 Target età:sulla 40 ina", "Ad Set": "Contattato", "Stato": "Contattato", "Note": "fatta meet e chiuso"},
        {"Nome Completo": "Andrea Mastroianni", "Telefono": "p:+393803607312", "Email": "mybatuffolinoadorato@libero.it", "Feedback": "non risponde", "Ad Set": "non spunta su whattsapp", "Stato": "non spunta su whattsapp", "Note": ""},
        {"Nome Completo": "Vincenzo Buccafurri", "Telefono": "p:+393913153954", "Email": "enzopogn@gmail.com", "Feedback": "Deve darmi conferma lunedi 20 novembre sembra essere in targe è un camionista però piace questo settore", "Ad Set": "Contattato", "Stato": "Contattato", "Note": "fatta meet e questa settimana fine novembre parte sta aspettando dei soldii"},
        {"Nome Completo": "Giovanni Tardone", "Telefono": "p:+393345378479", "Email": "oleyvis@gmail.com", "Feedback": "dice di essere un trader ma non ha soldi", "Ad Set": "Contattato", "Stato": "Contattato", "Note": "fatta meet voleva solo info è scomparso"},
        {"Nome Completo": "Carmine Landi", "Telefono": "p:+393357314196", "Email": "bestconligus@gmail.com", "Feedback": "Fissata per il 15/11", "Ad Set": "in target,concorenza del nostro settore", "Stato": "contattato", "Note": "fatta meet è palesemente concorenza diceva di essere interessato e si finge di essere in ospedale"},
        {"Nome Completo": "Mario Dalmine", "Telefono": "p:+39333123456", "Email": "dalmine16@hotmail.com Non spunta su whattsapp contatatto su messaggi", "Feedback": "contattato", "Ad Set": "", "Stato": "", "Note": ""},
        {"Nome Completo": "Fabio", "Telefono": "p:+393467830743", "Email": "santoriello_fabio@yahoo.it", "Feedback": "Ex cliente,chiuso con un servizio da 800", "Ad Set": "contattato", "Stato": "contattato", "Note": "fatta meet e chiuso ex cliente"},
        {"Nome Completo": "Gaetano Cataneo", "Telefono": "p:+393482759865", "Email": "cataneo.g@libero.it", "Feedback": "non risponde mi ha bloccato sicuramente ha sbagliato fuori target.", "Ad Set": "contattato", "Stato": "contattato", "Note": ""},
        {"Nome Completo": "Stex Trader", "Telefono": "p:+393311977696", "Email": "sdelgobbo@gmail.com", "Feedback": "Super in target è un trader", "Ad Set": "contattato", "Stato": "contattato", "Note": ""},
        # Aggiungo alcuni altri record rappresentativi
        {"Nome Completo": "Luca Rizzo", "Telefono": "p:+393407290888", "Email": "lucarizzo1986@gmail.com non lo trovo su whattsapp", "Feedback": "contattato", "Ad Set": "", "Stato": "", "Note": ""},
        {"Nome Completo": "Domenico Manfredi", "Telefono": "p:+393791323170", "Email": "domenicoamanfredich@gmail.com avevamo la zoom e mi ha bloccato dal nulla prima di farla.", "Feedback": "contattato", "Ad Set": "Zoom fissata per luendi 3 dicembre", "Stato": "", "Note": ""},
        {"Nome Completo": "Sadio Coulibaly", "Telefono": "p:+393511850766", "Email": "sadiocoubaly777@gmail.com", "Feedback": "contattato", "Ad Set": "", "Stato": "", "Note": ""},
        {"Nome Completo": "Francesco Perrotta", "Telefono": "p:+393346122097", "Email": "francescoperrotta.fp@gmail.com", "Feedback": "contattato", "Ad Set": "", "Stato": "", "Note": ""},
        {"Nome Completo": "Wouroud", "Telefono": "p:+393397476903", "Email": "wardabenh95@gmail.com", "Feedback": "non spunta su whattsapp provo a chiamare inesistente", "Ad Set": "", "Stato": "", "Note": ""},
        {"Nome Completo": "Marco Cavallaro", "Telefono": "p:+393428261161", "Email": "cavallaromarcof.sco@outlook.it", "Feedback": "un coglione perditempo del cazzo senza budget", "Ad Set": "contattato", "Stato": "contattato", "Note": ""},
        {"Nome Completo": "Alessandro Franco", "Telefono": "p:+393240537171", "Email": "alessandrofranco30@gmail.com", "Feedback": "da fissare zoom", "Ad Set": "contattato", "Stato": "contattato", "Note": ""},
        {"Nome Completo": "Raffaele Di Chio", "Telefono": "p:+393287223874", "Email": "raffaeledichio13@gmail.com", "Feedback": "contattato", "Ad Set": "perditempo pochissimo budget da investuire", "Stato": "Zoom fissata per luendi 3 dicembre", "Note": ""},
        {"Nome Completo": "Pino Testa", "Telefono": "p:+393388281820", "Email": "pino.50@hotmail.it", "Feedback": "dovrà partire per natale da risentire", "Ad Set": "contattato", "Stato": "contattato", "Note": ""},
        {"Nome Completo": "Michele Sperti", "Telefono": "p:+393888566210", "Email": "sperti55@gmail.com", "Feedback": "Chiuso a 800", "Ad Set": "contattato", "Stato": "Zoom fissata per luendi 3 dicembre", "Note": ""},
        {"Nome Completo": "Cesare Puliti", "Telefono": "p:+393293912225", "Email": "puliti.cesare@gmail.com", "Feedback": "contattato", "Ad Set": "", "Stato": "", "Note": ""},
        {"Nome Completo": "Lucio", "Telefono": "p:+393426804307", "Email": "anedda.lucio@gmail.com", "Feedback": "super in target ha dei noleggi ha 40 anni è un imprenditore ha acquistato un servizio di 1699 diviso in 2 parti", "Ad Set": "contattato", "Stato": "Zoom fissata per luendi 3 dicembre", "Note": ""},
        {"Nome Completo": "Donatello", "Telefono": "p:+393341973973", "Email": "donatello.montanari@yahoo.com", "Feedback": "deve farmi sapere prossiam settiamna del 10 dicembre", "Ad Set": "contattato", "Stato": "Zoom fissata per martedi 4 dicembre", "Note": ""},
        {"Nome Completo": "Lorenzo", "Telefono": "p:+393701191271", "Email": "lorenzobusaccas4mini@gmail.com", "Feedback": "voleva solo info perditempo", "Ad Set": "contattato", "Stato": "contattato", "Note": ""},
        {"Nome Completo": "Edoardo Romano", "Telefono": "p:+393490561921", "Email": "edoromano84@live.it", "Feedback": "Da risentire 8 dicembre deve paralre con la compagna", "Ad Set": "contattato", "Stato": "contattato", "Note": ""},
        {"Nome Completo": "Mohamed Bibu", "Telefono": "p:+393883959244", "Email": "mohamedmahmoudismail695@gmail.com", "Feedback": "contattato", "Ad Set": "", "Stato": "", "Note": ""},
        {"Nome Completo": "Carmine Pucardi", "Telefono": "p:+393347312400", "Email": "carminepucardi@gmail.com", "Feedback": "contattato", "Ad Set": "", "Stato": "", "Note": ""},
        {"Nome Completo": "Ernesto Aiello", "Telefono": "p:+393920622629", "Email": "ernesto.aiello@gmail.com", "Feedback": "90 enne", "Ad Set": "contattato", "Stato": "contattato", "Note": ""}
    ]
    
    # Crea DataFrame
    df = pd.DataFrame(raw_data)
    
    # Pulisce e struttura i dati
    cleaned_data = []
    
    for _, row in df.iterrows():
        nome, cognome = extract_name_from_full_name(row['Nome Completo'])
        telefono = clean_phone_number(row['Telefono'])
        email = clean_email(row['Email'])
        feedback = clean_feedback_text(row['Feedback'])
        
        # Salta record senza nome o email valida
        if not nome or not email or '@' not in email:
            continue
        
        # Determina stato e priorità
        stato = categorize_lead_status(feedback)
        priorita = categorize_lead_priority(feedback)
        budget = extract_budget_from_feedback(feedback)
        
        # Crea record pulito
        cleaned_record = {
            'Nome': nome,
            'Cognome': cognome,
            'Email': email,
            'Telefono': telefono,
            'Azienda': '',  # Non disponibile nel dataset originale
            'Posizione': '',  # Non disponibile nel dataset originale
            'Fonte': determine_lead_source(),
            'Categoria': 'A' if priorita == 'Alta' else 'B' if priorita == 'Media' else 'C',
            'Stato': stato,
            'Priorità': priorita,
            'Budget': budget if budget else '',
            'Data Chiusura': '',  # Non disponibile nel dataset originale
            'Note': f"{feedback} | {row['Note']}".strip(' |')
        }
        
        cleaned_data.append(cleaned_record)
    
    return pd.DataFrame(cleaned_data)

def create_summary_report(df: pd.DataFrame) -> Dict:
    """Crea un report di riepilogo dei dati"""
    
    report = {
        'Totale Lead': len(df),
        'Per Stato': df['Stato'].value_counts().to_dict(),
        'Per Priorità': df['Priorità'].value_counts().to_dict(),
        'Con Budget': len(df[df['Budget'] != '']),
        'Con Telefono': len(df[df['Telefono'] != '']),
        'Con Email': len(df[df['Email'] != '']),
        'Budget Totale': df[df['Budget'] != '']['Budget'].sum() if len(df[df['Budget'] != '']) > 0 else 0
    }
    
    return report

def main():
    """Funzione principale"""
    
    print("🚀 Importazione e Pulizia Dati Google Sheet CRM Gemini Trading")
    print("=" * 70)
    
    try:
        # Crea dataset pulito
        print("📊 Creazione dataset pulito...")
        df_cleaned = create_cleaned_dataset()
        
        print(f"✅ Dataset creato: {len(df_cleaned)} record validi")
        
        # Crea report di riepilogo
        print("\n📈 Report di Riepilogo:")
        report = create_summary_report(df_cleaned)
        
        print(f"📊 Totale Lead: {report['Totale Lead']}")
        print(f"📞 Con Telefono: {report['Con Telefono']}")
        print(f"📧 Con Email: {report['Con Email']}")
        print(f"💰 Con Budget: {report['Con Budget']}")
        print(f"💵 Budget Totale: €{report['Budget Totale']:,.2f}")
        
        print("\n📋 Distribuzione per Stato:")
        for stato, count in report['Per Stato'].items():
            print(f"   • {stato}: {count}")
        
        print("\n🎯 Distribuzione per Priorità:")
        for priorita, count in report['Per Priorità'].items():
            print(f"   • {priorita}: {count}")
        
        # Salva file Excel pulito
        output_file = Path(__file__).parent / 'clients_cleaned_for_import.xlsx'
        df_cleaned.to_excel(output_file, index=False, engine='openpyxl')
        
        print(f"\n💾 File Excel creato: {output_file}")
        print(f"📊 Righe: {len(df_cleaned)}")
        print(f"📋 Colonne: {list(df_cleaned.columns)}")
        
        # Mostra anteprima
        print("\n👀 Anteprima dati:")
        print(df_cleaned.head(10).to_string(index=False))
        
        # Crea anche un file CSV per backup
        csv_file = Path(__file__).parent / 'clients_cleaned_for_import.csv'
        df_cleaned.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"\n📄 File CSV creato: {csv_file}")
        
        print("\n🎉 Importazione completata con successo!")
        print("💡 Ora puoi usare il file 'clients_cleaned_for_import.xlsx' per importare i clienti nella dashboard")
        
    except Exception as e:
        print(f"❌ Errore durante l'importazione: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
