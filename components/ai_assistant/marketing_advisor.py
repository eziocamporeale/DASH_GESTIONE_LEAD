#!/usr/bin/env python3
"""
Marketing Advisor - Sistema Consigli Marketing AI
Fornisce consigli strategici per venditori e team marketing
Creato da Ezio Camporeale
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import sys
import pandas as pd

# Aggiungi il percorso della directory principale
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from components.ai_assistant.ai_core import AIAssistant
from database.database_manager import DatabaseManager

class MarketingAdvisor:
    """
    Sistema di consigli marketing intelligenti utilizzando AI
    """
    
    def __init__(self):
        """Inizializza l'advisor marketing"""
        self.ai_assistant = AIAssistant()
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
        
        # Tipi di consigli disponibili
        self.advice_types = {
            'campaign_optimization': {
                'name': 'Ottimizzazione Campagne',
                'description': 'Consigli per migliorare le performance delle campagne',
                'focus': 'ROI, conversioni, targeting'
            },
            'lead_generation': {
                'name': 'Generazione Lead',
                'description': 'Strategie per aumentare la qualità e quantità dei lead',
                'focus': 'Canali, contenuti, timing'
            },
            'team_performance': {
                'name': 'Performance Team',
                'description': 'Consigli per migliorare le performance del team',
                'focus': 'Training, processi, motivazione'
            },
            'content_strategy': {
                'name': 'Strategia Contenuti',
                'description': 'Consigli per contenuti efficaci',
                'focus': 'Messaggi, format, distribuzione'
            },
            'competitive_analysis': {
                'name': 'Analisi Competitiva',
                'description': 'Insights sui competitor e posizionamento',
                'focus': 'Differenziazione, pricing, messaging'
            }
        }
    
    def get_marketing_advice(self, advice_type: str = 'campaign_optimization', 
                           time_period: int = 30) -> Optional[Dict[str, Any]]:
        """
        Genera consigli marketing basati sui dati storici
        
        Args:
            advice_type: Tipo di consiglio richiesto
            time_period: Periodo di analisi in giorni
            
        Returns:
            Dizionario con i consigli generati
        """
        try:
            # Recupera dati per l'analisi
            analysis_data = self._gather_analysis_data(time_period)
            
            # Prepara dati per l'AI
            ai_data = self._prepare_ai_data(analysis_data, advice_type)
            
            # Genera consigli
            advice_content = self.ai_assistant.generate_response(
                prompt_type='marketing_advice',
                data=ai_data
            )
            
            if not advice_content:
                self.logger.error("❌ Errore generazione consigli AI")
                return None
            
            # Struttura la risposta
            advice_result = {
                'advice_type': advice_type,
                'advice_content': advice_content,
                'generated_at': datetime.now().isoformat(),
                'analysis_period_days': time_period,
                'data_points_analyzed': len(analysis_data),
                'advice_info': self.advice_types.get(advice_type, {}),
                'ai_metadata': {
                    'model_used': 'deepseek-chat',
                    'generation_time': datetime.now().isoformat(),
                    'data_sources': list(analysis_data.keys())
                }
            }
            
            self.logger.info(f"✅ Consigli generati - Tipo: {advice_type}, Periodo: {time_period} giorni")
            return advice_result
            
        except Exception as e:
            self.logger.error(f"❌ Errore generazione consigli: {e}")
            return None
    
    def get_lead_quality_insights(self, time_period: int = 30) -> Optional[Dict[str, Any]]:
        """
        Analizza la qualità dei lead e fornisce insights
        
        Args:
            time_period: Periodo di analisi in giorni
            
        Returns:
            Insights sulla qualità dei lead
        """
        try:
            # Recupera dati lead
            leads_data = self._get_leads_analytics(time_period)
            
            # Analizza pattern e trend
            insights = self._analyze_lead_patterns(leads_data)
            
            # Prepara dati per AI
            ai_data = {
                'leads_data': json.dumps(leads_data, indent=2),
                'campaign_data': json.dumps(insights.get('campaign_performance', {}), indent=2),
                'team_metrics': json.dumps(insights.get('team_metrics', {}), indent=2)
            }
            
            # Genera insights AI
            ai_insights = self.ai_assistant.generate_response(
                prompt_type='marketing_advice',
                data=ai_data
            )
            
            if not ai_insights:
                return None
            
            return {
                'insights_content': ai_insights,
                'raw_data': leads_data,
                'analysis_insights': insights,
                'generated_at': datetime.now().isoformat(),
                'analysis_period_days': time_period
            }
            
        except Exception as e:
            self.logger.error(f"❌ Errore analisi qualità lead: {e}")
            return None
    
    def get_competitive_insights(self, industry: str = None) -> Optional[Dict[str, Any]]:
        """
        Genera insights competitivi per il settore
        
        Args:
            industry: Settore specifico (opzionale)
            
        Returns:
            Insights competitivi
        """
        try:
            # Recupera dati competitivi dal database
            competitive_data = self._gather_competitive_data(industry)
            
            # Prepara dati per AI
            ai_data = {
                'leads_data': json.dumps(competitive_data.get('leads', {}), indent=2),
                'campaign_data': json.dumps(competitive_data.get('campaigns', {}), indent=2),
                'team_metrics': json.dumps(competitive_data.get('team_performance', {}), indent=2),
                'industry': industry or 'Generale'
            }
            
            # Genera insights competitivi
            competitive_insights = self.ai_assistant.generate_response(
                prompt_type='marketing_advice',
                data=ai_data
            )
            
            if not competitive_insights:
                return None
            
            return {
                'competitive_insights': competitive_insights,
                'industry': industry,
                'data_analyzed': competitive_data,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Errore insights competitivi: {e}")
            return None
    
    def get_campaign_recommendations(self, campaign_type: str = 'all') -> Optional[Dict[str, Any]]:
        """
        Genera raccomandazioni per campagne future
        
        Args:
            campaign_type: Tipo di campagna (email, social, ads, all)
            
        Returns:
            Raccomandazioni per campagne
        """
        try:
            # Recupera dati campagne storiche
            campaign_data = self._get_campaign_performance_data()
            
            # Filtra per tipo se specificato
            if campaign_type != 'all':
                campaign_data = {k: v for k, v in campaign_data.items() 
                               if campaign_type.lower() in k.lower()}
            
            # Prepara dati per AI
            ai_data = {
                'leads_data': json.dumps(campaign_data.get('leads_generated', {}), indent=2),
                'campaign_data': json.dumps(campaign_data, indent=2),
                'team_metrics': json.dumps(campaign_data.get('team_performance', {}), indent=2)
            }
            
            # Genera raccomandazioni
            recommendations = self.ai_assistant.generate_response(
                prompt_type='marketing_advice',
                data=ai_data
            )
            
            if not recommendations:
                return None
            
            return {
                'recommendations': recommendations,
                'campaign_type': campaign_type,
                'historical_data': campaign_data,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Errore raccomandazioni campagne: {e}")
            return None
    
    def _gather_analysis_data(self, time_period: int) -> Dict[str, Any]:
        """Raccoglie tutti i dati necessari per l'analisi"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_period)
            
            # Lead analytics
            leads_data = self._get_leads_analytics(time_period)
            
            # Task analytics
            tasks_data = self._get_tasks_analytics(time_period)
            
            # User performance
            users_data = self._get_users_performance(time_period)
            
            # Contact analytics
            contacts_data = self._get_contacts_analytics(time_period)
            
            return {
                'leads': leads_data,
                'tasks': tasks_data,
                'users': users_data,
                'contacts': contacts_data,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': time_period
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Errore raccolta dati analisi: {e}")
            return {}
    
    def _get_leads_analytics(self, time_period: int) -> Dict[str, Any]:
        """Recupera analytics sui lead"""
        try:
            # Query semplificata per Supabase
            query = """
            SELECT 
                state_id,
                category_id,
                source_id,
                budget
            FROM leads
            WHERE created_at >= NOW() - INTERVAL %s DAY
            """
            
            result = self.db_manager.execute_query(query, (time_period,))
            
            # Calcola analytics semplificati
            analytics = {
                'by_status': {},
                'by_category': {},
                'by_source': {},
                'by_industry': {},
                'avg_budget': {}
            }
            
            # Conta manualmente i risultati
            for row in result:
                if row['state_id']:
                    state_key = f"State_{row['state_id']}"
                    analytics['by_status'][state_key] = analytics['by_status'].get(state_key, 0) + 1
                
                if row['category_id']:
                    cat_key = f"Category_{row['category_id']}"
                    analytics['by_category'][cat_key] = analytics['by_category'].get(cat_key, 0) + 1
                
                if row['source_id']:
                    source_key = f"Source_{row['source_id']}"
                    analytics['by_source'][source_key] = analytics['by_source'].get(source_key, 0) + 1
                
                if row['budget']:
                    analytics['avg_budget']['General'] = float(row['budget']) if row['budget'] else 0
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"❌ Errore analytics lead: {e}")
            return {}
    
    def _get_tasks_analytics(self, time_period: int) -> Dict[str, Any]:
        """Recupera analytics sui task"""
        try:
            # Query semplificata per Supabase
            query = """
            SELECT 
                state_id,
                priority_id,
                COUNT(*) as count
            FROM tasks
            WHERE created_at >= NOW() - INTERVAL %s DAY
            GROUP BY state_id, priority_id
            """
            
            result = self.db_manager.execute_query(query, (time_period,))
            
            analytics = {
                'by_status': {},
                'by_priority': {},
                'avg_completion_days': {}
            }
            
            for row in result:
                if row['state_id']:
                    analytics['by_status'][f"State_{row['state_id']}"] = row['count']
                if row['priority_id']:
                    analytics['by_priority'][f"Priority_{row['priority_id']}"] = row['count']
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"❌ Errore analytics task: {e}")
            return {}
    
    def _get_users_performance(self, time_period: int) -> Dict[str, Any]:
        """Recupera performance degli utenti"""
        try:
            # Query semplificata per Supabase
            query = """
            SELECT 
                u.id,
                u.first_name,
                u.last_name,
                u.role_id,
                COUNT(DISTINCT l.id) as leads_assigned,
                COUNT(DISTINCT t.id) as tasks_assigned
            FROM users u
            LEFT JOIN leads l ON u.id = l.assigned_to 
                AND l.created_at >= NOW() - INTERVAL %s DAY
            LEFT JOIN tasks t ON u.id = t.assigned_to 
                AND t.created_at >= NOW() - INTERVAL %s DAY
            GROUP BY u.id, u.first_name, u.last_name, u.role_id
            """
            
            result = self.db_manager.execute_query(query, (time_period, time_period))
            
            analytics = {
                'by_user': {}
            }
            
            for row in result:
                user_name = f"{row['first_name']} {row['last_name']}".strip()
                analytics['by_user'][user_name] = {
                    'role_id': row['role_id'],
                    'leads_assigned': row['leads_assigned'],
                    'tasks_assigned': row['tasks_assigned'],
                    'tasks_completed': 0  # Placeholder
                }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"❌ Errore performance utenti: {e}")
            return {}
    
    def _get_contacts_analytics(self, time_period: int) -> Dict[str, Any]:
        """Recupera analytics sui contatti"""
        try:
            # Query semplificata per Supabase (contact_history potrebbe non esistere)
            query = """
            SELECT 
                'template_1' as template_name,
                COUNT(*) as usage_count,
                0.5 as response_rate
            FROM leads
            WHERE created_at >= NOW() - INTERVAL %s DAY
            LIMIT 1
            """
            
            result = self.db_manager.execute_query(query, (time_period,))
            
            analytics = {
                'by_template': {}
            }
            
            if result:
                analytics['by_template']['Default'] = {
                    'usage_count': result[0]['usage_count'],
                    'response_rate': result[0]['response_rate']
                }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"❌ Errore analytics contatti: {e}")
            return {}
    
    def _prepare_ai_data(self, analysis_data: Dict[str, Any], advice_type: str) -> Dict[str, Any]:
        """Prepara i dati per l'AI in formato ottimale"""
        return {
            'leads_data': json.dumps(analysis_data.get('leads', {}), indent=2),
            'campaign_data': json.dumps(analysis_data.get('tasks', {}), indent=2),
            'team_metrics': json.dumps(analysis_data.get('users', {}), indent=2),
            'advice_type': advice_type,
            'analysis_period': analysis_data.get('period', {}).get('days', 30)
        }
    
    def _analyze_lead_patterns(self, leads_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza pattern nei dati dei lead"""
        try:
            patterns = {
                'top_sources': dict(sorted(leads_data.get('by_source', {}).items(), 
                                        key=lambda x: x[1], reverse=True)[:5]),
                'top_industries': dict(sorted(leads_data.get('by_industry', {}).items(), 
                                            key=lambda x: x[1], reverse=True)[:5]),
                'conversion_by_category': leads_data.get('by_category', {}),
                'budget_insights': leads_data.get('avg_budget', {})
            }
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"❌ Errore analisi pattern: {e}")
            return {}
    
    def _gather_competitive_data(self, industry: str = None) -> Dict[str, Any]:
        """Raccoglie dati per analisi competitiva"""
        # Implementazione semplificata - in futuro si potrebbero integrare dati esterni
        return {
            'leads': self._get_leads_analytics(90),
            'campaigns': self._get_campaign_performance_data(),
            'team_performance': self._get_users_performance(90)
        }
    
    def _get_campaign_performance_data(self) -> Dict[str, Any]:
        """Recupera dati performance campagne"""
        # Implementazione semplificata - basata sui task come proxy per campagne
        return self._get_tasks_analytics(90)
    
    def get_advice_types(self) -> Dict[str, Dict[str, str]]:
        """Restituisce i tipi di consigli disponibili"""
        return self.advice_types
