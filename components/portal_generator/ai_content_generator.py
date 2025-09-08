#!/usr/bin/env python3
"""
AI Content Generator per DASH_GESTIONE_LEAD
Generatore di contenuti AI per portali web
Creato da Ezio Camporeale
"""

import json
import random
from typing import Dict, List
from datetime import datetime

class AIContentGenerator:
    """Generatore di contenuti AI per portali web"""
    
    def __init__(self):
        """Inizializza il generatore AI"""
        self.setup_content_templates()
        self.setup_sector_keywords()
        self.setup_business_phrases()
    
    def setup_content_templates(self):
        """Configura i template di contenuto"""
        self.content_templates = {
            'hero_titles': [
                "Trasforma il tuo business con {sector}",
                "La soluzione {sector} che stavi cercando",
                "Eccellenza nel settore {sector}",
                "Innovazione e qualità in {sector}",
                "Il tuo partner di fiducia in {sector}"
            ],
            'hero_subtitles': [
                "Scopri come possiamo aiutarti a raggiungere i tuoi obiettivi",
                "Soluzioni personalizzate per il tuo successo",
                "Esperienza e competenza al tuo servizio",
                "Risultati garantiti per il tuo business",
                "La tua crescita è la nostra priorità"
            ],
            'feature_titles': [
                "Esperienza Comprovata",
                "Soluzioni Innovative", 
                "Supporto Dedicato",
                "Risultati Misurabili",
                "Qualità Garantita"
            ],
            'feature_descriptions': [
                "Anni di esperienza nel settore per garantirti il massimo risultato",
                "Tecnologie all'avanguardia per soluzioni sempre aggiornate",
                "Un team di esperti sempre al tuo fianco",
                "Metriche chiare per monitorare i tuoi progressi",
                "Standard di qualità elevati in ogni progetto"
            ],
            'testimonials': [
                "Servizio eccellente e risultati oltre le aspettative",
                "Professionalità e competenza al massimo livello",
                "Consigliamo vivamente per la qualità del servizio",
                "Partner affidabile per il nostro business",
                "Risultati concreti e misurabili"
            ]
        }
    
    def setup_sector_keywords(self):
        """Configura le parole chiave per settore"""
        self.sector_keywords = {
            'finanza': {
                'keywords': ['investimenti', 'consulenza finanziaria', 'gestione patrimoni', 'pianificazione', 'risparmio'],
                'benefits': ['crescita patrimoniale', 'sicurezza finanziaria', 'rendimenti ottimali', 'rischio controllato'],
                'services': ['Consulenza Finanziaria', 'Gestione Portafogli', 'Pianificazione Pensionistica', 'Assicurazioni']
            },
            'immobiliare': {
                'keywords': ['immobili', 'vendita', 'acquisto', 'affitto', 'investimenti immobiliari'],
                'benefits': ['valore immobiliare', 'rendita locativa', 'plusvalenze', 'diversificazione'],
                'services': ['Vendita Immobili', 'Acquisto Casa', 'Affitti', 'Valutazioni Immobiliari']
            },
            'ecommerce': {
                'keywords': ['vendite online', 'negozio digitale', 'marketing digitale', 'e-commerce', 'online store'],
                'benefits': ['vendite aumentate', 'presenza digitale', 'clienti globali', 'automazione'],
                'services': ['Store Online', 'Marketing Digitale', 'Gestione Ordini', 'Customer Service']
            },
            'consulenza': {
                'keywords': ['consulenza', 'strategia', 'business', 'crescita', 'ottimizzazione'],
                'benefits': ['efficienza operativa', 'crescita sostenibile', 'processi ottimizzati', 'ROI migliorato'],
                'services': ['Consulenza Strategica', 'Business Planning', 'Process Optimization', 'Training']
            },
            'tech': {
                'keywords': ['tecnologia', 'innovazione', 'digitalizzazione', 'software', 'automazione'],
                'benefits': ['efficienza digitale', 'processi automatizzati', 'scalabilità', 'competitività'],
                'services': ['Sviluppo Software', 'Digital Transformation', 'IT Consulting', 'Cloud Solutions']
            },
            'salute': {
                'keywords': ['salute', 'benessere', 'cura', 'prevenzione', 'medicina'],
                'benefits': ['qualità della vita', 'prevenzione', 'cure avanzate', 'benessere'],
                'services': ['Consulenze Mediche', 'Prevenzione', 'Terapie', 'Check-up']
            },
            'educazione': {
                'keywords': ['formazione', 'apprendimento', 'educazione', 'corsi', 'competenze'],
                'benefits': ['crescita personale', 'competenze aggiornate', 'carriera', 'conoscenza'],
                'services': ['Corsi Online', 'Formazione Aziendale', 'Certificazioni', 'E-learning']
            },
            'marketing': {
                'keywords': ['marketing', 'promozione', 'branding', 'comunicazione', 'pubblicità'],
                'benefits': ['visibilità aumentata', 'brand awareness', 'lead generation', 'conversioni'],
                'services': ['Digital Marketing', 'Branding', 'Social Media', 'Advertising']
            }
        }
    
    def setup_business_phrases(self):
        """Configura frasi business generiche"""
        self.business_phrases = {
            'company_descriptions': [
                "Azienda leader nel settore con anni di esperienza",
                "Partner affidabile per la crescita del tuo business",
                "Esperienza e competenza al servizio dei clienti",
                "Innovazione e qualità per risultati eccellenti",
                "Soluzioni personalizzate per ogni esigenza"
            ],
            'value_propositions': [
                "Risultati garantiti e misurabili",
                "Approccio personalizzato per ogni cliente",
                "Tecnologie all'avanguardia",
                "Supporto continuo e dedicato",
                "Esperienza comprovata nel settore"
            ],
            'call_to_actions': [
                "Scopri come possiamo aiutarti",
                "Inizia il tuo percorso di successo",
                "Contattaci per una consulenza gratuita",
                "Richiedi informazioni senza impegno",
                "Prenota una demo personalizzata"
            ]
        }
    
    def enhance_portal_data(self, portal_data: Dict) -> Dict:
        """
        Migliora i dati del portale con contenuti AI generati
        
        Args:
            portal_data: Dati originali del portale
            
        Returns:
            Dict con dati arricchiti
        """
        enhanced_data = portal_data.copy()
        
        # Ottieni informazioni del settore
        sector = portal_data.get('sector', 'altro')
        sector_info = self.sector_keywords.get(sector, self.sector_keywords['consulenza'])
        
        # Genera contenuti dinamici
        enhanced_data.update({
            'hero_title': self._generate_hero_title(portal_data),
            'hero_subtitle': self._generate_hero_subtitle(portal_data),
            'company_description': self._generate_company_description(portal_data),
            'features': self._generate_features(portal_data, sector_info),
            'services': self._generate_services(portal_data, sector_info),
            'testimonials': self._generate_testimonials(portal_data),
            'value_proposition': self._generate_value_proposition(portal_data),
            'call_to_action': self._generate_call_to_action(portal_data),
            'meta_description': self._generate_meta_description(portal_data),
            'meta_keywords': self._generate_meta_keywords(portal_data, sector_info),
            'contact_info': self._generate_contact_info(portal_data),
            'social_links': self._generate_social_links(portal_data),
            'generated_at': datetime.now().isoformat(),
            'ai_enhanced': True
        })
        
        return enhanced_data
    
    def _generate_hero_title(self, data: Dict) -> str:
        """Genera titolo hero personalizzato"""
        sector = data.get('sector', 'business')
        company_name = data.get('company_name', '')
        
        if company_name:
            templates = [
                f"{company_name} - Eccellenza in {sector}",
                f"{company_name} - Il tuo partner in {sector}",
                f"{company_name} - Soluzioni {sector} innovative"
            ]
        else:
            templates = self.content_templates['hero_titles']
        
        template = random.choice(templates)
        return template.format(sector=sector.title())
    
    def _generate_hero_subtitle(self, data: Dict) -> str:
        """Genera sottotitolo hero"""
        business_goals = data.get('business_goals', '')
        
        if business_goals:
            return business_goals
        else:
            return random.choice(self.content_templates['hero_subtitles'])
    
    def _generate_company_description(self, data: Dict) -> str:
        """Genera descrizione azienda"""
        company_name = data.get('company_name', 'La nostra azienda')
        sector = data.get('sector', 'business')
        
        base_description = random.choice(self.business_phrases['company_descriptions'])
        
        return f"{company_name} è un'{base_description.lower()} {sector}. {random.choice(self.business_phrases['value_propositions'])}."
    
    def _generate_features(self, data: Dict, sector_info: Dict) -> List[Dict]:
        """Genera caratteristiche principali"""
        features = []
        
        # Caratteristiche generiche
        generic_features = [
            {
                'title': 'Esperienza Comprovata',
                'description': 'Anni di esperienza nel settore per garantirti risultati eccellenti',
                'icon': '🏆'
            },
            {
                'title': 'Soluzioni Personalizzate',
                'description': 'Approccio su misura per ogni esigenza specifica',
                'icon': '🎯'
            },
            {
                'title': 'Supporto Dedicato',
                'description': 'Un team di esperti sempre al tuo fianco',
                'icon': '🤝'
            }
        ]
        
        # Aggiungi caratteristiche specifiche del settore
        if sector_info:
            sector_features = [
                {
                    'title': f'Specializzazione {data.get("sector", "Business").title()}',
                    'description': f'Competenze specifiche nel settore {data.get("sector", "business")}',
                    'icon': '💼'
                },
                {
                    'title': 'Risultati Misurabili',
                    'description': f'Metriche chiare per monitorare i progressi in {data.get("sector", "business")}',
                    'icon': '📊'
                }
            ]
            generic_features.extend(sector_features)
        
        # Seleziona 3-4 caratteristiche casuali
        selected_features = random.sample(generic_features, min(4, len(generic_features)))
        
        return selected_features
    
    def _generate_services(self, data: Dict, sector_info: Dict) -> List[Dict]:
        """Genera servizi offerti"""
        services = []
        
        # Servizi generici
        generic_services = [
            'Consulenza Strategica',
            'Supporto Operativo',
            'Formazione e Training',
            'Analisi e Reporting'
        ]
        
        # Servizi specifici del settore
        if sector_info and 'services' in sector_info:
            services.extend(sector_info['services'])
        else:
            services.extend(generic_services)
        
        # Seleziona 3-5 servizi
        selected_services = random.sample(services, min(5, len(services)))
        
        return [{'name': service, 'description': f'Servizio professionale di {service.lower()}'} for service in selected_services]
    
    def _generate_testimonials(self, data: Dict) -> List[Dict]:
        """Genera testimonianze clienti"""
        testimonials = []
        
        # Nomi e aziende fittizi
        fake_clients = [
            {'name': 'Marco Rossi', 'company': 'ABC SRL', 'role': 'CEO'},
            {'name': 'Laura Bianchi', 'company': 'XYZ SpA', 'role': 'Direttore'},
            {'name': 'Giuseppe Verdi', 'company': 'DEF Srl', 'role': 'Manager'},
            {'name': 'Anna Neri', 'company': 'GHI SRL', 'role': 'Imprenditore'},
            {'name': 'Paolo Blu', 'company': 'JKL SpA', 'role': 'Amministratore'}
        ]
        
        # Genera 2-3 testimonianze
        selected_clients = random.sample(fake_clients, min(3, len(fake_clients)))
        
        for client in selected_clients:
            testimonials.append({
                'name': client['name'],
                'company': client['company'],
                'role': client['role'],
                'text': random.choice(self.content_templates['testimonials']),
                'rating': random.randint(4, 5)
            })
        
        return testimonials
    
    def _generate_value_proposition(self, data: Dict) -> str:
        """Genera proposta di valore"""
        return random.choice(self.business_phrases['value_propositions'])
    
    def _generate_call_to_action(self, data: Dict) -> str:
        """Genera call to action"""
        return random.choice(self.business_phrases['call_to_actions'])
    
    def _generate_meta_description(self, data: Dict) -> str:
        """Genera meta description SEO"""
        company_name = data.get('company_name', 'Azienda')
        sector = data.get('sector', 'business')
        portal_name = data.get('portal_name', 'Portale')
        
        return f"{portal_name} di {company_name}. Servizi professionali nel settore {sector}. Contattaci per una consulenza gratuita."
    
    def _generate_meta_keywords(self, data: Dict, sector_info: Dict) -> str:
        """Genera meta keywords SEO"""
        keywords = []
        
        # Keywords del settore
        if sector_info and 'keywords' in sector_info:
            keywords.extend(sector_info['keywords'])
        
        # Keywords generiche
        keywords.extend(['consulenza', 'professionale', 'qualità', 'risultati'])
        
        # Keywords specifiche del portale
        portal_name = data.get('portal_name', '').lower().split()
        keywords.extend(portal_name)
        
        # Rimuovi duplicati e limita a 10
        unique_keywords = list(dict.fromkeys(keywords))[:10]
        
        return ', '.join(unique_keywords)
    
    def _generate_contact_info(self, data: Dict) -> Dict:
        """Genera informazioni di contatto"""
        company_name = data.get('company_name', 'Azienda')
        
        return {
            'email': f'info@{company_name.lower().replace(" ", "")}.com',
            'phone': '+39 123 456 7890',
            'address': 'Via Roma 123, Milano, Italia',
            'website': f'www.{company_name.lower().replace(" ", "")}.com'
        }
    
    def _generate_social_links(self, data: Dict) -> Dict:
        """Genera link social"""
        company_name = data.get('company_name', 'azienda').lower().replace(' ', '')
        
        return {
            'facebook': f'https://facebook.com/{company_name}',
            'linkedin': f'https://linkedin.com/company/{company_name}',
            'twitter': f'https://twitter.com/{company_name}',
            'instagram': f'https://instagram.com/{company_name}'
        }
    
    def generate_sector_specific_content(self, sector: str, content_type: str) -> str:
        """
        Genera contenuti specifici per settore
        
        Args:
            sector: Settore di riferimento
            content_type: Tipo di contenuto da generare
            
        Returns:
            Contenuto generato
        """
        sector_info = self.sector_keywords.get(sector, self.sector_keywords['consulenza'])
        
        if content_type == 'benefits':
            return ', '.join(sector_info.get('benefits', ['benefici professionali']))
        elif content_type == 'keywords':
            return ', '.join(sector_info.get('keywords', ['servizi professionali']))
        else:
            return f"Contenuto specifico per il settore {sector}"
    
    def generate_dynamic_text(self, template: str, data: Dict) -> str:
        """
        Genera testo dinamico da template
        
        Args:
            template: Template con placeholder
            data: Dati per sostituire i placeholder
            
        Returns:
            Testo generato
        """
        try:
            return template.format(**data)
        except KeyError as e:
            # Se manca un placeholder, usa un valore di default
            missing_key = str(e).strip("'")
            data[missing_key] = f"[{missing_key}]"
            return template.format(**data)
    
    def get_content_suggestions(self, portal_data: Dict) -> List[str]:
        """
        Ottiene suggerimenti per migliorare i contenuti
        
        Args:
            portal_data: Dati del portale
            
        Returns:
            Lista di suggerimenti
        """
        suggestions = []
        
        # Controlla campi mancanti
        if not portal_data.get('company_name'):
            suggestions.append("Aggiungi il nome dell'azienda per personalizzare meglio i contenuti")
        
        if not portal_data.get('business_goals'):
            suggestions.append("Definisci gli obiettivi business per contenuti più mirati")
        
        if not portal_data.get('target_audience'):
            suggestions.append("Specifica il target audience per contenuti più efficaci")
        
        # Suggerimenti per settore
        sector = portal_data.get('sector', 'altro')
        if sector in self.sector_keywords:
            suggestions.append(f"Considera di aggiungere contenuti specifici per il settore {sector}")
        
        # Suggerimenti per tipo portale
        portal_type = portal_data.get('portal_type', 'landing_page')
        if portal_type == 'ecommerce':
            suggestions.append("Aggiungi informazioni sui prodotti e prezzi")
        elif portal_type == 'portfolio':
            suggestions.append("Includi esempi di progetti e case study")
        elif portal_type == 'blog':
            suggestions.append("Pianifica una strategia di contenuti regolari")
        
        return suggestions
