#!/usr/bin/env python3
"""
Componente Reports Manager per DASH_GESTIONE_LEAD
Report e analytics avanzate
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import get_current_user
from config import CUSTOM_COLORS

class ReportsManager:
    """Gestisce i report e analytics del sistema"""
    
    def __init__(self):
        """Inizializza il gestore report"""
        self.db = DatabaseManager()
        self.current_user = get_current_user()
    
    def render_reports_page(self):
        """Renderizza la pagina principale dei report"""
        
        st.markdown("## 📊 Report e Analytics")
        st.markdown("Report avanzati e analytics dettagliate")
        
        # Tab per diverse categorie di report
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard Analytics", "📊 Report Lead", "✅ Report Task", "📞 Report Contatti"])
        
        with tab1:
            self.render_dashboard_analytics()
        
        with tab2:
            self.render_lead_reports()
        
        with tab3:
            self.render_task_reports()
        
        with tab4:
            self.render_contact_reports()
    
    def render_dashboard_analytics(self):
        """Renderizza le analytics della dashboard"""
        
        st.markdown("### 📈 Dashboard Analytics")
        
        # Filtri temporali
        col1, col2, col3 = st.columns(3)
        
        with col1:
            period = st.selectbox(
                "📅 Periodo",
                options=["Ultimi 7 giorni", "Ultimi 30 giorni", "Ultimi 90 giorni", "Quest'anno", "Tutti"],
                index=1
            )
        
        with col2:
            group_by = st.selectbox(
                "📊 Raggruppa per",
                options=["Giorno", "Settimana", "Mese"],
                index=0
            )
        
        with col3:
            if st.button("🔄 Aggiorna Report", use_container_width=True):
                st.rerun()
        
        # KPI principali
        self.render_kpi_cards(period)
        
        # Grafici principali
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_lead_conversion_chart(period, group_by)
        
        with col2:
            self.render_task_completion_chart(period, group_by)
        
        # Grafici secondari
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_lead_source_chart(period)
        
        with col2:
            self.render_user_performance_chart(period)
    
    def render_kpi_cards(self, period: str):
        """Renderizza le card KPI"""
        
        # Calcola il periodo
        start_date, end_date = self.get_date_range(period)
        
        # Ottieni i dati
        lead_stats = self.db.get_lead_stats(start_date, end_date)
        task_stats = self.db.get_task_stats(start_date, end_date)
        
        # Card KPI
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👥 Lead Totali",
                value=lead_stats.get('total_leads', 0),
                delta=lead_stats.get('new_leads', 0)
            )
        
        with col2:
            conversion_rate = lead_stats.get('conversion_rate', 0)
            st.metric(
                label="🎯 Tasso Conversione",
                value=f"{conversion_rate:.1f}%",
                delta=f"{conversion_rate - 15:.1f}%" if conversion_rate > 15 else f"{conversion_rate - 15:.1f}%"
            )
        
        with col3:
            st.metric(
                label="✅ Task Completati",
                value=task_stats.get('completed_tasks', 0),
                delta=task_stats.get('completion_rate', 0)
            )
        
        with col4:
            avg_response_time = lead_stats.get('avg_response_time', 0)
            st.metric(
                label="⏱️ Tempo Risposta",
                value=f"{avg_response_time:.1f}h",
                delta=f"{avg_response_time - 24:.1f}h" if avg_response_time < 24 else f"{avg_response_time - 24:.1f}h"
            )
    
    def render_lead_conversion_chart(self, period: str, group_by: str):
        """Renderizza il grafico conversione lead"""
        
        start_date, end_date = self.get_date_range(period)
        
        # Query per dati conversione
        query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as total_leads,
                SUM(CASE WHEN state_id = (SELECT id FROM lead_states WHERE name = 'Chiuso') THEN 1 ELSE 0 END) as converted_leads
            FROM leads 
            WHERE created_at BETWEEN ? AND ?
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        
        data = self.db.execute_query(query, (start_date, end_date))
        
        if data:
            df = pd.DataFrame(data)
            df['conversion_rate'] = (df['converted_leads'] / df['total_leads'] * 100).round(1)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['conversion_rate'],
                mode='lines+markers',
                name='Tasso Conversione',
                line=dict(color=CUSTOM_COLORS['primary'], width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="📈 Tasso Conversione Lead",
                xaxis_title="Data",
                yaxis_title="Tasso Conversione (%)",
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Nessun dato disponibile per il periodo selezionato")
    
    def render_task_completion_chart(self, period: str, group_by: str):
        """Renderizza il grafico completamento task"""
        
        start_date, end_date = self.get_date_range(period)
        
        # Query per dati task
        query = """
            SELECT 
                ts.name as state,
                COUNT(*) as count,
                ts.color
            FROM tasks t
            JOIN task_states ts ON t.state_id = ts.id
            WHERE t.created_at BETWEEN ? AND ?
            GROUP BY ts.id, ts.name, ts.color
            ORDER BY count DESC
        """
        
        data = self.db.execute_query(query, (start_date, end_date))
        
        if data:
            df = pd.DataFrame(data)
            
            fig = px.pie(
                df, 
                values='count', 
                names='state',
                title="✅ Distribuzione Task per Stato"
            )
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Nessun dato disponibile per il periodo selezionato")
    
    def render_lead_source_chart(self, period: str):
        """Renderizza il grafico fonti lead"""
        
        start_date, end_date = self.get_date_range(period)
        
        # Query per fonti lead
        query = """
            SELECT 
                ls.name as source,
                COUNT(*) as count
            FROM leads l
            JOIN lead_sources ls ON l.source_id = ls.id
            WHERE l.created_at BETWEEN ? AND ?
            GROUP BY ls.id, ls.name
            ORDER BY count DESC
        """
        
        data = self.db.execute_query(query, (start_date, end_date))
        
        if data:
            df = pd.DataFrame(data)
            
            fig = px.bar(
                df,
                x='source',
                y='count',
                title="📊 Lead per Fonte",
                color='count',
                color_continuous_scale='viridis'
            )
            
            fig.update_layout(height=300, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Nessun dato disponibile per il periodo selezionato")
    
    def render_user_performance_chart(self, period: str):
        """Renderizza il grafico performance utenti"""
        
        start_date, end_date = self.get_date_range(period)
        
        # Query per performance utenti
        query = """
            SELECT 
                u.username,
                COUNT(l.id) as leads_assigned,
                COUNT(CASE WHEN l.state_id = (SELECT id FROM lead_states WHERE name = 'Chiuso') THEN 1 END) as leads_converted
            FROM users u
            LEFT JOIN leads l ON u.id = l.assigned_to
            WHERE (l.created_at BETWEEN ? AND ?) OR l.created_at IS NULL
            GROUP BY u.id, u.username
            ORDER BY leads_converted DESC
        """
        
        data = self.db.execute_query(query, (start_date, end_date))
        
        if data:
            df = pd.DataFrame(data)
            df['conversion_rate'] = (df['leads_converted'] / df['leads_assigned'] * 100).round(1)
            df = df[df['leads_assigned'] > 0]  # Filtra utenti con lead assegnati
            
            if not df.empty:
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=df['username'],
                    y=df['conversion_rate'],
                    name='Tasso Conversione',
                    marker_color=CUSTOM_COLORS['success']
                ))
                
                fig.update_layout(
                    title="👤 Performance Utenti",
                    xaxis_title="Utente",
                    yaxis_title="Tasso Conversione (%)",
                    height=300,
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 Nessun dato di performance disponibile")
        else:
            st.info("📊 Nessun dato disponibile per il periodo selezionato")
    
    def render_lead_reports(self):
        """Renderizza i report specifici per lead"""
        
        st.markdown("### 👥 Report Lead")
        
        # Filtri
        col1, col2, col3 = st.columns(3)
        
        with col1:
            lead_state = st.selectbox(
                "📋 Stato Lead",
                options=["Tutti"] + [state['name'] for state in self.db.get_lead_states()],
                index=0
            )
        
        with col2:
            lead_source = st.selectbox(
                "📡 Fonte Lead",
                options=["Tutte"] + [source['name'] for source in self.db.get_lead_sources()],
                index=0
            )
        
        with col3:
            assigned_user = st.selectbox(
                "👤 Assegnato a",
                options=["Tutti"] + [user['username'] for user in self.db.get_all_users()],
                index=0
            )
        
        # Report tabella
        self.render_lead_report_table(lead_state, lead_source, assigned_user)
        
        # Export
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("📤 Export Excel", use_container_width=True):
                self.export_lead_report(lead_state, lead_source, assigned_user)
    
    def render_lead_report_table(self, state: str, source: str, user: str):
        """Renderizza la tabella report lead"""
        
        # Costruisci query con filtri
        query = """
            SELECT 
                l.id,
                l.name,
                l.email,
                l.phone,
                l.budget,
                l.expected_close_date,
                ls.name as state,
                lsrc.name as source,
                u.username as assigned_to,
                l.created_at
            FROM leads l
            LEFT JOIN lead_states ls ON l.state_id = ls.id
            LEFT JOIN lead_sources lsrc ON l.source_id = lsrc.id
            LEFT JOIN users u ON l.assigned_to = u.id
            WHERE 1=1
        """
        
        params = []
        
        if state != "Tutti":
            query += " AND ls.name = ?"
            params.append(state)
        
        if source != "Tutte":
            query += " AND lsrc.name = ?"
            params.append(source)
        
        if user != "Tutti":
            query += " AND u.username = ?"
            params.append(user)
        
        query += " ORDER BY l.created_at DESC"
        
        data = self.db.execute_query(query, params)
        
        if data:
            df = pd.DataFrame(data)
            
            # Formatta le colonne
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y')
            df['expected_close_date'] = pd.to_datetime(df['expected_close_date']).dt.strftime('%d/%m/%Y')
            df['budget'] = df['budget'].apply(lambda x: f"€{x:,.0f}" if x else "N/A")
            
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "name": st.column_config.TextColumn("Nome", width="medium"),
                    "email": st.column_config.TextColumn("Email", width="medium"),
                    "phone": st.column_config.TextColumn("Telefono", width="small"),
                    "budget": st.column_config.TextColumn("Budget", width="small"),
                    "expected_close_date": st.column_config.TextColumn("Data Chiusura", width="small"),
                    "state": st.column_config.TextColumn("Stato", width="small"),
                    "source": st.column_config.TextColumn("Fonte", width="small"),
                    "assigned_to": st.column_config.TextColumn("Assegnato", width="small"),
                    "created_at": st.column_config.TextColumn("Creato", width="small")
                }
            )
        else:
            st.info("📊 Nessun lead trovato con i filtri selezionati")
    
    def render_task_reports(self):
        """Renderizza i report specifici per task"""
        
        st.markdown("### ✅ Report Task")
        
        # Filtri
        col1, col2, col3 = st.columns(3)
        
        with col1:
            task_state = st.selectbox(
                "📋 Stato Task",
                options=["Tutti"] + [state['name'] for state in self.db.get_task_states()],
                index=0
            )
        
        with col2:
            task_type = st.selectbox(
                "📝 Tipo Task",
                options=["Tutti"] + [type_['name'] for type_ in self.db.get_task_types()],
                index=0
            )
        
        with col3:
            task_user = st.selectbox(
                "👤 Assegnato a",
                options=["Tutti"] + [user['username'] for user in self.db.get_all_users()],
                index=0
            )
        
        # Report tabella
        self.render_task_report_table(task_state, task_type, task_user)
        
        # Export
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("📤 Export Excel", use_container_width=True):
                self.export_task_report(task_state, task_type, task_user)
    
    def render_task_report_table(self, state: str, type_: str, user: str):
        """Renderizza la tabella report task"""
        
        # Costruisci query con filtri
        query = """
            SELECT 
                t.id,
                t.title,
                t.description,
                ts.name as state,
                tt.name as type,
                u.username as assigned_to,
                t.due_date,
                t.created_at,
                l.name as lead_name
            FROM tasks t
            LEFT JOIN task_states ts ON t.state_id = ts.id
            LEFT JOIN task_types tt ON t.task_type_id = tt.id
            LEFT JOIN users u ON t.assigned_to = u.id
            LEFT JOIN leads l ON t.lead_id = l.id
            WHERE 1=1
        """
        
        params = []
        
        if state != "Tutti":
            query += " AND ts.name = ?"
            params.append(state)
        
        if type_ != "Tutti":
            query += " AND tt.name = ?"
            params.append(type_)
        
        if user != "Tutti":
            query += " AND u.username = ?"
            params.append(user)
        
        query += " ORDER BY t.due_date ASC"
        
        data = self.db.execute_query(query, params)
        
        if data:
            df = pd.DataFrame(data)
            
            # Formatta le colonne
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y')
            df['due_date'] = pd.to_datetime(df['due_date']).dt.strftime('%d/%m/%Y')
            
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "title": st.column_config.TextColumn("Titolo", width="medium"),
                    "description": st.column_config.TextColumn("Descrizione", width="large"),
                    "state": st.column_config.TextColumn("Stato", width="small"),
                    "type": st.column_config.TextColumn("Tipo", width="small"),
                    "assigned_to": st.column_config.TextColumn("Assegnato", width="small"),
                    "due_date": st.column_config.TextColumn("Scadenza", width="small"),
                    "created_at": st.column_config.TextColumn("Creato", width="small"),
                    "lead_name": st.column_config.TextColumn("Lead", width="small")
                }
            )
        else:
            st.info("📊 Nessun task trovato con i filtri selezionati")
    
    def render_contact_reports(self):
        """Renderizza i report specifici per contatti"""
        
        st.markdown("### 📞 Report Contatti")
        
        # Statistiche sequenze
        sequence_stats = self.db.get_sequence_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Sequenze Totali", sequence_stats.get('total_sequences', [{'count': 0}])[0]['count'])
        
        with col2:
            st.metric("🔄 Sequenze Attive", sequence_stats.get('active_sequences', [{'count': 0}])[0]['count'])
        
        with col3:
            st.metric("📧 Contatti Totali", sequence_stats.get('total_contacts', [{'count': 0}])[0]['count'])
        
        with col4:
            success_rate = sequence_stats.get('success_rate', [{'rate': 0}])[0]['rate']
            st.metric("🎯 Tasso Successo", f"{success_rate:.1f}%")
        
        # Grafico sequenze per tipo
        sequences_by_type = sequence_stats.get('sequences_by_type', [])
        
        if sequences_by_type:
            df = pd.DataFrame(sequences_by_type)
            
            fig = px.pie(
                df,
                values='count',
                names='type',
                title="📊 Distribuzione Sequenze per Tipo"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Nessun dato di sequenza disponibile")
    
    def get_date_range(self, period: str) -> Tuple[str, str]:
        """Calcola il range di date per il periodo selezionato"""
        
        end_date = datetime.now()
        
        if period == "Ultimi 7 giorni":
            start_date = end_date - timedelta(days=7)
        elif period == "Ultimi 30 giorni":
            start_date = end_date - timedelta(days=30)
        elif period == "Ultimi 90 giorni":
            start_date = end_date - timedelta(days=90)
        elif period == "Quest'anno":
            start_date = datetime(end_date.year, 1, 1)
        else:  # Tutti
            start_date = datetime(2020, 1, 1)
        
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    def export_lead_report(self, state: str, source: str, user: str):
        """Export report lead in Excel"""
        
        # Query per export
        query = """
            SELECT 
                l.id,
                l.name,
                l.email,
                l.phone,
                l.budget,
                l.expected_close_date,
                ls.name as state,
                lsrc.name as source,
                u.username as assigned_to,
                l.created_at
            FROM leads l
            LEFT JOIN lead_states ls ON l.state_id = ls.id
            LEFT JOIN lead_sources lsrc ON l.source_id = lsrc.id
            LEFT JOIN users u ON l.assigned_to = u.id
            WHERE 1=1
        """
        
        params = []
        
        if state != "Tutti":
            query += " AND ls.name = ?"
            params.append(state)
        
        if source != "Tutte":
            query += " AND lsrc.name = ?"
            params.append(source)
        
        if user != "Tutti":
            query += " AND u.username = ?"
            params.append(user)
        
        query += " ORDER BY l.created_at DESC"
        
        data = self.db.execute_query(query, params)
        
        if data:
            df = pd.DataFrame(data)
            
            # Crea file Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lead_report_{timestamp}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Report Lead', index=False)
            
            # Download file
            with open(filename, 'rb') as f:
                st.download_button(
                    label="📥 Scarica Report Excel",
                    data=f.read(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.success(f"✅ Report esportato: {filename}")
        else:
            st.warning("⚠️ Nessun dato da esportare")
    
    def export_task_report(self, state: str, type_: str, user: str):
        """Export report task in Excel"""
        
        # Query per export
        query = """
            SELECT 
                t.id,
                t.title,
                t.description,
                ts.name as state,
                tt.name as type,
                u.username as assigned_to,
                t.due_date,
                t.created_at,
                l.name as lead_name
            FROM tasks t
            LEFT JOIN task_states ts ON t.state_id = ts.id
            LEFT JOIN task_types tt ON t.task_type_id = tt.id
            LEFT JOIN users u ON t.assigned_to = u.id
            LEFT JOIN leads l ON t.lead_id = l.id
            WHERE 1=1
        """
        
        params = []
        
        if state != "Tutti":
            query += " AND ts.name = ?"
            params.append(state)
        
        if type_ != "Tutti":
            query += " AND tt.name = ?"
            params.append(type_)
        
        if user != "Tutti":
            query += " AND u.username = ?"
            params.append(user)
        
        query += " ORDER BY t.due_date ASC"
        
        data = self.db.execute_query(query, params)
        
        if data:
            df = pd.DataFrame(data)
            
            # Crea file Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"task_report_{timestamp}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Report Task', index=False)
            
            # Download file
            with open(filename, 'rb') as f:
                st.download_button(
                    label="📥 Scarica Report Excel",
                    data=f.read(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.success(f"✅ Report esportato: {filename}")
        else:
            st.warning("⚠️ Nessun dato da esportare")

def render_reports_wrapper():
    """Wrapper per renderizzare i report"""
    reports = ReportsManager()
    reports.render_reports_page()
