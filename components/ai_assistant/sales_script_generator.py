#!/usr/bin/env python3
"""
Sales Script Generator - Generatore Script Vendita AI
Genera script di vendita personalizzati basati sui dati dei lead
Creato da Ezio Camporeale
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import sys

# Aggiungi il percorso della directory principale
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from components.ai_assistant.ai_core import AIAssistant
from database.database_manager import DatabaseManager

class SalesScriptGenerator:
    """
    Generatore di script di vendita personalizzati utilizzando AI
    """
    
    def __init__(self):
        """Inizializza il generatore di script"""
        self.ai_assistant = AIAssistant()
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
        
        # Template per diversi tipi di script
        self.script_templates = {
            'cold_call': {
                'name': 'Cold Call',
                'description': 'Script per chiamate a freddo',
                'focus': 'Apertura forte, presentazione valore, gestione obiezioni'
            },
            'follow_up': {
                'name': 'Follow-up',
                'description': 'Script per chiamate di follow-up',
                'focus': 'Richiamo interesse, avanzamento processo, chiusura'
            },
            'objection_handling': {
                'name': 'Gestione Obiezioni',
                'description': 'Script per gestire obiezioni comuni',
                'focus': 'Empatia, comprensione, soluzioni concrete'
            },
            'closing': {
                'name': 'Chiusura',
                'description': 'Script per chiudere la vendita',
                'focus': 'Urgenza, valore, decisione'
            }
        }
    
    def generate_script(self, lead_id: int, script_type: str = 'cold_call', 
                       custom_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Genera uno script di vendita personalizzato per un lead
        
        Args:
            lead_id: ID del lead per cui generare lo script
            script_type: Tipo di script da generare
            custom_context: Contesto personalizzato aggiuntivo
            
        Returns:
            Dizionario con lo script generato o None in caso di errore
        """
        try:
            # Recupera dati del lead
            lead_data = self._get_lead_data(lead_id)
            if not lead_data:
                self.logger.error(f"❌ Lead {lead_id} non trovato")
                return None
            
            # Prepara i dati per l'AI
            ai_data = self._prepare_ai_data(lead_data, script_type, custom_context)
            
            # Genera lo script
            script_content = self.ai_assistant.generate_response(
                prompt_type='sales_script',
                data=ai_data
            )
            
            if not script_content:
                self.logger.error("❌ Errore generazione script AI")
                return None
            
            # Struttura la risposta
            script_result = {
                'lead_id': lead_id,
                'script_type': script_type,
                'script_content': script_content,
                'generated_at': datetime.now().isoformat(),
                'lead_info': {
                    'name': lead_data.get('first_name', '') + ' ' + lead_data.get('last_name', ''),
                    'company': lead_data.get('company', ''),
                    'industry': lead_data.get('industry', ''),
                    'source': lead_data.get('source', ''),
                    'status': lead_data.get('status', '')
                },
                'template_info': self.script_templates.get(script_type, {}),
                'ai_metadata': {
                    'model_used': 'deepseek-chat',
                    'generation_time': datetime.now().isoformat(),
                    'data_points_used': len(ai_data)
                }
            }
            
            self.logger.info(f"✅ Script generato per lead {lead_id} - Tipo: {script_type}")
            return script_result
            
        except Exception as e:
            self.logger.error(f"❌ Errore generazione script: {e}")
            return None
    
    def generate_bulk_scripts(self, lead_ids: List[int], script_type: str = 'cold_call') -> List[Dict[str, Any]]:
        """
        Genera script per multiple lead
        
        Args:
            lead_ids: Lista di ID lead
            script_type: Tipo di script da generare
            
        Returns:
            Lista di script generati
        """
        scripts = []
        
        for lead_id in lead_ids:
            script = self.generate_script(lead_id, script_type)
            if script:
                scripts.append(script)
        
        self.logger.info(f"✅ Generati {len(scripts)} script su {len(lead_ids)} lead richiesti")
        return scripts
    
    def generate_industry_script(self, industry: str, script_type: str = 'cold_call') -> Optional[Dict[str, Any]]:
        """
        Genera uno script generico per un settore specifico
        
        Args:
            industry: Settore di riferimento
            script_type: Tipo di script
            
        Returns:
            Script generico per il settore
        """
        try:
            # Dati generici per il settore
            industry_data = {
                'lead_data': f"Settore: {industry}",
                'industry': industry,
                'budget': 'Da valutare',
                'source': 'Generico',
                'status': 'Nuovo'
            }
            
            script_content = self.ai_assistant.generate_response(
                prompt_type='sales_script',
                data=industry_data
            )
            
            if not script_content:
                return None
            
            return {
                'industry': industry,
                'script_type': script_type,
                'script_content': script_content,
                'generated_at': datetime.now().isoformat(),
                'is_generic': True,
                'template_info': self.script_templates.get(script_type, {})
            }
            
        except Exception as e:
            self.logger.error(f"❌ Errore generazione script settore: {e}")
            return None
    
    def _get_lead_data(self, lead_id: int) -> Optional[Dict[str, Any]]:
        """Recupera i dati completi di un lead"""
        try:
            # Query per recuperare dati lead
            query = """
            SELECT 
                l.*,
                ls.name as status_name,
                lp.name as priority_name,
                lc.name as category_name,
                u.first_name as assigned_user_first_name,
                u.last_name as assigned_user_last_name
            FROM leads l
            LEFT JOIN lead_states ls ON l.status_id = ls.id
            LEFT JOIN lead_priorities lp ON l.priority_id = lp.id  
            LEFT JOIN lead_categories lc ON l.category_id = lc.id
            LEFT JOIN users u ON l.assigned_user_id = u.id
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
    
    def _prepare_ai_data(self, lead_data: Dict[str, Any], script_type: str, 
                        custom_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prepara i dati per l'AI in formato ottimale"""
        
        # Dati base del lead
        ai_data = {
            'lead_data': f"""
            Nome: {lead_data.get('first_name', '')} {lead_data.get('last_name', '')}
            Azienda: {lead_data.get('company', 'N/A')}
            Email: {lead_data.get('email', 'N/A')}
            Telefono: {lead_data.get('phone', 'N/A')}
            Settore: {lead_data.get('industry', 'N/A')}
            Budget stimato: {lead_data.get('budget', 'N/A')}
            Note: {lead_data.get('notes', 'Nessuna nota')}
            """,
            'industry': lead_data.get('industry', 'Generico'),
            'budget': lead_data.get('budget', 'Non specificato'),
            'source': lead_data.get('source', 'Sconosciuta'),
            'status': lead_data.get('status_name', 'Nuovo'),
            'script_type': script_type,
            'template_focus': self.script_templates.get(script_type, {}).get('focus', '')
        }
        
        # Aggiungi contesto personalizzato se fornito
        if custom_context:
            ai_data.update(custom_context)
        
        return ai_data
    
    def get_script_templates(self) -> Dict[str, Dict[str, str]]:
        """Restituisce i template di script disponibili"""
        return self.script_templates
    
    def analyze_script_effectiveness(self, script_content: str) -> Dict[str, Any]:
        """
        Analizza l'efficacia di uno script (implementazione futura)
        """
        # Implementazione futura per analisi script
        return {
            'analysis': 'Funzionalità in sviluppo',
            'suggestions': [],
            'score': 0
        }
    
    def save_script_to_history(self, script_data: Dict[str, Any]) -> bool:
        """
        Salva uno script nella cronologia (implementazione futura)
        """
        # Implementazione futura per salvataggio cronologia
        return True
    
    def get_script_history(self, lead_id: int = None) -> List[Dict[str, Any]]:
        """
        Recupera la cronologia degli script (implementazione futura)
        """
        # Implementazione futura per cronologia script
        return []
