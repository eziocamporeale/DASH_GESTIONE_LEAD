#!/usr/bin/env python3
"""
Script per creare 3 template standard per la sezione Contatti
Creato da Ezio Camporeale
"""

import os
from database.database_manager import DatabaseManager

def create_standard_contact_templates():
    """Crea 3 template standard per i contatti"""
    
    print("📞 Creazione template standard per contatti...")
    
    # Template standard
    templates = [
        {
            'name': 'Follow-up Iniziale',
            'type': 'email',
            'subject': 'Grazie per il tuo interesse - {company_name}',
            'content': '''Ciao {first_name},

Grazie per aver mostrato interesse nei nostri servizi di {service_type}.

Sono {agent_name} di {company_name} e sarei felice di aiutarti a valutare come possiamo supportare la tua azienda.

Vorrei programmare una breve chiamata di 15 minuti per:
- Comprendere meglio le tue esigenze
- Presentarti le nostre soluzioni più adatte
- Rispondere alle tue domande

Sei disponibile per una chiamata questa settimana?

Cordiali saluti,
{agent_name}
{company_name}
📞 {phone}
📧 {email}''',
            'category': 'Follow-up',
            'is_active': True
        },
        {
            'name': 'Proposta Commerciale',
            'type': 'email', 
            'subject': 'Proposta personalizzata per {company_name}',
            'content': '''Ciao {first_name},

Come promesso durante la nostra conversazione, ecco una proposta personalizzata per {company_name}.

📋 **LA NOSTRA PROPOSTA:**

🎯 **Obiettivo:** {objective}
💰 **Investimento:** {investment}
⏱️ **Timeline:** {timeline}
📈 **ROI Atteso:** {roi}

🔧 **SERVIZI INCLUSI:**
- {service_1}
- {service_2}
- {service_3}

📞 **PROSSIMI PASSI:**
1. Revisione della proposta
2. Chiamata di chiarimento (se necessario)
3. Firma del contratto
4. Avvio del progetto

Hai domande sulla proposta? Sono disponibile per una chiamata di 30 minuti per approfondire qualsiasi aspetto.

Cordiali saluti,
{agent_name}
{company_name}
📞 {phone}
📧 {email}''',
            'category': 'Proposta',
            'is_active': True
        },
        {
            'name': 'Reminder Chiusura',
            'type': 'email',
            'subject': 'Gentile reminder - Proposta {company_name}',
            'content': '''Ciao {first_name},

Spero che tu stia bene!

Ti scrivo per fare un follow-up sulla proposta che ti ho inviato per {company_name}.

📋 **RICAPITOLANDO:**
- Proposta inviata il: {proposal_date}
- Investimento: {investment}
- Scadenza offerta: {deadline}

🤔 **DOMANDE FREQUENTI:**
- Hai avuto modo di rivedere la proposta?
- Ci sono aspetti che vorresti chiarire?
- Hai domande sul processo di implementazione?

💡 **VALORE AGGIUNTO:**
Se procediamo entro {deadline}, includiamo gratuitamente:
- {bonus_1}
- {bonus_2}

Sono disponibile per una chiamata di 15 minuti per rispondere a qualsiasi tua domanda.

Cordiali saluti,
{agent_name}
{company_name}
📞 {phone}
📧 {email}''',
            'category': 'Reminder',
            'is_active': True
        }
    ]
    
    # Inizializza database
    db = DatabaseManager()
    
    print(f"📝 Creazione di {len(templates)} template standard...")
    
    success_count = 0
    for i, template in enumerate(templates, 1):
        try:
            print(f"\n{i}. Creazione template: {template['name']}")
            
            # Prepara i dati del template (solo campi essenziali)
            template_data = {
                'name': template['name'],
                'type': template['type'],
                'content': template['content'],
                'category': template['category'],
                'is_active': template['is_active']
            }
            
            # Aggiungi subject se presente (per email) - temporaneamente disabilitato
            # if 'subject' in template and template['subject']:
            #     template_data['subject'] = template['subject']
            
            # Crea il template
            success = db.create_contact_template(template_data)
            
            if success:
                print(f"   ✅ Template creato con successo")
                success_count += 1
            else:
                print(f"   ❌ Errore creazione template")
                
        except Exception as e:
            print(f"   ❌ Errore: {e}")
    
    print(f"\n🎯 RISULTATO:")
    print(f"✅ Template creati con successo: {success_count}/{len(templates)}")
    
    if success_count == len(templates):
        print("🎉 Tutti i template standard sono stati creati!")
        print("\n📋 TEMPLATE DISPONIBILI:")
        for template in templates:
            print(f"   • {template['name']} ({template['type']}) - {template['category']}")
    else:
        print("⚠️ Alcuni template non sono stati creati. Controlla i log per dettagli.")

if __name__ == "__main__":
    create_standard_contact_templates()
