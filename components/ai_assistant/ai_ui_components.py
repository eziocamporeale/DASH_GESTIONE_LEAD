#!/usr/bin/env python3
"""
AI UI Components - Componenti Interfaccia Assistente AI
Componenti Streamlit per l'interfaccia dell'assistente AI
Creato da Ezio Camporeale
"""

import streamlit as st
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import sys

# Aggiungi il percorso della directory principale
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from components.ai_assistant.ai_core import get_ai_assistant
from components.ai_assistant.sales_script_generator import SalesScriptGenerator
from components.ai_assistant.marketing_advisor import MarketingAdvisor
from components.ai_assistant.lead_analyzer import LeadAnalyzer
from database.database_manager import DatabaseManager
from config import CUSTOM_COLORS

class AIUIComponents:
    """
    Componenti UI per l'interfaccia dell'assistente AI
    """
    
    def __init__(self):
        """Inizializza i componenti UI"""
        self.ai_assistant = get_ai_assistant()
        self.script_generator = SalesScriptGenerator()
        self.marketing_advisor = MarketingAdvisor()
        self.lead_analyzer = LeadAnalyzer()
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
    
    def render_ai_dashboard(self):
        """Renderizza la dashboard principale dell'assistente AI"""
        st.markdown("## 🤖 Assistente AI - Dashboard")
        
        # Test connessione
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Test Connessione AI", use_container_width=True, key="ai_test_connection_main"):
                with st.spinner("Testando connessione DeepSeek..."):
                    if self.ai_assistant.test_connection():
                        st.success("✅ Connessione AI funzionante!")
                    else:
                        st.error("❌ Problema connessione AI")
        
        with col2:
            if st.button("📊 Statistiche Cache", use_container_width=True, key="ai_cache_stats_main"):
                cache_stats = self.ai_assistant.get_cache_stats()
                st.info(f"Cache: {cache_stats['valid_cached']}/{cache_stats['total_cached']} validi")
        
        with col3:
            if st.button("🗑️ Pulisci Cache", use_container_width=True, key="ai_clear_cache_main"):
                self.ai_assistant.clear_cache()
                st.success("Cache pulita!")
        
        st.divider()
        
        # Sezioni principali
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Script Vendita", "💡 Consigli Marketing", "🔍 Analisi Lead", "⚙️ Configurazione"])
        
        with tab1:
            self._render_sales_scripts_tab()
        
        with tab2:
            self._render_marketing_advice_tab()
        
        with tab3:
            self._render_lead_analysis_tab()
        
        with tab4:
            self._render_configuration_tab()
    
    def _render_sales_scripts_tab(self):
        """Renderizza la tab per script di vendita"""
        st.markdown("### 📝 Generatore Script di Vendita")
        
        # Selezione lead
        leads = self._get_leads_for_selection()
        
        # Debug info
        st.info(f"🔍 Debug: Trovati {len(leads)} lead nel database")
        
        if not leads:
            st.warning("⚠️ Nessun lead disponibile per la generazione script")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_lead_id = st.selectbox(
                "Seleziona Lead:",
                options=[lead['id'] for lead in leads],
                format_func=lambda x: f"{next(lead['name'] for lead in leads if lead['id'] == x)} - {next(lead['company'] for lead in leads if lead['id'] == x)}"
            )
        
        with col2:
            script_type = st.selectbox(
                "Tipo Script:",
                options=list(self.script_generator.get_script_templates().keys()),
                format_func=lambda x: self.script_generator.get_script_templates()[x]['name']
            )
        
        # Contesto personalizzato
        st.markdown("#### 🎯 Contesto Personalizzato (Opzionale)")
        custom_context = st.text_area(
            "Aggiungi informazioni aggiuntive per personalizzare lo script:",
            placeholder="Es: Il lead ha mostrato interesse per la soluzione X, budget confermato di €5000..."
        )
        
        # Pulsante generazione
        if st.button("🚀 Genera Script", use_container_width=True, type="primary", key="ai_generate_script"):
            if selected_lead_id:
                with st.spinner("🤖 Generando script personalizzato..."):
                    # Prepara contesto personalizzato
                    context_data = {}
                    if custom_context:
                        context_data['custom_context'] = custom_context
                    
                    # Genera script
                    script_result = self.script_generator.generate_script(
                        selected_lead_id, 
                        script_type, 
                        context_data
                    )
                    
                    if script_result:
                        self._display_script_result(script_result)
                    else:
                        st.error("❌ Errore nella generazione dello script")
            else:
                st.warning("⚠️ Seleziona un lead per generare lo script")
        
        # Script per settore
        st.divider()
        st.markdown("#### 🏭 Script Generico per Settore")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            industry = st.text_input("Settore:", placeholder="Es: Tecnologia, Finanza, Healthcare...")
        
        with col2:
            industry_script_type = st.selectbox(
                "Tipo Script:",
                options=list(self.script_generator.get_script_templates().keys()),
                format_func=lambda x: self.script_generator.get_script_templates()[x]['name'],
                key="industry_script_type"
            )
        
        if st.button("🏭 Genera Script Settore", use_container_width=True, key="ai_generate_industry_script"):
            if industry:
                with st.spinner("🤖 Generando script per settore..."):
                    industry_script = self.script_generator.generate_industry_script(
                        industry, 
                        industry_script_type
                    )
                    
                    if industry_script:
                        self._display_industry_script_result(industry_script)
                    else:
                        st.error("❌ Errore nella generazione dello script per settore")
            else:
                st.warning("⚠️ Inserisci un settore")
    
    def _render_marketing_advice_tab(self):
        """Renderizza la tab per consigli marketing"""
        st.markdown("### 💡 Consigli Marketing Intelligenti")
        
        # Selezione tipo consiglio
        advice_types = self.marketing_advisor.get_advice_types()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_advice_type = st.selectbox(
                "Tipo di Consiglio:",
                options=list(advice_types.keys()),
                format_func=lambda x: advice_types[x]['name']
            )
        
        with col2:
            time_period = st.selectbox(
                "Periodo Analisi:",
                options=[7, 14, 30, 60, 90],
                format_func=lambda x: f"{x} giorni"
            )
        
        # Descrizione tipo consiglio
        if selected_advice_type in advice_types:
            st.info(f"**{advice_types[selected_advice_type]['name']}**: {advice_types[selected_advice_type]['description']}")
        
        # Pulsante generazione consigli
        if st.button("💡 Genera Consigli Marketing", use_container_width=True, type="primary", key="ai_generate_marketing_advice"):
            with st.spinner("🤖 Analizzando dati e generando consigli..."):
                advice_result = self.marketing_advisor.get_marketing_advice(
                    selected_advice_type, 
                    time_period
                )
                
                if advice_result:
                    self._display_marketing_advice_result(advice_result)
                else:
                    st.error("❌ Errore nella generazione dei consigli")
        
        st.divider()
        
        # Analisi qualità lead
        st.markdown("#### 📊 Analisi Qualità Lead")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            lead_analysis_period = st.selectbox(
                "Periodo Analisi Lead:",
                options=[7, 14, 30, 60, 90],
                format_func=lambda x: f"{x} giorni",
                key="lead_analysis_period"
            )
        
        with col2:
            if st.button("📊 Analizza Qualità Lead", use_container_width=True, key="ai_analyze_lead_quality"):
                with st.spinner("🤖 Analizzando qualità lead..."):
                    lead_insights = self.marketing_advisor.get_lead_quality_insights(
                        lead_analysis_period
                    )
                    
                    if lead_insights:
                        self._display_lead_quality_insights(lead_insights)
                    else:
                        st.error("❌ Errore nell'analisi qualità lead")
        
        # Insights competitivi
        st.markdown("#### 🏆 Insights Competitivi")
        
        industry = st.text_input("Settore per Analisi Competitiva:", placeholder="Es: Tecnologia, Finanza...")
        
        if st.button("🏆 Genera Insights Competitivi", use_container_width=True, key="ai_generate_competitive_insights"):
            with st.spinner("🤖 Analizzando competitività..."):
                competitive_insights = self.marketing_advisor.get_competitive_insights(industry)
                
                if competitive_insights:
                    self._display_competitive_insights(competitive_insights)
                else:
                    st.error("❌ Errore nell'analisi competitiva")
    
    def _render_lead_analysis_tab(self):
        """Renderizza la tab per analisi lead"""
        st.markdown("### 🔍 Analisi Lead Intelligente")
        
        # Selezione lead per analisi
        leads = self._get_leads_for_selection()
        
        if not leads:
            st.warning("⚠️ Nessun lead disponibile per l'analisi")
            return
        
        # Analisi singolo lead - Layout ottimizzato
        st.markdown("#### 👤 Analisi Singolo Lead")
        
        # Selezione lead in una riga compatta
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            selected_lead_id = st.selectbox(
                "Seleziona Lead per Analisi:",
                options=[lead['id'] for lead in leads],
                format_func=lambda x: f"{next(lead['name'] for lead in leads if lead['id'] == x)} - {next(lead['company'] for lead in leads if lead['id'] == x)}",
                key="analysis_lead_select"
            )
        
        with col2:
            if st.button("🔍 Analizza Lead", use_container_width=True, type="primary", key="ai_analyze_single_lead"):
                with st.spinner("🤖 Analizzando lead..."):
                    analysis_result = self.lead_analyzer.analyze_lead(selected_lead_id)
                    
                    if analysis_result:
                        # Container a larghezza piena per l'analisi
                        with st.container():
                            self._display_lead_analysis_result(analysis_result)
                    else:
                        st.error("❌ Errore nell'analisi del lead")
        
        with col3:
            if st.button("🔄 Ricarica", use_container_width=True, key="reload_analysis_btn"):
                st.rerun()
        
        st.divider()
        
        # Analisi multipla lead
        st.markdown("#### 👥 Analisi Multipla Lead")
        
        selected_lead_ids = st.multiselect(
            "Seleziona Lead per Confronto:",
            options=[lead['id'] for lead in leads],
            format_func=lambda x: f"{next(lead['name'] for lead in leads if lead['id'] == x)} - {next(lead['company'] for lead in leads if lead['id'] == x)}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Confronta Lead", use_container_width=True, key="ai_compare_leads"):
                if len(selected_lead_ids) >= 2:
                    with st.spinner("🤖 Confrontando lead..."):
                        comparison_result = self.lead_analyzer.get_lead_comparison(selected_lead_ids)
                        
                        if comparison_result:
                            self._display_lead_comparison_result(comparison_result)
                        else:
                            st.error("❌ Errore nel confronto dei lead")
                else:
                    st.warning("⚠️ Seleziona almeno 2 lead per il confronto")
        
        with col2:
            if st.button("📈 Analisi Trend Lead", use_container_width=True, key="ai_analyze_lead_trend"):
                if selected_lead_ids:
                    lead_id = selected_lead_ids[0]  # Prendi il primo
                    with st.spinner("🤖 Analizzando trend..."):
                        trend_result = self.lead_analyzer.get_lead_trend_analysis(lead_id, 30)
                        
                        if trend_result:
                            self._display_lead_trend_result(trend_result)
                        else:
                            st.error("❌ Errore nell'analisi trend")
                else:
                    st.warning("⚠️ Seleziona un lead per l'analisi trend")
    
    def _render_configuration_tab(self):
        """Renderizza la tab di configurazione"""
        st.markdown("### ⚙️ Configurazione Assistente AI")
        
        # Informazioni connessione
        st.markdown("#### 🔗 Stato Connessione")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("API Model", "DeepSeek Chat")
        
        with col2:
            st.metric("Max Tokens", "2000")
        
        with col3:
            st.metric("Temperature", "0.7")
        
        # Test connessione dettagliato
        if st.button("🔍 Test Connessione Dettagliato", use_container_width=True, key="ai_test_connection_detailed"):
            with st.spinner("Testando connessione..."):
                if self.ai_assistant.test_connection():
                    st.success("✅ Connessione DeepSeek API funzionante!")
                else:
                    st.error("❌ Problema connessione DeepSeek API")
        
        # Statistiche cache
        st.markdown("#### 📊 Statistiche Cache")
        
        cache_stats = self.ai_assistant.get_cache_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Risposte in Cache", cache_stats['total_cached'])
        
        with col2:
            st.metric("Cache Valide", cache_stats['valid_cached'])
        
        with col3:
            st.metric("Hit Rate", f"{cache_stats['cache_hit_rate']:.1f}%")
        
        # Gestione cache
        st.markdown("#### 🗑️ Gestione Cache")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Pulisci Cache", use_container_width=True, key="ai_clear_cache_config"):
                self.ai_assistant.clear_cache()
                st.success("Cache pulita!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Ricarica Statistiche", use_container_width=True, key="ai_reload_stats"):
                st.rerun()
        
        # Informazioni sistema
        st.markdown("#### ℹ️ Informazioni Sistema")
        
        info_data = {
            "Versione AI Assistant": "1.0.0",
            "Ultimo Aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Cache Abilitata": "Sì" if cache_stats['cache_enabled'] else "No",
            "Timeout API": "30 secondi",
            "Tentativi Retry": "3"
        }
        
        for key, value in info_data.items():
            st.text(f"{key}: {value}")
    
    def _get_leads_for_selection(self) -> List[Dict[str, Any]]:
        """Recupera lead per la selezione"""
        try:
            # Query semplificata per Supabase
            query = """
            SELECT 
                id,
                name,
                company,
                email,
                phone,
                budget,
                state_id,
                source_id,
                notes
            FROM leads
            ORDER BY created_at DESC
            LIMIT 50
            """
            
            result = self.db_manager.execute_query(query)
            
            # Debug: mostra quanti risultati dalla query
            self.logger.info(f"🔍 Query result: {len(result) if result else 0} rows")
            
            # Formatta i dati per la selezione
            leads = []
            if result:
                for row in result:
                    leads.append({
                        'id': row['id'],
                        'name': row['name'] or 'N/A',
                        'company': row['company'] or 'N/A',
                        'email': row['email'] or 'N/A',
                        'phone': row['phone'] or 'N/A',
                        'budget': row['budget'] or 'N/A',
                        'state_id': row['state_id'],
                        'source_id': row['source_id'],
                        'notes': row['notes'] or ''
                    })
            
            self.logger.info(f"🔍 Formatted leads: {len(leads)}")
            return leads
            
        except Exception as e:
            self.logger.error(f"❌ Errore recupero lead: {e}")
            return []
    
    def _display_script_result(self, script_result: Dict[str, Any]):
        """Visualizza il risultato dello script generato"""
        st.markdown("### 📝 Script Generato")
        
        # Informazioni lead
        lead_info = script_result['lead_info']
        st.markdown(f"**Lead:** {lead_info['name']} - {lead_info['company']}")
        st.markdown(f"**Settore:** {lead_info['industry']} | **Fonte:** {lead_info['source']}")
        
        # Script content
        st.markdown("#### 📋 Script:")
        st.markdown(script_result['script_content'])
        
        # Metadati
        with st.expander("📊 Dettagli Generazione"):
            st.json(script_result['ai_metadata'])
    
    def _display_industry_script_result(self, script_result: Dict[str, Any]):
        """Visualizza il risultato dello script per settore"""
        st.markdown("### 🏭 Script per Settore")
        
        st.markdown(f"**Settore:** {script_result['industry']}")
        st.markdown(f"**Tipo:** {script_result['template_info']['name']}")
        
        st.markdown("#### 📋 Script:")
        st.markdown(script_result['script_content'])
    
    def _display_marketing_advice_result(self, advice_result: Dict[str, Any]):
        """Visualizza il risultato dei consigli marketing"""
        st.markdown("### 💡 Consigli Marketing")
        
        advice_info = advice_result['advice_info']
        st.markdown(f"**Tipo:** {advice_info['name']}")
        st.markdown(f"**Periodo Analisi:** {advice_result['analysis_period_days']} giorni")
        
        st.markdown("#### 📋 Consigli:")
        st.markdown(advice_result['advice_content'])
        
        # Statistiche
        with st.expander("📊 Statistiche Analisi"):
            st.metric("Punti Dati Analizzati", advice_result['data_points_analyzed'])
            st.metric("Fonti Dati", len(advice_result['ai_metadata']['data_sources']))
    
    def _display_lead_quality_insights(self, insights_result: Dict[str, Any]):
        """Visualizza gli insights sulla qualità lead"""
        st.markdown("### 📊 Insights Qualità Lead")
        
        st.markdown(f"**Periodo Analisi:** {insights_result['analysis_period_days']} giorni")
        
        st.markdown("#### 📋 Insights:")
        st.markdown(insights_result['insights_content'])
        
        # Dati grezzi
        with st.expander("📊 Dati Analisi"):
            st.json(insights_result['raw_data'])
    
    def _display_competitive_insights(self, insights_result: Dict[str, Any]):
        """Visualizza gli insights competitivi"""
        st.markdown("### 🏆 Insights Competitivi")
        
        st.markdown(f"**Settore:** {insights_result['industry'] or 'Generale'}")
        
        st.markdown("#### 📋 Analisi Competitiva:")
        st.markdown(insights_result['competitive_insights'])
    
    def _display_lead_analysis_result(self, analysis_result: Dict[str, Any]):
        """Visualizza il risultato dell'analisi lead"""
        st.markdown("### 🔍 Analisi Lead")
        
        lead_info = analysis_result['lead_info']
        st.markdown(f"**Lead:** {lead_info['name']} - {lead_info['company']}")
        
        # Score e categoria - Layout più compatto
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            st.metric("Quality Score", f"{analysis_result['quality_score']}/100")
        
        with col2:
            st.metric("Categoria", analysis_result['quality_category'])
        
        with col3:
            st.metric("Stato", lead_info['status'])
        
        # Separatore
        st.divider()
        
        # Analisi AI - Layout a larghezza piena
        st.markdown("#### 🤖 Analisi AI:")
        
        # Container per l'analisi con larghezza massima
        with st.container():
            st.markdown(analysis_result['analysis_content'])
        
        # Separatore
        st.divider()
        
        # Raccomandazioni - Layout migliorato
        if analysis_result['recommendations']:
            st.markdown("#### 💡 Raccomandazioni:")
            for i, rec in enumerate(analysis_result['recommendations'], 1):
                st.markdown(f"**{i}.** {rec}")
        
        # Dettagli - Layout più ordinato
        with st.expander("📊 Dettagli Analisi Completa"):
            tab1, tab2, tab3 = st.tabs(["Score Breakdown", "Storico Contatti", "Attività Recenti"])
            
            with tab1:
                st.json(analysis_result['score_breakdown'])
            
            with tab2:
                if analysis_result['contact_history']:
                    st.json(analysis_result['contact_history'])
                else:
                    st.info("Nessun contatto registrato")
            
            with tab3:
                if analysis_result['recent_activities']:
                    st.json(analysis_result['recent_activities'])
                else:
                    st.info("Nessuna attività recente")
    
    def _display_lead_comparison_result(self, comparison_result: Dict[str, Any]):
        """Visualizza il risultato del confronto lead"""
        st.markdown("### 📊 Confronto Lead")
        
        st.markdown(f"**Lead Confrontati:** {comparison_result['leads_compared']}")
        
        # Analisi comparativa
        st.markdown("#### 🤖 Analisi Comparativa:")
        st.markdown(comparison_result['comparison_analysis'])
        
        # Dettagli confronto
        with st.expander("📊 Dettagli Confronto"):
            st.json(comparison_result['comparison_data'])
    
    def _display_lead_trend_result(self, trend_result: Dict[str, Any]):
        """Visualizza il risultato dell'analisi trend"""
        st.markdown("### 📈 Analisi Trend Lead")
        
        st.markdown(f"**Periodo Analisi:** {trend_result['analysis_period_days']} giorni")
        
        # Analisi trend
        st.markdown("#### 🤖 Analisi Trend:")
        st.markdown(trend_result['trend_analysis'])
        
        # Dati storici
        with st.expander("📊 Dati Storici"):
            st.json(trend_result['history_data'])

# Funzione principale per renderizzare l'assistente AI
def render_ai_assistant():
    """Funzione principale per renderizzare l'assistente AI"""
    ai_ui = AIUIComponents()
    ai_ui.render_ai_dashboard()
