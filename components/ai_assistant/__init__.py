#!/usr/bin/env python3
"""
AI Assistant Module per DASH_GESTIONE_LEAD
Integrazione con DeepSeek API per assistenza intelligente
Creato da Ezio Camporeale
"""

from .ai_core import AIAssistant
from .sales_script_generator import SalesScriptGenerator
from .marketing_advisor import MarketingAdvisor
from .lead_analyzer import LeadAnalyzer

__all__ = [
    'AIAssistant',
    'SalesScriptGenerator', 
    'MarketingAdvisor',
    'LeadAnalyzer'
]
