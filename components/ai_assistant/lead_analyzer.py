#!/usr/bin/env python3
"""
Lead Analyzer - Analizzatore Lead AI
Analizza lead individuali e fornisce insights personalizzati
Creato da Ezio Camporeale
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Aggiungi il percorso della directory principale
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from components.ai_assistant.ai_core import AIAssistant
from database.database_manager import DatabaseManager

class LeadAnalyzer:
    """
    Analizzatore intelligente per singoli lead utilizzando AI
    """
    
    def __init__(self):
        """Inizializza l'analizzatore lead"""
        self.ai_assistant = AIAssistant()
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
        
        # Score weights per calcolo qualità lead
        self.score_weights = {
            'contact_info_completeness': 0.2,
            'company_info_completeness': 0.15,
            'budget_indication': 0.25,
            'timeline_urgency': 0.15,
            'source_quality': 0.1,
            'interaction_history': 0.15
        }
        
        # Threshold per categorizzazione
        self.score_thresholds = {
            'hot': 80,
            'warm': 60,
            'cold': 40
        }
    
    def analyze_lead(self, lead_id: int) -> Optional[Dict[str, Any]]:
        """
        Analizza un lead specifico e fornisce insights dettagliati
        
        Args:
            lead_id: ID del lead da analizzare
            
        Returns:
            Analisi completa del lead
        """
        try:
            # Recupera dati completi del lead
            lead_data = self._get_complete_lead_data(lead_id)
            if not lead_data:
                self.logger.error(f"❌ Lead {lead_id} non trovato")
                return None
            
            # Calcola score di qualità
            quality_score = self._calculate_lead_quality_score(lead_data)
            
            # Recupera storico contatti
            contact_history = self._get_lead_contact_history(lead_id)
            
            # Recupera attività recenti
            recent_activities = self._get_lead_recent_activities(lead_id)
            
            # Prepara dati per AI
            ai_data = self._prepare_ai_data(lead_data, contact_history, recent_activities)
            
            # Genera analisi AI
            ai_analysis = self.ai_assistant.generate_response(
                prompt_type='lead_analysis',
                data=ai_data
            )
            
            # Se AI non disponibile, usa analisi di base
            if not ai_analysis:
                self.logger.warning("⚠️ AI non disponibile, usando analisi di base")
                ai_analysis = self._generate_basic_analysis(lead_data, contact_history, recent_activities)
            
            # Struttura la risposta
            analysis_result = {
                'lead_id': lead_id,
                'analysis_content': ai_analysis,
                'quality_score': quality_score,
                'quality_category': self._categorize_lead_quality(quality_score),
                'generated_at': datetime.now().isoformat(),
                'lead_info': {
                    'name': f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}",
                    'company': lead_data.get('company', ''),
                    'email': lead_data.get('email', ''),
                    'phone': lead_data.get('phone', ''),
                    'industry': lead_data.get('industry', ''),
                    'source': lead_data.get('source', ''),
                    'status': lead_data.get('status_name', ''),
                    'priority': lead_data.get('priority_name', ''),
                    'category': lead_data.get('category_name', '')
                },
                'contact_history': contact_history,
                'recent_activities': recent_activities,
                'score_breakdown': self._get_score_breakdown(lead_data),
                'recommendations': self._generate_recommendations(lead_data, quality_score),
                'ai_metadata': {
                    'model_used': 'deepseek-chat',
                    'generation_time': datetime.now().isoformat(),
                    'data_points_analyzed': len(ai_data)
                }
            }
            
            self.logger.info(f"✅ Analisi completata per lead {lead_id} - Score: {quality_score}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"❌ Errore analisi lead: {e}")
            return None
    
    def _generate_basic_analysis(self, lead_data: Dict[str, Any], contact_history: List[Dict], recent_activities: List[Dict]) -> str:
        """Genera analisi di base quando AI non è disponibile"""
        
        # Calcola score di base
        score = 0
        factors = []
        
        # Budget
        budget = lead_data.get('budget', 0)
        if budget > 10000:
            score += 25
            factors.append("Budget elevato")
        elif budget > 5000:
            score += 15
            factors.append("Budget medio")
        else:
            score += 5
            factors.append("Budget limitato")
        
        # Contatti
        if contact_history:
            score += 20
            factors.append("Storico contatti presente")
        
        # Attività recenti
        if recent_activities:
            score += 15
            factors.append("Attività recenti")
        
        # Settore
        industry = lead_data.get('industry', '').lower()
        if industry in ['tecnologia', 'finanza', 'consulenza']:
            score += 10
            factors.append("Settore promettente")
        
        # Email valida
        email = lead_data.get('email', '')
        if '@' in email and '.' in email.split('@')[1]:
            score += 10
            factors.append("Email valida")
        
        # Telefono
        phone = lead_data.get('phone', '')
        if phone and len(phone) > 8:
            score += 10
            factors.append("Telefono presente")
        
        # Categoria score
        if score >= 80:
            category = "Alta"
        elif score >= 60:
            category = "Media"
        elif score >= 40:
            category = "Bassa"
        else:
            category = "Molto Bassa"
        
        # Genera analisi
        analysis = f"""
**Analisi Lead (Modalità Offline)**

**Score Qualità:** {score}/100 ({category})

**Fattori Positivi:**
{chr(10).join(f"- {factor}" for factor in factors)}

**Probabilità Conversione:** {self._get_conversion_probability(score)}

**Approccio Consigliato:**
1. Contatto entro 24-48 ore
2. Focus sui benefici specifici del settore
3. Presentazione personalizzata
4. Follow-up regolare

**Timing Ottimale:**
- Chiamata: Mattina (9-11) o Pomeriggio (15-17)
- Email: Martedì-Giovedì, ore 10-14

**Note:** Analisi generata automaticamente. Per insights avanzati, riprova quando la connessione AI è disponibile.
        """
        
        return analysis.strip()
    
    def _get_conversion_probability(self, score: int) -> str:
        """Calcola probabilità di conversione basata sullo score"""
        if score >= 80:
            return "Alta (75-90%)"
        elif score >= 60:
            return "Media-Alta (50-75%)"
        elif score >= 40:
            return "Media (25-50%)"
        else:
            return "Bassa (10-25%)"
    
    def analyze_multiple_leads(self, lead_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Analizza multiple lead contemporaneamente
        
        Args:
            lead_ids: Lista di ID lead da analizzare
            
        Returns:
            Lista di analisi per ogni lead
        """
        analyses = []
        
        for lead_id in lead_ids:
            analysis = self.analyze_lead(lead_id)
            if analysis:
                analyses.append(analysis)
        
        self.logger.info(f"✅ Analizzate {len(analyses)} lead su {len(lead_ids)} richieste")
        return analyses
    
    def get_lead_comparison(self, lead_ids: List[int]) -> Optional[Dict[str, Any]]:
        """
        Confronta multiple lead e fornisce insights comparativi
        
        Args:
            lead_ids: Lista di ID lead da confrontare
            
        Returns:
            Analisi comparativa
        """
        try:
            if len(lead_ids) < 2:
                self.logger.warning("⚠️ Serve almeno 2 lead per il confronto")
                return None
            
            # Analizza tutti i lead
            analyses = self.analyze_multiple_leads(lead_ids)
            
            if len(analyses) < 2:
                return None
            
            # Prepara dati comparativi
            comparison_data = self._prepare_comparison_data(analyses)
            
            # Genera analisi comparativa con AI
            ai_data = {
                'lead_data': json.dumps(comparison_data, indent=2),
                'contact_history': json.dumps([a['contact_history'] for a in analyses], indent=2),
                'recent_activities': json.dumps([a['recent_activities'] for a in analyses], indent=2)
            }
            
            comparison_analysis = self.ai_assistant.generate_response(
                prompt_type='lead_analysis',
                data=ai_data
            )
            
            if not comparison_analysis:
                return None
            
            return {
                'comparison_analysis': comparison_analysis,
                'individual_analyses': analyses,
                'comparison_data': comparison_data,
                'generated_at': datetime.now().isoformat(),
                'leads_compared': len(analyses)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Errore confronto lead: {e}")
            return None
    
    def get_lead_trend_analysis(self, lead_id: int, days: int = 30) -> Optional[Dict[str, Any]]:
        """
        Analizza i trend di un lead nel tempo
        
        Args:
            lead_id: ID del lead
            days: Periodo di analisi in giorni
            
        Returns:
            Analisi dei trend
        """
        try:
            # Recupera storico completo
            history_data = self._get_lead_history_trend(lead_id, days)
            
            if not history_data:
                return None
            
            # Prepara dati per AI
            ai_data = {
                'lead_data': json.dumps(history_data.get('lead_info', {}), indent=2),
                'contact_history': json.dumps(history_data.get('contacts', []), indent=2),
                'recent_activities': json.dumps(history_data.get('activities', []), indent=2),
                'trend_data': json.dumps(history_data.get('trends', {}), indent=2)
            }
            
            # Genera analisi trend
            trend_analysis = self.ai_assistant.generate_response(
                prompt_type='lead_analysis',
                data=ai_data
            )
            
            if not trend_analysis:
                return None
            
            return {
                'trend_analysis': trend_analysis,
                'history_data': history_data,
                'analysis_period_days': days,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Errore analisi trend: {e}")
            return None
    
    def _get_complete_lead_data(self, lead_id: int) -> Optional[Dict[str, Any]]:
        """Recupera tutti i dati di un lead"""
        try:
            query = """
            SELECT 
                l.*,
                ls.name as status_name,
                lp.name as priority_name,
                lc.name as category_name,
                u.first_name as assigned_user_first_name,
                u.last_name as assigned_user_last_name,
                ur.name as assigned_user_role
            FROM leads l
            LEFT JOIN lead_states ls ON l.status_id = ls.id
            LEFT JOIN lead_priorities lp ON l.priority_id = lp.id  
            LEFT JOIN lead_categories lc ON l.category_id = lc.id
            LEFT JOIN users u ON l.assigned_user_id = u.id
            LEFT JOIN user_roles ur ON u.role_id = ur.id
            WHERE l.id = %s
            """
            
            result = self.db_manager.execute_query(query, (lead_id,))
            
            if result and len(result) > 0:
                return result[0]
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Errore recupero dati lead: {e}")
            return None
    
    def _calculate_lead_quality_score(self, lead_data: Dict[str, Any]) -> int:
        """Calcola il score di qualità del lead"""
        try:
            score = 0
            
            # Completezza informazioni contatto (0-20 punti)
            contact_score = 0
            if lead_data.get('first_name'): contact_score += 5
            if lead_data.get('last_name'): contact_score += 5
            if lead_data.get('email'): contact_score += 5
            if lead_data.get('phone'): contact_score += 5
            score += contact_score * self.score_weights['contact_info_completeness']
            
            # Completezza informazioni azienda (0-15 punti)
            company_score = 0
            if lead_data.get('company'): company_score += 5
            if lead_data.get('industry'): company_score += 5
            if lead_data.get('website'): company_score += 5
            score += company_score * self.score_weights['company_info_completeness']
            
            # Indicazione budget (0-25 punti)
            budget_score = 0
            if lead_data.get('budget'):
                try:
                    budget = float(lead_data.get('budget', 0))
                    if budget > 10000: budget_score = 25
                    elif budget > 5000: budget_score = 20
                    elif budget > 1000: budget_score = 15
                    elif budget > 0: budget_score = 10
                except:
                    pass
            score += budget_score * self.score_weights['budget_indication']
            
            # Urgenza timeline (0-15 punti)
            timeline_score = 0
            if lead_data.get('notes'):
                notes = lead_data.get('notes', '').lower()
                urgent_words = ['urgente', 'immediato', 'subito', 'asap', 'presto']
                if any(word in notes for word in urgent_words):
                    timeline_score = 15
                elif 'settimana' in notes or 'giorni' in notes:
                    timeline_score = 10
                elif 'mese' in notes:
                    timeline_score = 5
            score += timeline_score * self.score_weights['timeline_urgency']
            
            # Qualità fonte (0-10 punti)
            source_score = 0
            source = lead_data.get('source', '').lower()
            high_quality_sources = ['referral', 'website', 'linkedin']
            medium_quality_sources = ['email', 'social', 'event']
            if source in high_quality_sources:
                source_score = 10
            elif source in medium_quality_sources:
                source_score = 7
            elif source:
                source_score = 5
            score += source_score * self.score_weights['source_quality']
            
            # Storico interazioni (0-15 punti)
            interaction_score = 0
            # Questo sarà calcolato basandosi sui contatti effettuati
            # Per ora assegniamo un punteggio base
            interaction_score = 10  # Placeholder
            score += interaction_score * self.score_weights['interaction_history']
            
            return min(100, max(0, int(score)))
            
        except Exception as e:
            self.logger.error(f"❌ Errore calcolo score: {e}")
            return 50  # Score di default
    
    def _categorize_lead_quality(self, score: int) -> str:
        """Categorizza la qualità del lead basata sul score"""
        if score >= self.score_thresholds['hot']:
            return 'Hot'
        elif score >= self.score_thresholds['warm']:
            return 'Warm'
        else:
            return 'Cold'
    
    def _get_lead_contact_history(self, lead_id: int) -> List[Dict[str, Any]]:
        """Recupera lo storico dei contatti per un lead"""
        try:
            query = """
            SELECT 
                ch.*,
                ct.name as template_name,
                ct.type as template_type,
                u.first_name as user_first_name,
                u.last_name as user_last_name
            FROM contact_history ch
            LEFT JOIN contact_templates ct ON ch.template_id = ct.id
            LEFT JOIN users u ON ch.user_id = u.id
            WHERE ch.lead_id = %s
            ORDER BY ch.created_at DESC
            LIMIT 10
            """
            
            result = self.db_manager.execute_query(query, (lead_id,))
            return result or []
            
        except Exception as e:
            self.logger.error(f"❌ Errore recupero storico contatti: {e}")
            return []
    
    def _get_lead_recent_activities(self, lead_id: int) -> List[Dict[str, Any]]:
        """Recupera le attività recenti per un lead"""
        try:
            query = """
            SELECT 
                t.*,
                ts.name as status_name,
                tp.name as priority_name,
                u.first_name as assigned_user_first_name,
                u.last_name as assigned_user_last_name
            FROM tasks t
            LEFT JOIN task_states ts ON t.status_id = ts.id
            LEFT JOIN task_priorities tp ON t.priority_id = tp.id
            LEFT JOIN users u ON t.assigned_user_id = u.id
            WHERE t.lead_id = %s
            ORDER BY t.created_at DESC
            LIMIT 5
            """
            
            result = self.db_manager.execute_query(query, (lead_id,))
            return result or []
            
        except Exception as e:
            self.logger.error(f"❌ Errore recupero attività recenti: {e}")
            return []
    
    def _prepare_ai_data(self, lead_data: Dict[str, Any], contact_history: List[Dict[str, Any]], 
                        recent_activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepara i dati per l'AI in formato ottimale"""
        return {
            'lead_data': json.dumps(lead_data, indent=2),
            'contact_history': json.dumps(contact_history, indent=2),
            'recent_activities': json.dumps(recent_activities, indent=2)
        }
    
    def _get_score_breakdown(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Restituisce il breakdown dettagliato del score"""
        return {
            'contact_info_completeness': self._calculate_contact_completeness(lead_data),
            'company_info_completeness': self._calculate_company_completeness(lead_data),
            'budget_indication': self._calculate_budget_score(lead_data),
            'timeline_urgency': self._calculate_timeline_score(lead_data),
            'source_quality': self._calculate_source_score(lead_data),
            'interaction_history': self._calculate_interaction_score(lead_data)
        }
    
    def _calculate_contact_completeness(self, lead_data: Dict[str, Any]) -> int:
        """Calcola completezza informazioni contatto"""
        score = 0
        if lead_data.get('first_name'): score += 25
        if lead_data.get('last_name'): score += 25
        if lead_data.get('email'): score += 25
        if lead_data.get('phone'): score += 25
        return score
    
    def _calculate_company_completeness(self, lead_data: Dict[str, Any]) -> int:
        """Calcola completezza informazioni azienda"""
        score = 0
        if lead_data.get('company'): score += 33
        if lead_data.get('industry'): score += 33
        if lead_data.get('website'): score += 34
        return score
    
    def _calculate_budget_score(self, lead_data: Dict[str, Any]) -> int:
        """Calcola score basato su budget"""
        if lead_data.get('budget'):
            try:
                budget = float(lead_data.get('budget', 0))
                if budget > 10000: return 100
                elif budget > 5000: return 80
                elif budget > 1000: return 60
                elif budget > 0: return 40
            except:
                pass
        return 0
    
    def _calculate_timeline_score(self, lead_data: Dict[str, Any]) -> int:
        """Calcola score basato su urgenza timeline"""
        if lead_data.get('notes'):
            notes = lead_data.get('notes', '').lower()
            urgent_words = ['urgente', 'immediato', 'subito', 'asap', 'presto']
            if any(word in notes for word in urgent_words):
                return 100
            elif 'settimana' in notes or 'giorni' in notes:
                return 67
            elif 'mese' in notes:
                return 33
        return 0
    
    def _calculate_source_score(self, lead_data: Dict[str, Any]) -> int:
        """Calcola score basato su qualità fonte"""
        source = lead_data.get('source', '').lower()
        high_quality_sources = ['referral', 'website', 'linkedin']
        medium_quality_sources = ['email', 'social', 'event']
        if source in high_quality_sources:
            return 100
        elif source in medium_quality_sources:
            return 70
        elif source:
            return 50
        return 0
    
    def _calculate_interaction_score(self, lead_data: Dict[str, Any]) -> int:
        """Calcola score basato su interazioni"""
        # Placeholder - in futuro si può basare sui contatti effettuati
        return 70
    
    def _generate_recommendations(self, lead_data: Dict[str, Any], quality_score: int) -> List[str]:
        """Genera raccomandazioni basate sui dati del lead"""
        recommendations = []
        
        # Raccomandazioni basate su completezza
        if not lead_data.get('phone'):
            recommendations.append("Raccogliere numero di telefono per contatto diretto")
        if not lead_data.get('company'):
            recommendations.append("Identificare l'azienda di appartenenza")
        if not lead_data.get('budget'):
            recommendations.append("Valutare il budget disponibile")
        
        # Raccomandazioni basate su score
        if quality_score < 40:
            recommendations.append("Lead freddo - concentrarsi su nurturing e educazione")
        elif quality_score < 70:
            recommendations.append("Lead tiepido - mantenere follow-up regolari")
        else:
            recommendations.append("Lead caldo - procedere con proposta commerciale")
        
        # Raccomandazioni basate su fonte
        source = lead_data.get('source', '').lower()
        if source == 'cold_call':
            recommendations.append("Preparare script personalizzato per cold calling")
        elif source == 'email':
            recommendations.append("Seguire con chiamata telefonica")
        
        return recommendations
    
    def _prepare_comparison_data(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepara dati per confronto tra lead"""
        return {
            'lead_count': len(analyses),
            'avg_quality_score': sum(a['quality_score'] for a in analyses) / len(analyses),
            'quality_distribution': {
                'hot': sum(1 for a in analyses if a['quality_category'] == 'Hot'),
                'warm': sum(1 for a in analyses if a['quality_category'] == 'Warm'),
                'cold': sum(1 for a in analyses if a['quality_category'] == 'Cold')
            },
            'common_industries': {},
            'common_sources': {},
            'budget_ranges': {}
        }
    
    def _get_lead_history_trend(self, lead_id: int, days: int) -> Optional[Dict[str, Any]]:
        """Recupera dati storici per analisi trend"""
        try:
            # Implementazione semplificata
            return {
                'lead_info': self._get_complete_lead_data(lead_id),
                'contacts': self._get_lead_contact_history(lead_id),
                'activities': self._get_lead_recent_activities(lead_id),
                'trends': {}
            }
        except Exception as e:
            self.logger.error(f"❌ Errore recupero storico trend: {e}")
            return None
