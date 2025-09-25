#!/usr/bin/env python3
"""
Database Manager per DASH_GESTIONE_LEAD
Gestione connessione e operazioni database
Creato da Ezio Camporeale
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import sys

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

from config import DATABASE_PATH, USE_SUPABASE, SUPABASE_URL, SUPABASE_KEY

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestore database per l'applicazione"""
    
    def __init__(self):
        """Inizializza il gestore database"""
        self.db_path = DATABASE_PATH
        self.use_supabase = USE_SUPABASE
        
        if self.use_supabase:
            try:
                from supabase import create_client, Client
                self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
                logger.info("✅ Connessione Supabase inizializzata")
            except ImportError:
                logger.error("❌ Libreria supabase non installata")
                self.use_supabase = False
            except Exception as e:
                logger.error(f"❌ Errore connessione Supabase: {e}")
                self.use_supabase = False
        
        if not self.use_supabase:
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Inizializza SQLite"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info("✅ Connessione SQLite inizializzata")
        except Exception as e:
            logger.error(f"❌ Errore connessione SQLite: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Esegue una query di selezione"""
        if self.use_supabase:
            return self._execute_supabase_query(query, params)
        else:
            return self._execute_sqlite_query(query, params)
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Esegue una query di aggiornamento/inserimento"""
        if self.use_supabase:
            return self._execute_supabase_update(query, params)
        else:
            return self._execute_sqlite_update(query, params)
    
    def _execute_sqlite_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Esegue query SQLite"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"❌ Errore query SQLite: {e}")
            raise
    
    def _execute_sqlite_update(self, query: str, params: tuple = ()) -> int:
        """Esegue update SQLite"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ Errore update SQLite: {e}")
            self.conn.rollback()
            raise
    
    def _execute_supabase_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Esegue query Supabase (semplificata)"""
        try:
            # Per ora, implementazione semplificata
            # In futuro, parser SQL più sofisticato
            if "SELECT" in query.upper():
                table_name = self._extract_table_name(query)
                if table_name:
                    result = self.supabase.table(table_name).select('*').execute()
                    return result.data
            return []
        except Exception as e:
            logger.error(f"❌ Errore query Supabase: {e}")
            raise
    
    def _execute_supabase_update(self, query: str, params: tuple = ()) -> int:
        """Esegue update Supabase (semplificata)"""
        try:
            # Per ora, implementazione semplificata
            # In futuro, parser SQL più sofisticato
            if "INSERT" in query.upper():
                table_name = self._extract_table_name(query)
                if table_name:
                    # Estrai dati dai parametri (semplificato)
                    data = self._extract_data_from_params(params)
                    result = self.supabase.table(table_name).insert(data).execute()
                    return len(result.data) if result.data else 0
            return 0
        except Exception as e:
            logger.error(f"❌ Errore update Supabase: {e}")
            raise
    
    def _extract_table_name(self, query: str) -> Optional[str]:
        """Estrae il nome della tabella dalla query (semplificato)"""
        query_upper = query.upper()
        if "FROM" in query_upper:
            parts = query_upper.split("FROM")
            if len(parts) > 1:
                table_part = parts[1].strip().split()[0]
                return table_part.lower()
        elif "INSERT INTO" in query_upper:
            parts = query_upper.split("INSERT INTO")
            if len(parts) > 1:
                table_part = parts[1].strip().split()[0]
                return table_part.lower()
        return None
    
    def _extract_data_from_params(self, params: tuple) -> Dict:
        """Estrae dati dai parametri (semplificato)"""
        # Implementazione semplificata - in futuro più sofisticata
        return {}
    
    # ==================== METODI LEAD ====================
    
    def get_all_leads(self) -> List[Dict]:
        """Ottiene tutti i lead"""
        if self.use_supabase:
            try:
                # Ottieni tutti i lead con limite alto per evitare il limite Supabase di 1000
                result = self.supabase.table('leads').select('*').order('created_at', desc=True).limit(10000).execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_all_leads Supabase: {e}")
                return []
        else:
            query = """
                SELECT l.*, 
                       ls.name as state_name,
                       lp.name as priority_name,
                       lc.name as category_name,
                       ls2.name as source_name,
                       u.first_name || ' ' || u.last_name as assigned_to_name
                FROM leads l
                LEFT JOIN lead_states ls ON l.state_id = ls.id
                LEFT JOIN lead_priorities lp ON l.priority_id = lp.id
                LEFT JOIN lead_categories lc ON l.category_id = lc.id
                LEFT JOIN lead_sources ls2 ON l.source_id = ls2.id
                LEFT JOIN users u ON l.assigned_to = u.id
                ORDER BY l.created_at DESC
            """
            return self.execute_query(query)
    
    def get_leads(self, filters: Dict = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Ottiene i lead con filtri opzionali"""
        if self.use_supabase:
            try:
                # Query semplice senza rename (gestiamo i nomi dopo)
                query = self.supabase.table('leads').select('*')
                
                # Applica filtri se forniti
                if filters:
                    if filters.get('state_id'):
                        query = query.eq('state_id', filters['state_id'])
                    if filters.get('category_id'):
                        query = query.eq('category_id', filters['category_id'])
                    if filters.get('assigned_to'):
                        query = query.eq('assigned_to', filters['assigned_to'])
                    if filters.get('group_id'):
                        query = query.eq('group_id', filters['group_id'])
                    if filters.get('search'):
                        search_term = filters['search']
                        # Ricerca in più campi
                        query = query.or_(f"name.ilike.%{search_term}%,email.ilike.%{search_term}%,company.ilike.%{search_term}%")
                
                # Ordina e limita
                result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
                leads = result.data
                
                # Ottieni tutti i dati di lookup in una volta sola
                if leads:
                    # Ottieni tutti gli stati
                    state_ids = list(set([lead.get('state_id') for lead in leads if lead.get('state_id')]))
                    states = {}
                    if state_ids:
                        state_result = self.supabase.table('lead_states').select('id,name').in_('id', state_ids).execute()
                        states = {state['id']: state['name'] for state in state_result.data}
                    
                    # Ottieni tutte le priorità
                    priority_ids = list(set([lead.get('priority_id') for lead in leads if lead.get('priority_id')]))
                    priorities = {}
                    if priority_ids:
                        priority_result = self.supabase.table('lead_priorities').select('id,name').in_('id', priority_ids).execute()
                        priorities = {p['id']: p['name'] for p in priority_result.data}
                    
                    # Ottieni tutte le categorie
                    category_ids = list(set([lead.get('category_id') for lead in leads if lead.get('category_id')]))
                    categories = {}
                    if category_ids:
                        category_result = self.supabase.table('lead_categories').select('id,name').in_('id', category_ids).execute()
                        categories = {c['id']: c['name'] for c in category_result.data}
                    
                    # Ottieni tutte le fonti
                    source_ids = list(set([lead.get('source_id') for lead in leads if lead.get('source_id')]))
                    sources = {}
                    if source_ids:
                        source_result = self.supabase.table('lead_sources').select('id,name').in_('id', source_ids).execute()
                        sources = {s['id']: s['name'] for s in source_result.data}
                    
                    # Ottieni tutti gli utenti assegnati
                    user_ids = list(set([lead.get('assigned_to') for lead in leads if lead.get('assigned_to')]))
                    users = {}
                    if user_ids:
                        user_result = self.supabase.table('users').select('id,first_name,last_name').in_('id', user_ids).execute()
                        users = {u['id']: {'first_name': u.get('first_name', ''), 'last_name': u.get('last_name', '')} for u in user_result.data}
                    
                    # Aggiungi i nomi ai lead
                    for lead in leads:
                        lead['state_name'] = states.get(lead.get('state_id'), 'N/A')
                        lead['priority_name'] = priorities.get(lead.get('priority_id'), 'N/A')
                        lead['category_name'] = categories.get(lead.get('category_id'), 'N/A')
                        lead['source_name'] = sources.get(lead.get('source_id'), 'N/A')
                        
                        if lead.get('assigned_to') and lead['assigned_to'] in users:
                            user = users[lead['assigned_to']]
                            lead['assigned_first_name'] = user['first_name']
                            lead['assigned_last_name'] = user['last_name']
                        else:
                            lead['assigned_first_name'] = ''
                            lead['assigned_last_name'] = ''
                        
                        # Mappa name in first_name e last_name per compatibilità
                        if 'name' in lead and lead['name']:
                            name_parts = lead['name'].split(' ', 1)
                            lead['first_name'] = name_parts[0] if name_parts else ''
                            lead['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
                        else:
                            lead['first_name'] = ''
                            lead['last_name'] = ''
                
                return leads
            except Exception as e:
                logger.error(f"❌ Errore get_leads Supabase: {e}")
                return []
        else:
            # SQLite non supportato per produzione - solo per backup
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return []
    
    def get_lead(self, lead_id: int) -> Optional[Dict]:
        """Ottiene un singolo lead per ID"""
        if self.use_supabase:
            try:
                result = self.supabase.table('leads').select('*').eq('id', lead_id).execute()
                if result.data:
                    lead = result.data[0]
                    
                    # Ottieni i dati di lookup
                    if lead.get('state_id'):
                        state_result = self.supabase.table('lead_states').select('id,name').eq('id', lead['state_id']).execute()
                        if state_result.data:
                            lead['state_name'] = state_result.data[0]['name']
                        else:
                            lead['state_name'] = 'N/A'
                    
                    if lead.get('priority_id'):
                        priority_result = self.supabase.table('lead_priorities').select('id,name').eq('id', lead['priority_id']).execute()
                        if priority_result.data:
                            lead['priority_name'] = priority_result.data[0]['name']
                        else:
                            lead['priority_name'] = 'N/A'
                    
                    if lead.get('category_id'):
                        category_result = self.supabase.table('lead_categories').select('id,name').eq('id', lead['category_id']).execute()
                        if category_result.data:
                            lead['category_name'] = category_result.data[0]['name']
                        else:
                            lead['category_name'] = 'N/A'
                    
                    if lead.get('source_id'):
                        source_result = self.supabase.table('lead_sources').select('id,name').eq('id', lead['source_id']).execute()
                        if source_result.data:
                            lead['source_name'] = source_result.data[0]['name']
                        else:
                            lead['source_name'] = 'N/A'
                    
                    if lead.get('assigned_to'):
                        user_result = self.supabase.table('users').select('id,first_name,last_name').eq('id', lead['assigned_to']).execute()
                        if user_result.data:
                            user = user_result.data[0]
                            lead['assigned_first_name'] = user.get('first_name', '')
                            lead['assigned_last_name'] = user.get('last_name', '')
                        else:
                            lead['assigned_first_name'] = ''
                            lead['assigned_last_name'] = ''
                    else:
                        lead['assigned_first_name'] = ''
                        lead['assigned_last_name'] = ''
                    
                    # Mappa name in first_name e last_name per compatibilità
                    if 'name' in lead and lead['name']:
                        name_parts = lead['name'].split(' ', 1)
                        lead['first_name'] = name_parts[0] if name_parts else ''
                        lead['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
                    else:
                        lead['first_name'] = ''
                        lead['last_name'] = ''
                    
                    return lead
                return None
            except Exception as e:
                logger.error(f"❌ Errore get_lead Supabase: {e}")
                return None
        else:
            # SQLite implementation
            query = """
                SELECT l.*, 
                       ls.name as state_name,
                       lp.name as priority_name,
                       lc.name as category_name,
                       ls2.name as source_name,
                       u.first_name as assigned_first_name,
                       u.last_name as assigned_last_name
                FROM leads l
                LEFT JOIN lead_states ls ON l.state_id = ls.id
                LEFT JOIN lead_priorities lp ON l.priority_id = lp.id
                LEFT JOIN lead_categories lc ON l.category_id = lc.id
                LEFT JOIN lead_sources ls2 ON l.source_id = ls2.id
                LEFT JOIN users u ON l.assigned_to = u.id
                WHERE l.id = ?
            """
            result = self.execute_query(query, (lead_id,))
            if result:
                return result[0]
            return None
    
    def filter_sensitive_data_for_tester(self, data: List[Dict], data_type: str = 'lead') -> List[Dict]:
        """Filtra i dati sensibili per il ruolo Tester"""
        filtered_data = []
        
        for item in data:
            # Crea una copia dell'item
            filtered_item = item.copy()
            
            # Maschera i dati sensibili comuni
            self._mask_sensitive_fields(filtered_item)
            
            # Maschera dati specifici per tipo
            if data_type == 'lead':
                self._mask_lead_specific_data(filtered_item)
            elif data_type == 'user':
                self._mask_user_specific_data(filtered_item)
            elif data_type == 'contact':
                self._mask_contact_specific_data(filtered_item)
            
            # Mantieni solo i dati non sensibili
            filtered_data.append(filtered_item)
        
        return filtered_data
    
    def _mask_sensitive_fields(self, item: Dict):
        """Maschera i campi sensibili comuni"""
        # Maschera nomi (first_name, last_name, name)
        for field in ['first_name', 'last_name', 'name']:
            if field in item and item[field]:
                if field == 'name':
                    # Per il campo name completo
                    name_parts = str(item[field]).split(' ', 1)
                    if len(name_parts) >= 2:
                        item[field] = f"{name_parts[0][0]}. {name_parts[1][0]}."
                    else:
                        item[field] = f"{name_parts[0][0]}."
                else:
                    # Per first_name e last_name separati
                    name = str(item[field])
                    if len(name) > 0:
                        item[field] = f"{name[0]}."
        
        # Maschera email mantenendo solo dominio
        if 'email' in item and item['email']:
            email_parts = str(item['email']).split('@')
            if len(email_parts) == 2:
                item['email'] = f"***@{email_parts[1]}"
            else:
                item['email'] = "***@***"
        
        # Maschera telefono mantenendo solo ultime 3 cifre
        if 'phone' in item and item['phone']:
            phone = str(item['phone'])
            if len(phone) > 3:
                item['phone'] = f"***{phone[-3:]}"
            else:
                item['phone'] = "***"
        
        # Maschera azienda mantenendo solo prime 3 lettere
        if 'company' in item and item['company']:
            company = str(item['company'])
            if len(company) > 3:
                item['company'] = f"{company[:3]}***"
            else:
                item['company'] = "***"
    
    def _mask_lead_specific_data(self, item: Dict):
        """Maschera dati specifici dei lead"""
        # Maschera note se contengono informazioni sensibili
        if 'notes' in item and item['notes']:
            item['notes'] = "*** Dati sensibili nascosti ***"
        
        # Maschera posizione lavorativa
        if 'position' in item and item['position']:
            position = str(item['position'])
            if len(position) > 3:
                item['position'] = f"{position[:3]}***"
            else:
                item['position'] = "***"
    
    def _mask_user_specific_data(self, item: Dict):
        """Maschera dati specifici degli utenti"""
        # Maschera username mantenendo solo prime 2 lettere
        if 'username' in item and item['username']:
            username = str(item['username'])
            if len(username) > 2:
                item['username'] = f"{username[:2]}***"
            else:
                item['username'] = "***"
        
        # Maschera note utente
        if 'notes' in item and item['notes']:
            item['notes'] = "*** Dati sensibili nascosti ***"
    
    def _mask_contact_specific_data(self, item: Dict):
        """Maschera dati specifici dei contatti"""
        # Maschera note contatto
        if 'notes' in item and item['notes']:
            item['notes'] = "*** Dati sensibili nascosti ***"
    
    def create_lead(self, lead_data: Dict) -> bool:
        """Crea un nuovo lead"""
        if self.use_supabase:
            try:
                # Mappa i dati per la struttura corretta di Supabase
                supabase_data = {
                    'name': f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}".strip(),
                    'email': lead_data.get('email') or None,
                    'phone': lead_data.get('phone') or None,
                    'company': lead_data.get('company') or None,
                    'position': lead_data.get('position') or None,
                    'budget': lead_data.get('budget') if lead_data.get('budget') and str(lead_data.get('budget')).strip() != '' else None,
                    'expected_close_date': lead_data.get('expected_close_date') if lead_data.get('expected_close_date') and str(lead_data.get('expected_close_date')).strip() != '' else None,
                    'category_id': lead_data.get('lead_category_id'),
                    'state_id': lead_data.get('lead_state_id'),
                    'priority_id': lead_data.get('lead_priority_id'),
                    'source_id': lead_data.get('lead_source_id'),
                    'assigned_to': lead_data.get('assigned_to'),
                    'group_id': lead_data.get('group_id'),
                    'notes': lead_data.get('notes') or None,
                    'created_by': lead_data.get('created_by')
                }
                
                result = self.supabase.table('leads').insert(supabase_data).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore create_lead Supabase: {e}")
                return False
        else:
            query = """
                INSERT INTO leads (
                    first_name, last_name, email, phone, company, position,
                    source_id, category_id, state_id, priority_id, assigned_to,
                    notes, budget, expected_close_date, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                lead_data['first_name'], lead_data['last_name'], lead_data['email'],
                lead_data['phone'], lead_data['company'], lead_data['position'],
                lead_data['source_id'], lead_data['category_id'], lead_data['state_id'],
                lead_data['priority_id'], lead_data['assigned_to'], lead_data['notes'],
                lead_data['budget'], lead_data['expected_close_date'], lead_data['created_by']
            )
            rows_affected = self.execute_update(query, params)
            return rows_affected > 0
    
    def update_lead(self, lead_id: int, lead_data: Dict) -> bool:
        """Aggiorna un lead esistente"""
        if self.use_supabase:
            try:
                # Costruisci solo i campi che sono stati forniti
                supabase_data = {}
                
                # Gestisci il nome solo se first_name o last_name sono forniti
                if 'first_name' in lead_data or 'last_name' in lead_data:
                    supabase_data['name'] = f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}".strip()
                elif 'name' in lead_data:
                    supabase_data['name'] = lead_data['name']
                
                # Aggiorna solo i campi forniti
                if 'email' in lead_data:
                    supabase_data['email'] = lead_data['email'] or None
                if 'phone' in lead_data:
                    supabase_data['phone'] = lead_data['phone'] or None
                if 'company' in lead_data:
                    supabase_data['company'] = lead_data['company'] or None
                if 'position' in lead_data:
                    supabase_data['position'] = lead_data['position'] or None
                if 'budget' in lead_data:
                    supabase_data['budget'] = lead_data['budget'] if lead_data['budget'] and str(lead_data['budget']).strip() != '' else None
                if 'expected_close_date' in lead_data:
                    supabase_data['expected_close_date'] = lead_data['expected_close_date'] if lead_data['expected_close_date'] and str(lead_data['expected_close_date']).strip() != '' else None
                if 'lead_category_id' in lead_data:
                    supabase_data['category_id'] = lead_data['lead_category_id']
                if 'lead_state_id' in lead_data:
                    supabase_data['state_id'] = lead_data['lead_state_id']
                if 'lead_priority_id' in lead_data:
                    supabase_data['priority_id'] = lead_data['lead_priority_id']
                if 'lead_source_id' in lead_data:
                    supabase_data['source_id'] = lead_data['lead_source_id']
                if 'assigned_to' in lead_data:
                    supabase_data['assigned_to'] = lead_data['assigned_to']
                if 'group_id' in lead_data:
                    supabase_data['group_id'] = lead_data['group_id']
                if 'notes' in lead_data:
                    supabase_data['notes'] = lead_data['notes'] or None
                if 'created_by' in lead_data:
                    supabase_data['created_by'] = lead_data['created_by']
                
                result = self.supabase.table('leads').update(supabase_data).eq('id', lead_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore update_lead Supabase: {e}")
                return False
        else:
            query = """
                UPDATE leads SET
                    first_name = ?, last_name = ?, email = ?, phone = ?, company = ?,
                    position = ?, source_id = ?, category_id = ?, state_id = ?,
                    priority_id = ?, assigned_to = ?, notes = ?, budget = ?,
                    expected_close_date = ?, updated_at = DATETIME('now')
                WHERE id = ?
            """
            params = (
                lead_data['first_name'], lead_data['last_name'], lead_data['email'],
                lead_data['phone'], lead_data['company'], lead_data['position'],
                lead_data['source_id'], lead_data['category_id'], lead_data['state_id'],
                lead_data['priority_id'], lead_data['assigned_to'], lead_data['notes'],
                lead_data['budget'], lead_data['expected_close_date'], lead_id
            )
            rows_affected = self.execute_update(query, params)
            return rows_affected > 0
    
    def delete_lead(self, lead_id: int) -> bool:
        """Elimina un lead"""
        if self.use_supabase:
            try:
                result = self.supabase.table('leads').delete().eq('id', lead_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore delete_lead Supabase: {e}")
                return False
        else:
            query = "DELETE FROM leads WHERE id = ?"
            rows_affected = self.execute_update(query, (lead_id,))
            return rows_affected > 0
    
    # ==================== METODI TASK ====================
    
    def get_all_tasks(self) -> List[Dict]:
        """Ottiene tutti i task"""
        if self.use_supabase:
            try:
                result = self.supabase.table('tasks').select('*').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_all_tasks Supabase: {e}")
                return []
        else:
            query = """
                SELECT t.*, 
                       tt.name as task_type_name,
                       ts.name as state_name,
                       u.first_name || ' ' || u.last_name as assigned_to_name
                FROM tasks t
                LEFT JOIN task_types tt ON t.task_type_id = tt.id
                LEFT JOIN task_states ts ON t.state_id = ts.id
                LEFT JOIN users u ON t.assigned_to = u.id
                ORDER BY t.due_date ASC
            """
            return self.execute_query(query)
    
    def get_tasks(self, filters: Dict = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Ottiene i task con filtri opzionali"""
        if self.use_supabase:
            try:
                # Query semplice senza rename (gestiamo i nomi dopo)
                query = self.supabase.table('tasks').select('*')
                
                # Applica filtri se forniti
                if filters:
                    if filters.get('state_id'):
                        query = query.eq('state_id', filters['state_id'])
                    if filters.get('task_type_id'):
                        query = query.eq('task_type_id', filters['task_type_id'])
                    if filters.get('priority_id'):
                        query = query.eq('priority_id', filters['priority_id'])
                    if filters.get('assigned_to'):
                        query = query.eq('assigned_to', filters['assigned_to'])
                    if filters.get('lead_id'):
                        query = query.eq('lead_id', filters['lead_id'])
                    
                    # Filtri per date
                    if filters.get('due_filter'):
                        due_filter = filters['due_filter']
                        today = datetime.now().date()
                        
                        if due_filter == "Scaduti":
                            query = query.lt('due_date', today.isoformat())
                        elif due_filter == "Oggi":
                            query = query.eq('due_date', today.isoformat())
                        elif due_filter == "Questa settimana":
                            from datetime import timedelta
                            week_end = today + timedelta(days=7)
                            query = query.gte('due_date', today.isoformat()).lte('due_date', week_end.isoformat())
                        elif due_filter == "Questo mese":
                            from datetime import timedelta
                            month_end = today + timedelta(days=30)
                            query = query.gte('due_date', today.isoformat()).lte('due_date', month_end.isoformat())
                        elif due_filter == "Prossimi 7 giorni":
                            from datetime import timedelta
                            week_end = today + timedelta(days=7)
                            query = query.gte('due_date', today.isoformat()).lte('due_date', week_end.isoformat())
                    
                    if filters.get('created_filter'):
                        created_filter = filters['created_filter']
                        today = datetime.now().date()
                        
                        if created_filter == "Oggi":
                            query = query.gte('created_at', today.isoformat())
                        elif created_filter == "Ieri":
                            from datetime import timedelta
                            yesterday = today - timedelta(days=1)
                            query = query.gte('created_at', yesterday.isoformat()).lt('created_at', today.isoformat())
                        elif created_filter == "Ultima settimana":
                            from datetime import timedelta
                            week_ago = today - timedelta(days=7)
                            query = query.gte('created_at', week_ago.isoformat())
                        elif created_filter == "Ultimo mese":
                            from datetime import timedelta
                            month_ago = today - timedelta(days=30)
                            query = query.gte('created_at', month_ago.isoformat())
                
                # Ordina e limita
                result = query.order('due_date', desc=True).range(offset, offset + limit - 1).execute()
                tasks = result.data
                
                # Ottieni tutti i dati di lookup in una volta sola
                if tasks:
                    # Ottieni tutti gli stati
                    state_ids = list(set([task.get('state_id') for task in tasks if task.get('state_id')]))
                    states = {}
                    if state_ids:
                        state_result = self.supabase.table('task_states').select('id,name').in_('id', state_ids).execute()
                        states = {state['id']: state['name'] for state in state_result.data}
                    
                                    # Ottieni tutti i tipi
                type_ids = list(set([task.get('task_type_id') for task in tasks if task.get('task_type_id')]))
                types = {}
                if type_ids:
                    type_result = self.supabase.table('task_types').select('id,name').in_('id', type_ids).execute()
                    types = {t['id']: t['name'] for t in type_result.data}
                
                # Ottieni tutte le priorità dalla tabella lead_priorities
                priority_ids = list(set([task.get('priority_id') for task in tasks if task.get('priority_id')]))
                priorities = {}
                if priority_ids:
                    try:
                        priority_result = self.supabase.table('lead_priorities').select('id,name').in_('id', priority_ids).execute()
                        priorities = {p['id']: p['name'] for p in priority_result.data}
                    except Exception as e:
                        logger.warning(f"⚠️ Tabella lead_priorities non trovata: {e}")
                        # Usa valori di default per le priorità
                        priorities = {1: 'Alta', 2: 'Media', 3: 'Bassa'}
                
                # Ottieni tutti gli utenti assegnati
                user_ids = list(set([task.get('assigned_to') for task in tasks if task.get('assigned_to')]))
                users = {}
                if user_ids:
                    user_result = self.supabase.table('users').select('id,first_name,last_name').in_('id', user_ids).execute()
                    users = {u['id']: {'first_name': u.get('first_name', ''), 'last_name': u.get('last_name', '')} for u in user_result.data}
                
                # Ottieni tutti i lead associati (incluso il numero di telefono)
                lead_ids = list(set([task.get('lead_id') for task in tasks if task.get('lead_id')]))
                leads = {}
                if lead_ids:
                    lead_result = self.supabase.table('leads').select('id,name,phone').in_('id', lead_ids).execute()
                    leads = {l['id']: {'id': l.get('id'), 'name': l.get('name', ''), 'phone': l.get('phone', '')} for l in lead_result.data}
                
                # Aggiungi i nomi ai task
                for task in tasks:
                    task['state_name'] = states.get(task.get('state_id'), 'N/A')
                    task['task_type_name'] = types.get(task.get('task_type_id'), 'N/A')
                    task['priority_name'] = priorities.get(task.get('priority_id'), 'N/A')
                    
                    if task.get('assigned_to') and task['assigned_to'] in users:
                        user = users[task['assigned_to']]
                        task['assigned_first_name'] = user['first_name']
                        task['assigned_last_name'] = user['last_name']
                    else:
                        task['assigned_first_name'] = ''
                        task['assigned_last_name'] = ''
                    
                    if task.get('lead_id') and task['lead_id'] in leads:
                        lead = leads[task['lead_id']]
                        # Aggiungi l'ID del lead (numero cliente)
                        task['lead_client_id'] = lead['id']
                        # Aggiungi il numero di telefono del lead
                        task['lead_phone'] = lead['phone']
                        # Dividi il nome del lead in first_name e last_name
                        lead_name = lead['name']
                        if lead_name:
                            name_parts = lead_name.split(' ', 1)
                            task['lead_first_name'] = name_parts[0]
                            task['lead_last_name'] = name_parts[1] if len(name_parts) > 1 else ''
                        else:
                            task['lead_first_name'] = ''
                            task['lead_last_name'] = ''
                    else:
                        task['lead_client_id'] = None
                        task['lead_phone'] = ''
                        task['lead_first_name'] = ''
                        task['lead_last_name'] = ''
                
                return tasks
            except Exception as e:
                logger.error(f"❌ Errore get_tasks Supabase: {e}")
                return []
        else:
            base_query = """
                SELECT t.*, 
                       tt.name as task_type_name,
                       ts.name as state_name,
                       u.first_name || ' ' || u.last_name as assigned_to_name,
                       l.first_name as lead_first_name,
                       l.last_name as lead_last_name,
                       l.phone as lead_phone,
                       l.id as lead_client_id
                FROM tasks t
                LEFT JOIN task_types tt ON t.task_type_id = tt.id
                LEFT JOIN task_states ts ON t.state_id = ts.id
                LEFT JOIN users u ON t.assigned_to = u.id
                LEFT JOIN leads l ON t.lead_id = l.id
            """
            
            where_conditions = []
            params = []
            
            if filters:
                if filters.get('state_id'):
                    where_conditions.append("t.state_id = ?")
                    params.append(filters['state_id'])
                
                if filters.get('task_type_id'):
                    where_conditions.append("t.task_type_id = ?")
                    params.append(filters['task_type_id'])
                
                if filters.get('priority_id'):
                    where_conditions.append("t.priority_id = ?")
                    params.append(filters['priority_id'])
                
                if filters.get('assigned_to'):
                    where_conditions.append("t.assigned_to = ?")
                    params.append(filters['assigned_to'])
                
                if filters.get('lead_id'):
                    where_conditions.append("t.lead_id = ?")
                    params.append(filters['lead_id'])
                
                # Filtri per date
                if filters.get('due_filter'):
                    due_filter = filters['due_filter']
                    today = datetime.now().date()
                    
                    if due_filter == "Scaduti":
                        where_conditions.append("t.due_date < ?")
                        params.append(today.isoformat())
                    elif due_filter == "Oggi":
                        where_conditions.append("t.due_date = ?")
                        params.append(today.isoformat())
                    elif due_filter == "Questa settimana":
                        from datetime import timedelta
                        week_end = today + timedelta(days=7)
                        where_conditions.append("t.due_date >= ? AND t.due_date <= ?")
                        params.extend([today.isoformat(), week_end.isoformat()])
                    elif due_filter == "Questo mese":
                        from datetime import timedelta
                        month_end = today + timedelta(days=30)
                        where_conditions.append("t.due_date >= ? AND t.due_date <= ?")
                        params.extend([today.isoformat(), month_end.isoformat()])
                    elif due_filter == "Prossimi 7 giorni":
                        from datetime import timedelta
                        week_end = today + timedelta(days=7)
                        where_conditions.append("t.due_date >= ? AND t.due_date <= ?")
                        params.extend([today.isoformat(), week_end.isoformat()])
                
                if filters.get('created_filter'):
                    created_filter = filters['created_filter']
                    today = datetime.now().date()
                    
                    if created_filter == "Oggi":
                        where_conditions.append("DATE(t.created_at) = ?")
                        params.append(today.isoformat())
                    elif created_filter == "Ieri":
                        from datetime import timedelta
                        yesterday = today - timedelta(days=1)
                        where_conditions.append("DATE(t.created_at) = ?")
                        params.append(yesterday.isoformat())
                    elif created_filter == "Ultima settimana":
                        from datetime import timedelta
                        week_ago = today - timedelta(days=7)
                        where_conditions.append("DATE(t.created_at) >= ?")
                        params.append(week_ago.isoformat())
                    elif created_filter == "Ultimo mese":
                        from datetime import timedelta
                        month_ago = today - timedelta(days=30)
                        where_conditions.append("DATE(t.created_at) >= ?")
                        params.append(month_ago.isoformat())
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            base_query += " ORDER BY t.due_date ASC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            return self.execute_query(base_query, tuple(params))
    
    def create_task(self, task_data: Dict) -> bool:
        """Crea un nuovo task"""
        if self.use_supabase:
            try:
                result = self.supabase.table('tasks').insert(task_data).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore create_task Supabase: {e}")
                return False
        else:
            query = """
                INSERT INTO tasks (
                    title, description, task_type_id, state_id, priority_id,
                    assigned_to, lead_id, due_date, notes, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                task_data['title'], task_data['description'], task_data['task_type_id'],
                task_data['state_id'], task_data['priority_id'], task_data['assigned_to'],
                task_data['lead_id'], task_data['due_date'], task_data['notes'],
                task_data['created_by']
            )
            rows_affected = self.execute_update(query, params)
            return rows_affected > 0
    
    def update_task(self, task_id: int, task_data: Dict) -> bool:
        """Aggiorna un task esistente"""
        if self.use_supabase:
            try:
                result = self.supabase.table('tasks').update(task_data).eq('id', task_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore update_task Supabase: {e}")
                return False
        else:
            query = """
                UPDATE tasks SET
                    title = ?, description = ?, task_type_id = ?, state_id = ?,
                    priority_id = ?, assigned_to = ?, lead_id = ?, due_date = ?,
                    notes = ?, updated_at = DATETIME('now')
                WHERE id = ?
            """
            params = (
                task_data['title'], task_data['description'], task_data['task_type_id'],
                task_data['state_id'], task_data['priority_id'], task_data['assigned_to'],
                task_data['lead_id'], task_data['due_date'], task_data['notes'], task_id
            )
            rows_affected = self.execute_update(query, params)
            return rows_affected > 0
    
    def delete_task(self, task_id: int) -> bool:
        """Elimina un task"""
        if self.use_supabase:
            try:
                result = self.supabase.table('tasks').delete().eq('id', task_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore delete_task Supabase: {e}")
                return False
        else:
            query = "DELETE FROM tasks WHERE id = ?"
            rows_affected = self.execute_update(query, (task_id,))
            return rows_affected > 0
    
    def update_task_state(self, task_id: int, new_state_id: int) -> bool:
        """Aggiorna lo stato di un task"""
        if self.use_supabase:
            try:
                result = self.supabase.table('tasks').update({
                    'state_id': new_state_id,
                    'updated_at': datetime.now().isoformat()
                }).eq('id', task_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore update_task_state Supabase: {e}")
                return False
        else:
            query = """
                UPDATE tasks SET
                    state_id = ?, updated_at = DATETIME('now')
                WHERE id = ?
            """
            return self.execute_update(query, (new_state_id, task_id)) > 0
    
    # ==================== METODI UTENTI ====================
    
    def get_all_users(self) -> List[Dict]:
        """Ottiene tutti gli utenti"""
        if self.use_supabase:
            try:
                result = self.supabase.table('users').select('*').execute()
                users = result.data
                
                # Ottieni tutti i dati di lookup in una volta sola
                if users:
                    # Ottieni tutti i ruoli
                    role_ids = list(set([user.get('role_id') for user in users if user.get('role_id')]))
                    roles = {}
                    if role_ids:
                        role_result = self.supabase.table('roles').select('id,name').in_('id', role_ids).execute()
                        roles = {role['id']: role['name'] for role in role_result.data}
                    
                    # Ottieni tutti i dipartimenti
                    dept_ids = list(set([user.get('department_id') for user in users if user.get('department_id')]))
                    departments = {}
                    if dept_ids:
                        dept_result = self.supabase.table('departments').select('id,name').in_('id', dept_ids).execute()
                        departments = {dept['id']: dept['name'] for dept in dept_result.data}
                    
                    # Aggiungi i nomi agli utenti
                    for user in users:
                        user['role_name'] = roles.get(user.get('role_id'), 'N/A')
                        user['department_name'] = departments.get(user.get('department_id'), 'N/A')
                
                return users
            except Exception as e:
                logger.error(f"❌ Errore get_all_users Supabase: {e}")
                return []
        else:
            query = """
                SELECT u.*, r.name as role_name, d.name as department_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                LEFT JOIN departments d ON u.department_id = d.id
                ORDER BY u.created_at DESC
            """
            return self.execute_query(query)
    
    def get_users(self, filters: Dict = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Ottiene gli utenti con filtri opzionali"""
        if self.use_supabase:
            try:
                query = self.supabase.table('users').select('*')
                
                # Applica filtri se forniti
                if filters:
                    if filters.get('role_id'):
                        query = query.eq('role_id', filters['role_id'])
                    if filters.get('department_id'):
                        query = query.eq('department_id', filters['department_id'])
                    if filters.get('is_active') is not None:
                        query = query.eq('is_active', filters['is_active'])
                    if filters.get('search'):
                        search_term = filters['search']
                        # Ricerca in più campi
                        query = query.or_(f"username.ilike.%{search_term}%,email.ilike.%{search_term}%,first_name.ilike.%{search_term}%,last_name.ilike.%{search_term}%")
                
                # Ordina e limita
                result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
                users = result.data
                
                # Aggiungi i nomi dei ruoli e dipartimenti
                for user in users:
                    # Ottieni nome ruolo
                    if user.get('role_id'):
                        role_result = self.supabase.table('roles').select('name').eq('id', user['role_id']).execute()
                        if role_result.data:
                            user['role_name'] = role_result.data[0]['name']
                    
                    # Ottieni nome dipartimento
                    if user.get('department_id'):
                        dept_result = self.supabase.table('departments').select('name').eq('id', user['department_id']).execute()
                        if dept_result.data:
                            user['department_name'] = dept_result.data[0]['name']
                
                return users
            except Exception as e:
                logger.error(f"❌ Errore get_users Supabase: {e}")
                return []
        else:
            base_query = """
                SELECT u.*, 
                       r.name as role_name,
                       d.name as department_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                LEFT JOIN departments d ON u.department_id = d.id
            """
            
            where_conditions = []
            params = []
            
            if filters:
                if filters.get('role_id'):
                    where_conditions.append("u.role_id = ?")
                    params.append(filters['role_id'])
                
                if filters.get('department_id'):
                    where_conditions.append("u.department_id = ?")
                    params.append(filters['department_id'])
                
                if filters.get('is_active') is not None:
                    where_conditions.append("u.is_active = ?")
                    params.append(filters['is_active'])
                
                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    where_conditions.append("(u.username LIKE ? OR u.email LIKE ? OR u.first_name LIKE ? OR u.last_name LIKE ?)")
                    params.extend([search_term, search_term, search_term, search_term])
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            base_query += " ORDER BY u.created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            return self.execute_query(base_query, tuple(params))
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Ottiene un utente per username"""
        if self.use_supabase:
            try:
                result = self.supabase.table('users').select('*').eq('username', username).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                logger.error(f"❌ Errore get_user_by_username Supabase: {e}")
                return None
        else:
            query = """
                SELECT u.*, r.name as role_name, d.name as department_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                LEFT JOIN departments d ON u.department_id = d.id
                WHERE u.username = ? AND u.is_active = 1
            """
            results = self.execute_query(query, (username,))
            return results[0] if results else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Ottiene un utente per email"""
        if self.use_supabase:
            try:
                result = self.supabase.table('users').select('*').eq('email', email).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                logger.error(f"❌ Errore get_user_by_email Supabase: {e}")
                return None
        else:
            query = """
                SELECT u.*, r.name as role_name, d.name as department_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                LEFT JOIN departments d ON u.department_id = d.id
                WHERE u.email = ? AND u.is_active = 1
            """
            results = self.execute_query(query, (email,))
            return results[0] if results else None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Ottiene un utente specifico"""
        if self.use_supabase:
            try:
                result = self.supabase.table('users').select('*').eq('id', user_id).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                logger.error(f"❌ Errore get_user Supabase: {e}")
                return None
        else:
            query = """
                SELECT u.*, r.name as role_name, d.name as department_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                LEFT JOIN departments d ON u.department_id = d.id
                WHERE u.id = ?
            """
            results = self.execute_query(query, (user_id,))
            return results[0] if results else None
    
    def create_user(self, user_data: Dict) -> Optional[int]:
        """Crea un nuovo utente e restituisce l'ID dell'utente creato"""
        if self.use_supabase:
            try:
                # Gestisce l'hashing della password se viene fornita in chiaro
                password_hash = user_data.get('password_hash', '')
                if not password_hash and 'password' in user_data:
                    # Se non c'è password_hash ma c'è password, hashala
                    import bcrypt
                    password_bytes = user_data['password'].encode('utf-8')
                    salt = bcrypt.gensalt()
                    password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
                
                # Mappa i dati per la struttura corretta di Supabase
                supabase_data = {
                    'username': user_data.get('username', user_data.get('email', '')),  # Usa email come username se non fornito
                    'email': user_data.get('email', ''),
                    'password_hash': password_hash,
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'phone': user_data.get('phone', ''),
                    'role_id': user_data.get('role_id', 1),  # Default role_id = 1
                    'is_active': user_data.get('is_active', True),
                    'is_admin': user_data.get('is_admin', False),
                    'notes': user_data.get('notes', ''),
                    'department_id': user_data.get('department_id'),
                    'created_by': user_data.get('created_by')
                }
                
                result = self.supabase.table('users').insert(supabase_data).execute()
                if len(result.data) > 0:
                    # Restituisce l'ID dell'utente creato
                    return result.data[0]['id']
                return None
            except Exception as e:
                logger.error(f"❌ Errore create_user Supabase: {e}")
                return None
        else:
            # Gestisce l'hashing della password per SQLite
            password_hash = user_data.get('password_hash', '')
            if not password_hash and 'password' in user_data:
                import bcrypt
                password_bytes = user_data['password'].encode('utf-8')
                salt = bcrypt.gensalt()
                password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
            
            query = """
                INSERT INTO users (
                    username, first_name, last_name, email, password_hash,
                    role_id, department_id, is_active, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                user_data['username'], user_data['first_name'], user_data['last_name'],
                user_data['email'], password_hash, user_data['role_id'],
                user_data['department_id'], user_data['is_active'], user_data['created_by']
            )
            rows_affected = self.execute_update(query, params)
            if rows_affected > 0:
                # Per SQLite, ottieni l'ultimo ID inserito
                cursor = self.conn.execute("SELECT last_insert_rowid()")
                return cursor.fetchone()[0]
            return None
    
    def update_user(self, user_id: int, user_data: Dict) -> bool:
        """Aggiorna un utente esistente"""
        if self.use_supabase:
            try:
                # Gestisce l'hashing della password se viene fornita in chiaro
                password_hash = user_data.get('password_hash', '')
                if not password_hash and 'password' in user_data:
                    # Se non c'è password_hash ma c'è password, hashala
                    import bcrypt
                    password_bytes = user_data['password'].encode('utf-8')
                    salt = bcrypt.gensalt()
                    password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
                
                # Mappa i dati per la struttura corretta di Supabase
                supabase_data = {
                    'username': user_data.get('username', user_data.get('email', '')),
                    'email': user_data.get('email', ''),
                    'password_hash': password_hash,
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'phone': user_data.get('phone', ''),
                    'role_id': user_data.get('role_id', 1),
                    'is_active': user_data.get('is_active', True),
                    'is_admin': user_data.get('is_admin', False),
                    'notes': user_data.get('notes', ''),
                    'department_id': user_data.get('department_id')
                }
                
                result = self.supabase.table('users').update(supabase_data).eq('id', user_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore update_user Supabase: {e}")
                return False
        else:
            # Gestisce l'hashing della password per SQLite
            password_hash = user_data.get('password_hash', '')
            if not password_hash and 'password' in user_data:
                import bcrypt
                password_bytes = user_data['password'].encode('utf-8')
                salt = bcrypt.gensalt()
                password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
            
            # Costruisce la query dinamicamente per includere password_hash solo se necessario
            if password_hash:
                query = """
                    UPDATE users SET
                        username = ?, first_name = ?, last_name = ?, email = ?,
                        password_hash = ?, role_id = ?, department_id = ?, is_active = ?, updated_at = DATETIME('now')
                    WHERE id = ?
                """
                params = (
                    user_data['username'], user_data['first_name'], user_data['last_name'],
                    user_data['email'], password_hash, user_data['role_id'], user_data['department_id'],
                    user_data['is_active'], user_id
                )
            else:
                query = """
                    UPDATE users SET
                        username = ?, first_name = ?, last_name = ?, email = ?,
                        role_id = ?, department_id = ?, is_active = ?, updated_at = DATETIME('now')
                    WHERE id = ?
                """
                params = (
                    user_data['username'], user_data['first_name'], user_data['last_name'],
                    user_data['email'], user_data['role_id'], user_data['department_id'],
                    user_data['is_active'], user_id
                )
            
            rows_affected = self.execute_update(query, params)
            return rows_affected > 0
    
    def delete_user(self, user_id: int) -> bool:
        """Elimina un utente"""
        if self.use_supabase:
            try:
                result = self.supabase.table('users').delete().eq('id', user_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore delete_user Supabase: {e}")
                return False
        else:
            query = "DELETE FROM users WHERE id = ?"
            rows_affected = self.execute_update(query, (user_id,))
            return rows_affected > 0
    
    def update_user_last_login(self, user_id: int) -> bool:
        """Aggiorna l'ultimo login di un utente"""
        if self.use_supabase:
            try:
                result = self.supabase.table('users').update({
                    'last_login': datetime.now().isoformat()
                }).eq('id', user_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore update_user_last_login Supabase: {e}")
                return False
        else:
            query = "UPDATE users SET last_login = DATETIME('now') WHERE id = ?"
            rows_affected = self.execute_update(query, (user_id,))
            return rows_affected > 0
    
    # ==================== METODI LOOKUP ====================
    
    def get_lead_states(self) -> List[Dict]:
        """Ottiene gli stati dei lead"""
        if self.use_supabase:
            try:
                result = self.supabase.table('lead_states').select('*').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_lead_states Supabase: {e}")
                return []
        else:
            return self.execute_query("SELECT * FROM lead_states ORDER BY id")
    
    def get_lead_priorities(self) -> List[Dict]:
        """Ottiene le priorità dei lead"""
        if self.use_supabase:
            try:
                result = self.supabase.table('lead_priorities').select('*').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_lead_priorities Supabase: {e}")
                return []
        else:
            return self.execute_query("SELECT * FROM lead_priorities ORDER BY id")
    
    def get_lead_categories(self) -> List[Dict]:
        """Ottiene le categorie dei lead"""
        if self.use_supabase:
            try:
                result = self.supabase.table('lead_categories').select('*').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_lead_categories Supabase: {e}")
                return []
        else:
            return self.execute_query("SELECT * FROM lead_categories ORDER BY id")
    
    def get_lead_sources(self) -> List[Dict]:
        """Ottiene le fonti dei lead"""
        if self.use_supabase:
            try:
                result = self.supabase.table('lead_sources').select('*').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_lead_sources Supabase: {e}")
                return []
        else:
            return self.execute_query("SELECT * FROM lead_sources ORDER BY id")
    
    def get_task_states(self) -> List[Dict]:
        """Ottiene gli stati dei task"""
        if self.use_supabase:
            try:
                result = self.supabase.table('task_states').select('*').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_task_states Supabase: {e}")
                return []
        else:
            return self.execute_query("SELECT * FROM task_states ORDER BY id")
    
    def get_task_types(self) -> List[Dict]:
        """Ottiene i tipi di task"""
        if self.use_supabase:
            try:
                result = self.supabase.table('task_types').select('*').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_task_types Supabase: {e}")
                return []
        else:
            return self.execute_query("SELECT * FROM task_types ORDER BY id")
    
    def get_roles(self) -> List[Dict]:
        """Ottiene i ruoli"""
        if self.use_supabase:
            try:
                result = self.supabase.table('roles').select('*').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_roles Supabase: {e}")
                return []
        else:
            return self.execute_query("SELECT * FROM roles ORDER BY id")
    
    def create_role(self, role_data: Dict) -> Optional[int]:
        """Crea un nuovo ruolo e restituisce l'ID del ruolo creato"""
        if self.use_supabase:
            try:
                # Mappa i dati per la struttura corretta di Supabase
                supabase_data = {
                    'name': role_data.get('name', ''),
                    'description': role_data.get('description', ''),
                    'permissions': role_data.get('permissions', [])
                }
                
                result = self.supabase.table('roles').insert(supabase_data).execute()
                if len(result.data) > 0:
                    # Restituisce l'ID del ruolo creato
                    return result.data[0]['id']
                return None
            except Exception as e:
                logger.error(f"❌ Errore create_role Supabase: {e}")
                return None
        else:
            query = """
                INSERT INTO roles (name, description, permissions)
                VALUES (?, ?, ?)
            """
            params = (
                role_data['name'],
                role_data['description'],
                json.dumps(role_data['permissions']) if isinstance(role_data['permissions'], list) else role_data['permissions']
            )
            rows_affected = self.execute_update(query, params)
            if rows_affected > 0:
                # Per SQLite, ottieni l'ultimo ID inserito
                cursor = self.conn.execute("SELECT last_insert_rowid()")
                return cursor.fetchone()[0]
            return None
    
    def get_departments(self) -> List[Dict]:
        """Ottiene i dipartimenti"""
        if self.use_supabase:
            try:
                result = self.supabase.table('departments').select('*').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_departments Supabase: {e}")
                return []
        else:
            return self.execute_query("SELECT * FROM departments ORDER BY id")
    
    def get_lead_stats(self) -> Dict:
        """Ottiene statistiche sui lead"""
        if self.use_supabase:
            try:
                # Ottieni tutti i lead
                leads = self.get_all_leads()
                
                # Calcola statistiche
                total_leads = len(leads)
                leads_by_state = {}
                leads_by_category = {}
                leads_by_source = {}
                
                for lead in leads:
                    # Per stato
                    state_id = lead.get('state_id')
                    if state_id:
                        state_name = f"State_{state_id}"
                        leads_by_state[state_name] = leads_by_state.get(state_name, 0) + 1
                    
                    # Per categoria
                    category_id = lead.get('category_id')
                    if category_id:
                        category_name = f"Category_{category_id}"
                        leads_by_category[category_name] = leads_by_category.get(category_name, 0) + 1
                    
                    # Per fonte
                    source_id = lead.get('source_id')
                    if source_id:
                        source_name = f"Source_{source_id}"
                        leads_by_source[source_name] = leads_by_source.get(source_name, 0) + 1
                
                return {
                    'total_leads': total_leads,
                    'leads_by_state': [{'name': k, 'count': v} for k, v in leads_by_state.items()],
                    'leads_by_category': [{'name': k, 'count': v} for k, v in leads_by_category.items()],
                    'leads_by_source': [{'name': k, 'count': v} for k, v in leads_by_source.items()]
                }
            except Exception as e:
                logger.error(f"❌ Errore get_lead_stats Supabase: {e}")
                return {
                    'total_leads': 0,
                    'leads_by_state': [],
                    'leads_by_category': [],
                    'leads_by_source': []
                }
        else:
            # Implementazione SQLite
            queries = {
                'total_leads': "SELECT COUNT(*) as count FROM leads",
                'leads_by_state': """
                    SELECT ls.name, COUNT(l.id) as count
                    FROM lead_states ls
                    LEFT JOIN leads l ON ls.id = l.state_id
                    GROUP BY ls.id, ls.name
                    ORDER BY ls.order_index
                """,
                'leads_by_category': """
                    SELECT lc.name, COUNT(l.id) as count
                    FROM lead_categories lc
                    LEFT JOIN leads l ON lc.id = l.category_id
                    GROUP BY lc.id, lc.name
                    ORDER BY count DESC
                """,
                'leads_by_source': """
                    SELECT ls.name, COUNT(l.id) as count
                    FROM lead_sources ls
                    LEFT JOIN leads l ON ls.id = l.source_id
                    WHERE ls.is_active = 1
                    GROUP BY ls.id, ls.name
                    ORDER BY count DESC
                """
            }
            
            stats = {}
            for key, query in queries.items():
                stats[key] = self.execute_query(query)
            
            return stats
    
    def get_task_stats(self) -> Dict:
        """Ottiene statistiche sui task"""
        if self.use_supabase:
            try:
                # Ottieni tutti i task
                tasks = self.get_all_tasks()
                
                # Calcola statistiche
                total_tasks = len(tasks)
                tasks_by_state = {}
                overdue_tasks = 0
                
                for task in tasks:
                    # Per stato
                    state_id = task.get('state_id')
                    if state_id:
                        state_name = f"State_{state_id}"
                        tasks_by_state[state_name] = tasks_by_state.get(state_name, 0) + 1
                    
                    # Task scaduti
                    due_date = task.get('due_date')
                    if due_date:
                        from datetime import datetime
                        try:
                            due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                            if due_date_obj < datetime.now() and state_id != 3:  # Non completati
                                overdue_tasks += 1
                        except:
                            pass
                
                return {
                    'total_tasks': total_tasks,
                    'tasks_by_state': [{'name': k, 'count': v} for k, v in tasks_by_state.items()],
                    'overdue_tasks': overdue_tasks
                }
            except Exception as e:
                logger.error(f"❌ Errore get_task_stats Supabase: {e}")
                return {
                    'total_tasks': 0,
                    'tasks_by_state': [],
                    'overdue_tasks': 0
                }
        else:
            # Implementazione SQLite
            queries = {
                'total_tasks': "SELECT COUNT(*) as count FROM tasks",
                'tasks_by_state': """
                    SELECT ts.name, COUNT(t.id) as count
                    FROM task_states ts
                    LEFT JOIN tasks t ON ts.id = t.state_id
                    GROUP BY ts.id, ts.name
                    ORDER BY ts.id
                """,
                'overdue_tasks': """
                    SELECT COUNT(*) as count
                    FROM tasks
                    WHERE due_date < DATE('now') AND state_id != 3
                """
            }
            
            stats = {}
            for key, query in queries.items():
                stats[key] = self.execute_query(query)
            
            return stats
    
    def get_user_stats(self) -> Dict:
        """Ottiene statistiche sugli utenti"""
        if self.use_supabase:
            try:
                # Ottieni tutti gli utenti
                users = self.get_all_users()
                
                # Calcola statistiche
                total_users = len(users)
                active_users = sum(1 for user in users if user.get('is_active', False))
                admin_users = sum(1 for user in users if user.get('is_admin', False))
                users_by_role = {}
                
                for user in users:
                    role_id = user.get('role_id')
                    if role_id:
                        role_name = f"Role_{role_id}"
                        users_by_role[role_name] = users_by_role.get(role_name, 0) + 1
                
                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'admin_users': admin_users,
                    'users_by_role': [{'name': k, 'count': v} for k, v in users_by_role.items()]
                }
            except Exception as e:
                logger.error(f"❌ Errore get_user_stats Supabase: {e}")
                return {
                    'total_users': 0,
                    'active_users': 0,
                    'admin_users': 0,
                    'users_by_role': []
                }
        else:
            # Implementazione SQLite
            queries = {
                'total_users': "SELECT COUNT(*) as count FROM users",
                'active_users': "SELECT COUNT(*) as count FROM users WHERE is_active = 1",
                'admin_users': "SELECT COUNT(*) as count FROM users WHERE is_admin = 1",
                'users_by_role': """
                    SELECT r.name, COUNT(u.id) as count
                    FROM roles r
                    LEFT JOIN users u ON r.id = u.role_id
                    GROUP BY r.id, r.name
                    ORDER BY count DESC
                """
            }
            
            stats = {}
            for key, query in queries.items():
                stats[key] = self.execute_query(query)
            
            return stats
    
    # ==================== METODI IMPOSTAZIONI ====================

    def get_settings_by_category(self, category: str) -> List[Dict]:
        """Ottiene le impostazioni per categoria"""
        if self.use_supabase:
            try:
                result = self.supabase.table('settings').select('*').ilike('key', f"{category}_%").execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_settings_by_category Supabase: {e}")
                return []
        else:
            query = """
                SELECT key, value, description, updated_at
                FROM settings
                WHERE key LIKE ?
                ORDER BY key
            """
            return self.execute_query(query, (f"{category}_%",))

    def get_setting(self, key: str) -> Optional[Dict]:
        """Ottiene una singola impostazione"""
        if self.use_supabase:
            try:
                result = self.supabase.table('settings').select('*').eq('key', key).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                logger.error(f"❌ Errore get_setting Supabase: {e}")
                return None
        else:
            query = "SELECT * FROM settings WHERE key = ?"
            results = self.execute_query(query, (key,))
            return results[0] if results else None

    def update_setting(self, key: str, value: str, description: str = None) -> bool:
        """Aggiorna o crea un'impostazione"""
        if self.use_supabase:
            try:
                existing = self.get_setting(key)
                if existing:
                    result = self.supabase.table('settings').update({
                        'value': str(value),
                        'updated_at': datetime.now().isoformat()
                    }).eq('key', key).execute()
                else:
                    result = self.supabase.table('settings').insert({
                        'key': key,
                        'value': str(value),
                        'description': description or f"Impostazione: {key}"
                    }).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore update_setting Supabase: {e}")
                return False
        else:
            existing = self.get_setting(key)
            if existing:
                query = "UPDATE settings SET value = ?, updated_at = DATETIME('now') WHERE key = ?"
                params = (str(value), key)
            else:
                query = "INSERT INTO settings (key, value, description) VALUES (?, ?, ?)"
                params = (key, str(value), description or f"Impostazione: {key}")
            rows_affected = self.execute_update(query, params)
            return rows_affected > 0

    def delete_setting(self, key: str) -> bool:
        """Elimina un'impostazione"""
        if self.use_supabase:
            try:
                result = self.supabase.table('settings').delete().eq('key', key).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore delete_setting Supabase: {e}")
                return False
        else:
            query = "DELETE FROM settings WHERE key = ?"
            rows_affected = self.execute_update(query, (key,))
            return rows_affected > 0

    def backup_database(self) -> str:
        """Crea un backup del database"""
        if self.use_supabase:
            # Per Supabase, creiamo un backup dei dati principali
            try:
                import shutil
                from datetime import datetime
                backup_dir = Path(self.db_path).parent / "backups"
                backup_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"supabase_backup_{timestamp}.json"
                backup_path = backup_dir / backup_filename
                
                # Esporta dati principali
                backup_data = {
                    'leads': self.get_all_leads(),
                    'tasks': self.get_all_tasks(),
                    'users': self.get_all_users(),
                    'settings': self.get_settings_by_category(''),
                    'timestamp': timestamp
                }
                
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, default=str)
                
                self.log_activity(
                    user_id=1,  # Admin
                    action='database_backup',
                    entity_type='system',
                    entity_id=0,
                    details=f"Backup Supabase creato: {backup_filename}"
                )
                return str(backup_path)
            except Exception as e:
                logger.error(f"❌ Errore backup Supabase: {e}")
                raise
        else:
            import shutil
            from datetime import datetime
            backup_dir = Path(self.db_path).parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"leads_database_backup_{timestamp}.db"
            backup_path = backup_dir / backup_filename
            shutil.copy2(self.db_path, backup_path)
            self.log_activity(
                user_id=1,  # Admin
                action='database_backup',
                entity_type='system',
                entity_id=0,
                details=f"Backup creato: {backup_filename}"
            )
            return str(backup_path)

    # ==================== METODI LOG ====================

    def log_activity(self, user_id: int, action: str, entity_type: str, entity_id: int, details: str = None):
        """Registra un'attività nel log"""
        if self.use_supabase:
            try:
                log_data = {
                    'user_id': user_id,
                    'action': action,
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'details': details,
                    'created_at': datetime.now().isoformat()
                }
                self.supabase.table('activity_log').insert(log_data).execute()
            except Exception as e:
                logger.error(f"❌ Errore log_activity Supabase: {e}")
        else:
            query = """
                INSERT INTO activity_log (user_id, action, entity_type, entity_id, details)
                VALUES (?, ?, ?, ?, ?)
            """
            try:
                self.execute_update(query, (user_id, action, entity_type, entity_id, details))
            except Exception as e:
                logger.error(f"❌ Errore log_activity SQLite: {e}")

    def get_activity_log(self, limit: int = 100) -> List[Dict]:
        """Ottiene il log delle attività"""
        if self.use_supabase:
            try:
                result = self.supabase.table('activity_log').select('*').order('created_at', desc=True).limit(limit).execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_activity_log Supabase: {e}")
                return []
        else:
            query = """
                SELECT al.*, u.first_name, u.last_name
                FROM activity_log al
                LEFT JOIN users u ON al.user_id = u.id
                ORDER BY al.created_at DESC
                LIMIT ?
            """
            return self.execute_query(query, (limit,))

    # ==================== METODI CONTATTI ====================
    
    def get_contact_templates(self) -> List[Dict]:
        """Ottiene i template di contatto"""
        if self.use_supabase:
            try:
                result = self.supabase.table('contact_templates').select('*').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_contact_templates Supabase: {e}")
                return []
        else:
            return self.execute_query("SELECT * FROM contact_templates ORDER BY id")
    
    def get_contact_sequences(self) -> List[Dict]:
        """Ottiene le sequenze di contatto"""
        if self.use_supabase:
            try:
                result = self.supabase.table('contact_sequences').select('*').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_contact_sequences Supabase: {e}")
                return []
        else:
            return self.execute_query("SELECT * FROM contact_sequences ORDER BY id")
    
    def create_contact_template(self, template_data: Dict) -> bool:
        """Crea un nuovo template di contatto"""
        if self.use_supabase:
            try:
                result = self.supabase.table('contact_templates').insert(template_data).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore create_contact_template Supabase: {e}")
                return False
        else:
            query = """
                INSERT INTO contact_templates (name, type, content, variables, category, delay_hours, retry_count, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                template_data['name'], template_data['type'], template_data['content'],
                template_data['variables'], template_data['category'], template_data['delay_hours'],
                template_data['retry_count'], template_data['priority']
            )
            return self.execute_update(query, params) > 0
    
    def create_contact_sequence(self, sequence_data: Dict) -> bool:
        """Crea una nuova sequenza di contatto"""
        if self.use_supabase:
            try:
                result = self.supabase.table('contact_sequences').insert(sequence_data).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore create_contact_sequence Supabase: {e}")
                return False
        else:
            query = """
                INSERT INTO contact_sequences (name, trigger_event, conditions, steps, is_active)
                VALUES (?, ?, ?, ?, ?)
            """
            params = (
                sequence_data['name'], sequence_data['trigger_event'], sequence_data['conditions'],
                sequence_data['steps'], sequence_data['is_active']
            )
            return self.execute_update(query, params) > 0
    
    def update_contact_template(self, template_id: int, template_data: Dict) -> bool:
        """Aggiorna un template di contatto"""
        if self.use_supabase:
            try:
                result = self.supabase.table('contact_templates').update(template_data).eq('id', template_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore update_contact_template Supabase: {e}")
                return False
        else:
            query = """
                UPDATE contact_templates SET
                    name = ?, type = ?, content = ?, variables = ?, category = ?,
                    delay_hours = ?, retry_count = ?, priority = ?, updated_at = DATETIME('now')
                WHERE id = ?
            """
            params = (
                template_data['name'], template_data['type'], template_data['content'],
                template_data['variables'], template_data['category'], template_data['delay_hours'],
                template_data['retry_count'], template_data['priority'], template_id
            )
            return self.execute_update(query, params) > 0
    
    def update_contact_sequence(self, sequence_id: int, sequence_data: Dict) -> bool:
        """Aggiorna una sequenza di contatto"""
        if self.use_supabase:
            try:
                result = self.supabase.table('contact_sequences').update(sequence_data).eq('id', sequence_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore update_contact_sequence Supabase: {e}")
                return False
        else:
            query = """
                UPDATE contact_sequences SET
                    name = ?, trigger_event = ?, conditions = ?, steps = ?, is_active = ?,
                    updated_at = DATETIME('now')
                WHERE id = ?
            """
            params = (
                sequence_data['name'], sequence_data['trigger_event'], sequence_data['conditions'],
                sequence_data['steps'], sequence_data['is_active'], sequence_id
            )
            return self.execute_update(query, params) > 0
    
    def delete_contact_template(self, template_id: int) -> bool:
        """Elimina un template di contatto"""
        if self.use_supabase:
            try:
                result = self.supabase.table('contact_templates').delete().eq('id', template_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore delete_contact_template Supabase: {e}")
                return False
        else:
            query = "DELETE FROM contact_templates WHERE id = ?"
            return self.execute_update(query, (template_id,)) > 0
    
    def delete_contact_sequence(self, sequence_id: int) -> bool:
        """Elimina una sequenza di contatto"""
        if self.use_supabase:
            try:
                result = self.supabase.table('contact_sequences').delete().eq('id', sequence_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore delete_contact_sequence Supabase: {e}")
                return False
        else:
            query = "DELETE FROM contact_sequences WHERE id = ?"
            return self.execute_update(query, (sequence_id,)) > 0
    
    def get_sequence_stats(self) -> Dict:
        """Ottiene le statistiche delle sequenze di contatto"""
        if self.use_supabase:
            try:
                # Ottieni tutte le sequenze
                sequences_result = self.supabase.table('contact_sequences').select('*').execute()
                sequences = sequences_result.data
                
                # Calcola statistiche
                total_sequences = len(sequences)
                active_sequences = len([s for s in sequences if s.get('is_active', False)])
                inactive_sequences = total_sequences - active_sequences
                
                # Statistiche per trigger event
                trigger_stats = {}
                for seq in sequences:
                    trigger = seq.get('trigger_event', 'Unknown')
                    trigger_stats[trigger] = trigger_stats.get(trigger, 0) + 1
                
                return {
                    'total_sequences': total_sequences,
                    'active_sequences': active_sequences,
                    'inactive_sequences': inactive_sequences,
                    'trigger_stats': trigger_stats
                }
            except Exception as e:
                logger.error(f"❌ Errore get_sequence_stats Supabase: {e}")
                return {
                    'total_sequences': 0,
                    'active_sequences': 0,
                    'inactive_sequences': 0,
                    'trigger_stats': {}
                }
        else:
            # Implementazione SQLite
            sequences = self.execute_query("SELECT * FROM contact_sequences")
            total_sequences = len(sequences)
            active_sequences = len([s for s in sequences if s.get('is_active', False)])
            inactive_sequences = total_sequences - active_sequences
            
            trigger_stats = {}
            for seq in sequences:
                trigger = seq.get('trigger_event', 'Unknown')
                trigger_stats[trigger] = trigger_stats.get(trigger, 0) + 1
            
            return {
                'total_sequences': total_sequences,
                'active_sequences': active_sequences,
                'inactive_sequences': inactive_sequences,
                'trigger_stats': trigger_stats
            }

    def close(self):
        """Chiude la connessione database"""
        if not self.use_supabase and hasattr(self, 'conn'):
            self.conn.close()

    # ========================================
    # METODI PER GESTIONE BROKER LINKS
    # ========================================
    
    def create_broker_link(self, broker_name: str, affiliate_link: str, created_by: str = None) -> Optional[int]:
        """Crea un nuovo link broker"""
        if self.use_supabase:
            try:
                # Prova prima con la tabella broker_links_simple (senza RLS)
                data = {
                    'broker_name': broker_name,
                    'affiliate_link': affiliate_link,
                    'is_active': True
                }
                result = self.supabase.table('broker_links_simple').insert(data).execute()
                if result.data:
                    logger.info("✅ Broker link creato in tabella broker_links_simple")
                    return result.data[0]['id']
                return None
            except Exception as e:
                logger.warning(f"⚠️ Tabella broker_links_simple non esiste, prova con broker_links: {e}")
                # Fallback alla tabella originale
                try:
                    data = {
                        'broker_name': broker_name,
                        'affiliate_link': affiliate_link,
                        'is_active': True
                    }
                    result = self.supabase.table('broker_links').insert(data).execute()
                    if result.data:
                        logger.info("✅ Broker link creato in tabella broker_links")
                        return result.data[0]['id']
                    return None
                except Exception as e2:
                    logger.error(f"❌ Errore create_broker_link Supabase: {e2}")
                    return None
        else:
            query = """
                INSERT INTO broker_links (broker_name, affiliate_link, created_by, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
            """
            try:
                cursor = self.conn.cursor()
                cursor.execute(query, (broker_name, affiliate_link, created_by, True))
                self.conn.commit()
                return cursor.lastrowid
            except Exception as e:
                logger.error(f"❌ Errore create_broker_link SQLite: {e}")
                self.conn.rollback()
                return None
    
    def is_valid_uuid(self, uuid_string: str) -> bool:
        """Verifica se una stringa è un UUID valido"""
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, uuid_string.lower()))
    
    def get_broker_links(self, active_only: bool = True) -> List[Dict]:
        """Ottiene tutti i link broker"""
        if self.use_supabase:
            try:
                # Prova prima con la tabella broker_links_simple
                query = self.supabase.table('broker_links_simple').select('*')
                if active_only:
                    query = query.eq('is_active', True)
                query = query.order('created_at', desc=True)
                result = query.execute()
                if result.data:
                    logger.info("✅ Broker links recuperati da broker_links_simple")
                    return result.data
                else:
                    # Fallback alla tabella originale
                    query = self.supabase.table('broker_links').select('*')
                    if active_only:
                        query = query.eq('is_active', True)
                    query = query.order('created_at', desc=True)
                    result = query.execute()
                    return result.data
            except Exception as e:
                logger.warning(f"⚠️ Errore con broker_links_simple, prova con broker_links: {e}")
                try:
                    query = self.supabase.table('broker_links').select('*')
                    if active_only:
                        query = query.eq('is_active', True)
                    query = query.order('created_at', desc=True)
                    result = query.execute()
                    return result.data
                except Exception as e2:
                    logger.error(f"❌ Errore get_broker_links Supabase: {e2}")
                    return []
        else:
            query = """
                SELECT bl.*, u.first_name, u.last_name 
                FROM broker_links bl
                LEFT JOIN users u ON bl.created_by = u.id
                WHERE bl.is_active = ?
                ORDER BY bl.created_at DESC
            """
            return self.execute_query(query, (active_only,))
    
    def get_broker_link(self, link_id: int) -> Optional[Dict]:
        """Ottiene un singolo link broker"""
        if self.use_supabase:
            try:
                # Prova prima con broker_links_simple (senza RLS)
                try:
                    result = self.supabase.table('broker_links_simple').select('*').eq('id', link_id).execute()
                    logger.info("✅ Broker link recuperato da broker_links_simple")
                    return result.data[0] if result.data else None
                except Exception as e:
                    logger.warning(f"⚠️ Fallback a broker_links originale: {e}")
                    result = self.supabase.table('broker_links').select('*').eq('id', link_id).execute()
                    return result.data[0] if result.data else None
            except Exception as e:
                logger.error(f"❌ Errore get_broker_link Supabase: {e}")
                return None
        else:
            query = """
                SELECT bl.*, u.first_name, u.last_name 
                FROM broker_links bl
                LEFT JOIN users u ON bl.created_by = u.id
                WHERE bl.id = ?
            """
            results = self.execute_query(query, (link_id,))
            return results[0] if results else None
    
    def update_broker_link(self, link_id: int, broker_name: str, affiliate_link: str, is_active: bool = True) -> bool:
        """Aggiorna un link broker"""
        if self.use_supabase:
            try:
                data = {
                    'broker_name': broker_name,
                    'affiliate_link': affiliate_link,
                    'is_active': is_active
                }
                # Prova prima con broker_links_simple (senza RLS)
                try:
                    result = self.supabase.table('broker_links_simple').update(data).eq('id', link_id).execute()
                    logger.info("✅ Broker link aggiornato in broker_links_simple")
                    return len(result.data) > 0
                except Exception as e:
                    logger.warning(f"⚠️ Fallback a broker_links originale: {e}")
                    result = self.supabase.table('broker_links').update(data).eq('id', link_id).execute()
                    return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore update_broker_link Supabase: {e}")
                return False
        else:
            query = """
                UPDATE broker_links 
                SET broker_name = ?, affiliate_link = ?, is_active = ?, updated_at = datetime('now')
                WHERE id = ?
            """
            return self.execute_update(query, (broker_name, affiliate_link, is_active, link_id)) > 0
    
    def delete_broker_link(self, link_id: int) -> bool:
        """Elimina un link broker"""
        if self.use_supabase:
            try:
                # Prova prima con broker_links_simple (senza RLS)
                try:
                    result = self.supabase.table('broker_links_simple').delete().eq('id', link_id).execute()
                    logger.info("✅ Broker link eliminato da broker_links_simple")
                    return len(result.data) > 0
                except Exception as e:
                    logger.warning(f"⚠️ Fallback a broker_links originale: {e}")
                    result = self.supabase.table('broker_links').delete().eq('id', link_id).execute()
                    return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore delete_broker_link Supabase: {e}")
                return False
        else:
            query = "DELETE FROM broker_links WHERE id = ?"
            return self.execute_update(query, (link_id,)) > 0
    
    def toggle_broker_link_status(self, link_id: int) -> bool:
        """Attiva/disattiva un link broker"""
        if self.use_supabase:
            try:
                # Prima ottieni lo stato attuale
                current = self.get_broker_link(link_id)
                if current is None:
                    return False
                
                new_status = not current.get('is_active', True)
                result = self.supabase.table('broker_links').update({'is_active': new_status}).eq('id', link_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore toggle_broker_link_status Supabase: {e}")
                return False
        else:
            query = """
                UPDATE broker_links 
                SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END,
                    updated_at = datetime('now')
                WHERE id = ?
            """
            return self.execute_update(query, (link_id,)) > 0
    
    def get_broker_links_stats(self) -> Dict:
        """Ottiene le statistiche dei link broker"""
        if self.use_supabase:
            try:
                # Prova prima con broker_links_simple (senza RLS)
                try:
                    all_links = self.supabase.table('broker_links_simple').select('*').execute()
                    links = all_links.data
                    logger.info("✅ Statistiche broker links ottenute da broker_links_simple")
                except Exception as e:
                    logger.warning(f"⚠️ Fallback a broker_links originale: {e}")
                    all_links = self.supabase.table('broker_links').select('*').execute()
                    links = all_links.data
                
                total_links = len(links)
                active_links = len([l for l in links if l.get('is_active', False)])
                inactive_links = total_links - active_links
                
                return {
                    'total_links': total_links,
                    'active_links': active_links,
                    'inactive_links': inactive_links
                }
            except Exception as e:
                logger.error(f"❌ Errore get_broker_links_stats Supabase: {e}")
                return {
                    'total_links': 0,
                    'active_links': 0,
                    'inactive_links': 0
                }
        else:
            query = """
                SELECT 
                    COUNT(*) as total_links,
                    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_links,
                    SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) as inactive_links
                FROM broker_links
            """
            results = self.execute_query(query)
            if results:
                return {
                    'total_links': results[0]['total_links'],
                    'active_links': results[0]['active_links'],
                    'inactive_links': results[0]['inactive_links']
                }
            return {
                'total_links': 0,
                'active_links': 0,
                'inactive_links': 0
            }

    # ========================================
    # METODI PER GESTIONE SCRIPTS
    # ========================================
    
    def create_script(self, title: str, content: str, script_type: str, category: str, created_by: str = None) -> Optional[int]:
        """Crea un nuovo script"""
        if self.use_supabase:
            try:
                data = {
                    'title': title,
                    'content': content,
                    'script_type': script_type,
                    'category': category,
                    'is_active': True
                }
                
                # Aggiungi created_by solo se è un UUID valido
                if created_by and self.is_valid_uuid(str(created_by)):
                    data['created_by'] = created_by
                
                # Prova prima con la tabella scripts_simple (senza RLS)
                try:
                    result = self.supabase.table('scripts_simple').insert(data).execute()
                    if result.data:
                        logger.info("✅ Script creato in tabella scripts_simple")
                        return result.data[0]['id']
                    return None
                except Exception as e:
                    logger.warning(f"⚠️ Tabella scripts_simple non esiste, prova con scripts: {e}")
                    # Fallback alla tabella originale
                    result = self.supabase.table('scripts').insert(data).execute()
                    if result.data:
                        logger.info("✅ Script creato in tabella scripts")
                        return result.data[0]['id']
                    return None
                    
            except Exception as e:
                logger.error(f"❌ Errore create_script Supabase: {e}")
                return None
        else:
            query = """
                INSERT INTO scripts (title, content, script_type, category, created_by, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """
            try:
                cursor = self.conn.cursor()
                cursor.execute(query, (title, content, script_type, category, created_by, True))
                self.conn.commit()
                return cursor.lastrowid
            except Exception as e:
                logger.error(f"❌ Errore create_script SQLite: {e}")
                self.conn.rollback()
                return None
    
    def get_scripts(self, active_only: bool = True, script_type: str = None, category: str = None) -> List[Dict]:
        """Ottiene tutti gli script con filtri opzionali"""
        if self.use_supabase:
            try:
                # Prova prima con la tabella scripts_simple
                try:
                    query = self.supabase.table('scripts_simple').select('*')
                    if active_only:
                        query = query.eq('is_active', True)
                    if script_type:
                        query = query.eq('script_type', script_type)
                    if category:
                        query = query.eq('category', category)
                    query = query.order('created_at', desc=True)
                    result = query.execute()
                    logger.info("✅ Script recuperati da scripts_simple")
                    return result.data
                except Exception as e:
                    logger.warning(f"⚠️ Tabella scripts_simple non esiste, prova con scripts: {e}")
                    # Fallback alla tabella originale
                    query = self.supabase.table('scripts').select('*')
                    if active_only:
                        query = query.eq('is_active', True)
                    if script_type:
                        query = query.eq('script_type', script_type)
                    if category:
                        query = query.eq('category', category)
                    query = query.order('created_at', desc=True)
                    result = query.execute()
                    return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_scripts Supabase: {e}")
                return []
        else:
            conditions = ["s.is_active = ?"]
            params = [active_only]
            
            if script_type:
                conditions.append("s.script_type = ?")
                params.append(script_type)
            if category:
                conditions.append("s.category = ?")
                params.append(category)
            
            where_clause = " AND ".join(conditions)
            query = f"""
                SELECT s.*, u.first_name, u.last_name 
                FROM scripts s
                LEFT JOIN users u ON s.created_by = u.id
                WHERE {where_clause}
                ORDER BY s.created_at DESC
            """
            return self.execute_query(query, tuple(params))
    
    def get_script(self, script_id: int) -> Optional[Dict]:
        """Ottiene un singolo script"""
        if self.use_supabase:
            try:
                # Prova prima con la tabella scripts_simple
                try:
                    result = self.supabase.table('scripts_simple').select('*').eq('id', script_id).execute()
                    if result.data:
                        return result.data[0]
                except Exception as e:
                    logger.warning(f"⚠️ Tabella scripts_simple non esiste, prova con scripts: {e}")
                    # Fallback alla tabella originale
                    result = self.supabase.table('scripts').select('*').eq('id', script_id).execute()
                    return result.data[0] if result.data else None
                return None
            except Exception as e:
                logger.error(f"❌ Errore get_script Supabase: {e}")
                return None
        else:
            query = """
                SELECT s.*, u.first_name, u.last_name 
                FROM scripts s
                LEFT JOIN users u ON s.created_by = u.id
                WHERE s.id = ?
            """
            results = self.execute_query(query, (script_id,))
            return results[0] if results else None
    
    def update_script(self, script_id: int, title: str, content: str, script_type: str, category: str, is_active: bool = True) -> bool:
        """Aggiorna un script"""
        if self.use_supabase:
            try:
                data = {
                    'title': title,
                    'content': content,
                    'script_type': script_type,
                    'category': category,
                    'is_active': is_active
                }
                
                # Prova prima con la tabella scripts_simple
                try:
                    result = self.supabase.table('scripts_simple').update(data).eq('id', script_id).execute()
                    if len(result.data) > 0:
                        logger.info("✅ Script aggiornato in scripts_simple")
                        return True
                except Exception as e:
                    logger.warning(f"⚠️ Tabella scripts_simple non esiste, prova con scripts: {e}")
                    # Fallback alla tabella originale
                    result = self.supabase.table('scripts').update(data).eq('id', script_id).execute()
                    return len(result.data) > 0
                return False
            except Exception as e:
                logger.error(f"❌ Errore update_script Supabase: {e}")
                return False
        else:
            query = """
                UPDATE scripts 
                SET title = ?, content = ?, script_type = ?, category = ?, is_active = ?, updated_at = datetime('now')
                WHERE id = ?
            """
            return self.execute_update(query, (title, content, script_type, category, is_active, script_id)) > 0
    
    def delete_script(self, script_id: int) -> bool:
        """Elimina un script"""
        if self.use_supabase:
            try:
                # Prova prima con la tabella scripts_simple
                try:
                    result = self.supabase.table('scripts_simple').delete().eq('id', script_id).execute()
                    if len(result.data) > 0:
                        logger.info("✅ Script eliminato da scripts_simple")
                        return True
                except Exception as e:
                    logger.warning(f"⚠️ Tabella scripts_simple non esiste, prova con scripts: {e}")
                    # Fallback alla tabella originale
                    result = self.supabase.table('scripts').delete().eq('id', script_id).execute()
                    return len(result.data) > 0
                return False
            except Exception as e:
                logger.error(f"❌ Errore delete_script Supabase: {e}")
                return False
        else:
            query = "DELETE FROM scripts WHERE id = ?"
            return self.execute_update(query, (script_id,)) > 0
    
    def toggle_script_status(self, script_id: int) -> bool:
        """Attiva/disattiva un script"""
        if self.use_supabase:
            try:
                # Prima ottieni lo stato attuale
                current = self.get_script(script_id)
                if current is None:
                    return False
                
                new_status = not current.get('is_active', True)
                result = self.supabase.table('scripts').update({'is_active': new_status}).eq('id', script_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore toggle_script_status Supabase: {e}")
                return False
        else:
            query = """
                UPDATE scripts 
                SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END,
                    updated_at = datetime('now')
                WHERE id = ?
            """
            return self.execute_update(query, (script_id,)) > 0
    
    def get_scripts_by_type(self, script_type: str, active_only: bool = True) -> List[Dict]:
        """Ottiene script filtrati per tipo"""
        return self.get_scripts(active_only=active_only, script_type=script_type)
    
    def get_scripts_by_category(self, category: str, active_only: bool = True) -> List[Dict]:
        """Ottiene script filtrati per categoria"""
        return self.get_scripts(active_only=active_only, category=category)
    
    def get_scripts_stats(self) -> Dict:
        """Ottiene le statistiche degli script"""
        if self.use_supabase:
            try:
                # Prova prima con scripts_simple (senza RLS)
                try:
                    all_scripts = self.supabase.table('scripts_simple').select('*').execute()
                    scripts = all_scripts.data
                    logger.info("✅ Statistiche ottenute da scripts_simple")
                except Exception as e:
                    logger.warning(f"⚠️ Fallback a scripts originale: {e}")
                    all_scripts = self.supabase.table('scripts').select('*').execute()
                    scripts = all_scripts.data
                
                total_scripts = len(scripts)
                active_scripts = len([s for s in scripts if s.get('is_active', False)])
                inactive_scripts = total_scripts - active_scripts
                
                # Statistiche per tipo
                type_stats = {}
                for script in scripts:
                    script_type = script.get('script_type', 'Unknown')
                    type_stats[script_type] = type_stats.get(script_type, 0) + 1
                
                # Statistiche per categoria
                category_stats = {}
                for script in scripts:
                    category = script.get('category', 'Unknown')
                    category_stats[category] = category_stats.get(category, 0) + 1
                
                return {
                    'total_scripts': total_scripts,
                    'active_scripts': active_scripts,
                    'inactive_scripts': inactive_scripts,
                    'type_stats': type_stats,
                    'category_stats': category_stats
                }
            except Exception as e:
                logger.error(f"❌ Errore get_scripts_stats Supabase: {e}")
                return {
                    'total_scripts': 0,
                    'active_scripts': 0,
                    'inactive_scripts': 0,
                    'type_stats': {},
                    'category_stats': {}
                }
        else:
            query = """
                SELECT 
                    COUNT(*) as total_scripts,
                    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_scripts,
                    SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) as inactive_scripts
                FROM scripts
            """
            results = self.execute_query(query)
            if results:
                return {
                    'total_scripts': results[0]['total_scripts'],
                    'active_scripts': results[0]['active_scripts'],
                    'inactive_scripts': results[0]['inactive_scripts'],
                    'type_stats': {},
                    'category_stats': {}
                }
            return {
                'total_scripts': 0,
                'active_scripts': 0,
                'inactive_scripts': 0,
                'type_stats': {},
                'category_stats': {}
            }
    
    def get_lead_by_email(self, email: str) -> Optional[Dict]:
        """Ottiene un lead per email"""
        if self.use_supabase:
            try:
                result = self.supabase.table('leads').select('*').eq('email', email).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                logger.error(f"❌ Errore get_lead_by_email Supabase: {e}")
                return None
        else:
            query = "SELECT * FROM leads WHERE email = ?"
            results = self.execute_query(query, (email,))
            return results[0] if results else None
    
    def create_lead_source(self, source_data: Dict) -> Optional[int]:
        """Crea una nuova fonte lead"""
        if self.use_supabase:
            try:
                result = self.supabase.table('lead_sources').insert(source_data).execute()
                return result.data[0]['id'] if result.data else None
            except Exception as e:
                logger.error(f"❌ Errore create_lead_source Supabase: {e}")
                return None
        else:
            query = "INSERT INTO lead_sources (name, description, is_active) VALUES (?, ?, ?)"
            cursor = self.execute_query(query, (
                source_data['name'],
                source_data.get('description', ''),
                source_data.get('is_active', True)
            ))
            return cursor.lastrowid if cursor else None
    
    # ==================== METODI GESTIONE GRUPPI LEAD ====================
    
    def get_lead_groups(self) -> List[Dict]:
        """Ottiene tutti i gruppi di lead attivi"""
        if self.use_supabase:
            try:
                result = self.supabase.table('lead_groups').select('*').eq('is_active', True).order('name').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_lead_groups Supabase: {e}")
                return []
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return []
    
    def get_lead_group_by_id(self, group_id: int) -> Optional[Dict]:
        """Ottiene un gruppo di lead per ID"""
        if self.use_supabase:
            try:
                result = self.supabase.table('lead_groups').select('*').eq('id', group_id).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                logger.error(f"❌ Errore get_lead_group_by_id Supabase: {e}")
                return None
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return None
    
    def create_lead_group(self, group_data: Dict) -> Optional[int]:
        """Crea un nuovo gruppo di lead"""
        if self.use_supabase:
            try:
                result = self.supabase.table('lead_groups').insert(group_data).execute()
                return result.data[0]['id'] if result.data else None
            except Exception as e:
                logger.error(f"❌ Errore create_lead_group Supabase: {e}")
                return None
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return None
    
    def update_lead_group(self, group_id: int, group_data: Dict) -> bool:
        """Aggiorna un gruppo di lead"""
        if self.use_supabase:
            try:
                result = self.supabase.table('lead_groups').update(group_data).eq('id', group_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore update_lead_group Supabase: {e}")
                return False
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return False
    
    def delete_lead_group(self, group_id: int) -> bool:
        """Elimina un gruppo di lead (soft delete)"""
        if self.use_supabase:
            try:
                result = self.supabase.table('lead_groups').update({'is_active': False}).eq('id', group_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore delete_lead_group Supabase: {e}")
                return False
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return False
    
    def get_user_lead_groups(self, user_id: int) -> List[Dict]:
        """Ottiene i gruppi di lead di un utente. Se user_id=0, restituisce tutte le assegnazioni."""
        if self.use_supabase:
            try:
                if user_id == 0:
                    # Caso speciale: restituisce tutte le assegnazioni
                    result = self.supabase.table('user_lead_groups').select('*, lead_groups(*)').execute()
                else:
                    # Caso normale: restituisce solo le assegnazioni dell'utente specifico
                    result = self.supabase.table('user_lead_groups').select('*, lead_groups(*)').eq('user_id', user_id).execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_user_lead_groups Supabase: {e}")
                return []
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return []
    
    def assign_user_to_group(self, user_id: int, group_id: int, can_manage: bool = False) -> bool:
        """Assegna un utente a un gruppo di lead"""
        if self.use_supabase:
            try:
                assignment_data = {
                    'user_id': user_id,
                    'group_id': group_id,
                    'can_manage': can_manage
                }
                result = self.supabase.table('user_lead_groups').insert(assignment_data).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore assign_user_to_group Supabase: {e}")
                return False
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return False
    
    def remove_user_from_group(self, user_id: int, group_id: int) -> bool:
        """Rimuove un utente da un gruppo di lead"""
        if self.use_supabase:
            try:
                result = self.supabase.table('user_lead_groups').delete().eq('user_id', user_id).eq('group_id', group_id).execute()
                return True
            except Exception as e:
                logger.error(f"❌ Errore remove_user_from_group Supabase: {e}")
                return False
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return False
    
    def get_leads_by_group(self, group_id: int, user_id: Optional[int] = None) -> List[Dict]:
        """Ottiene i lead di un gruppo specifico"""
        if self.use_supabase:
            try:
                query = self.supabase.table('leads').select('*').eq('group_id', group_id)
                if user_id:
                    # Verifica che l'utente abbia accesso al gruppo
                    user_groups = self.get_user_lead_groups(user_id)
                    user_group_ids = [ug['group_id'] for ug in user_groups]
                    if group_id not in user_group_ids:
                        return []
                result = query.execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_leads_by_group Supabase: {e}")
                return []
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return []
    
    def get_leads_for_user_groups(self, user_id: int) -> List[Dict]:
        """Ottiene tutti i lead accessibili da un utente in base ai suoi gruppi"""
        if self.use_supabase:
            try:
                # Ottieni i gruppi dell'utente
                user_groups = self.get_user_lead_groups(user_id)
                if not user_groups:
                    return []
                
                group_ids = [ug['group_id'] for ug in user_groups]
                
                # Ottieni i lead di questi gruppi
                result = self.supabase.table('leads').select('*').in_('group_id', group_ids).limit(10000).execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_leads_for_user_groups Supabase: {e}")
                return []
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return []
    
    def get_tasks_for_user_groups(self, user_id: int, filters: Dict = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Ottiene tutti i task accessibili da un utente in base ai suoi gruppi di lead"""
        if self.use_supabase:
            try:
                # Ottieni i gruppi dell'utente
                user_groups = self.get_user_lead_groups(user_id)
                if not user_groups:
                    return []
                
                group_ids = [ug['group_id'] for ug in user_groups]
                
                # Ottieni i lead di questi gruppi
                leads_result = self.supabase.table('leads').select('id').in_('group_id', group_ids).execute()
                lead_ids = [lead['id'] for lead in leads_result.data]
                
                if not lead_ids:
                    return []
                
                # Ottieni i task collegati a questi lead
                query = self.supabase.table('tasks').select('*').in_('lead_id', lead_ids)
                
                # Applica filtri se forniti
                if filters:
                    if filters.get('state_id'):
                        query = query.eq('state_id', filters['state_id'])
                    if filters.get('task_type_id'):
                        query = query.eq('task_type_id', filters['task_type_id'])
                    if filters.get('priority_id'):
                        query = query.eq('priority_id', filters['priority_id'])
                    if filters.get('assigned_to'):
                        query = query.eq('assigned_to', filters['assigned_to'])
                    
                    # Filtri per date
                    if filters.get('due_filter'):
                        due_filter = filters['due_filter']
                        today = datetime.now().date()
                        
                        if due_filter == "Scaduti":
                            query = query.lt('due_date', today.isoformat())
                        elif due_filter == "Oggi":
                            query = query.eq('due_date', today.isoformat())
                        elif due_filter == "Questa settimana":
                            from datetime import timedelta
                            week_end = today + timedelta(days=7)
                            query = query.gte('due_date', today.isoformat()).lte('due_date', week_end.isoformat())
                        elif due_filter == "Questo mese":
                            from datetime import timedelta
                            month_end = today + timedelta(days=30)
                            query = query.gte('due_date', today.isoformat()).lte('due_date', month_end.isoformat())
                        elif due_filter == "Prossimi 7 giorni":
                            from datetime import timedelta
                            week_end = today + timedelta(days=7)
                            query = query.gte('due_date', today.isoformat()).lte('due_date', week_end.isoformat())
                    
                    if filters.get('created_filter'):
                        created_filter = filters['created_filter']
                        today = datetime.now().date()
                        
                        if created_filter == "Oggi":
                            query = query.gte('created_at', today.isoformat())
                        elif created_filter == "Ieri":
                            from datetime import timedelta
                            yesterday = today - timedelta(days=1)
                            query = query.gte('created_at', yesterday.isoformat()).lt('created_at', today.isoformat())
                        elif created_filter == "Ultima settimana":
                            from datetime import timedelta
                            week_ago = today - timedelta(days=7)
                            query = query.gte('created_at', week_ago.isoformat())
                        elif created_filter == "Ultimo mese":
                            from datetime import timedelta
                            month_ago = today - timedelta(days=30)
                            query = query.gte('created_at', month_ago.isoformat())
                
                # Ordina e limita
                result = query.order('due_date', desc=True).range(offset, offset + limit - 1).execute()
                tasks = result.data
                
                # Aggiungi i dati di lookup per i task
                if tasks:
                    # Ottieni tutti gli stati dei task
                    state_ids = list(set([task.get('state_id') for task in tasks if task.get('state_id')]))
                    states = {}
                    if state_ids:
                        state_result = self.supabase.table('task_states').select('id,name').in_('id', state_ids).execute()
                        states = {state['id']: state['name'] for state in state_result.data}
                    
                    # Ottieni tutti i tipi di task
                    type_ids = list(set([task.get('task_type_id') for task in tasks if task.get('task_type_id')]))
                    types = {}
                    if type_ids:
                        type_result = self.supabase.table('task_types').select('id,name').in_('id', type_ids).execute()
                        types = {t['id']: t['name'] for t in type_result.data}
                    
                    # Ottieni tutte le priorità
                    priority_ids = list(set([task.get('priority_id') for task in tasks if task.get('priority_id')]))
                    priorities = {}
                    if priority_ids:
                        priority_result = self.supabase.table('lead_priorities').select('id,name').in_('id', priority_ids).execute()
                        priorities = {p['id']: p['name'] for p in priority_result.data}
                    
                    # Ottieni tutti gli utenti assegnati
                    user_ids = list(set([task.get('assigned_to') for task in tasks if task.get('assigned_to')]))
                    users = {}
                    if user_ids:
                        user_result = self.supabase.table('users').select('id,first_name,last_name').in_('id', user_ids).execute()
                        users = {u['id']: {'first_name': u.get('first_name', ''), 'last_name': u.get('last_name', '')} for u in user_result.data}
                    
                    # Ottieni tutti i lead collegati
                    lead_ids = list(set([task.get('lead_id') for task in tasks if task.get('lead_id')]))
                    leads = {}
                    if lead_ids:
                        lead_result = self.supabase.table('leads').select('id,name,phone').in_('id', lead_ids).execute()
                        leads = {l['id']: {'name': l.get('name', ''), 'phone': l.get('phone', '')} for l in lead_result.data}
                    
                    # Aggiungi i nomi ai task
                    for task in tasks:
                        task['state_name'] = states.get(task.get('state_id'), 'N/A')
                        task['type_name'] = types.get(task.get('task_type_id'), 'N/A')
                        task['priority_name'] = priorities.get(task.get('priority_id'), 'N/A')
                        
                        if task.get('assigned_to') and task['assigned_to'] in users:
                            user = users[task['assigned_to']]
                            task['assigned_first_name'] = user['first_name']
                            task['assigned_last_name'] = user['last_name']
                        else:
                            task['assigned_first_name'] = ''
                            task['assigned_last_name'] = ''
                        
                        if task.get('lead_id') and task['lead_id'] in leads:
                            lead = leads[task['lead_id']]
                            task['lead_name'] = lead['name']
                            task['lead_phone'] = lead['phone']
                        else:
                            task['lead_name'] = ''
                            task['lead_phone'] = ''
                
                return tasks
            except Exception as e:
                logger.error(f"❌ Errore get_tasks_for_user_groups Supabase: {e}")
                return []
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return []
    
    def reset_tasks(self, user_id: int = None, reset_all: bool = False) -> Dict:
        """
        Resetta le task con controlli di sicurezza
        
        Args:
            user_id: ID dell'utente che richiede il reset
            reset_all: Se True, resetta tutte le task (solo Admin)
        
        Returns:
            Dict con risultati del reset
        """
        if self.use_supabase:
            try:
                # Controllo sicurezza: solo Admin può resettare tutte le task
                if reset_all:
                    # Verifica che l'utente sia Admin
                    user_result = self.supabase.table('users').select('id,role_id').eq('id', user_id).execute()
                    if not user_result.data:
                        return {'success': False, 'message': 'Utente non trovato'}
                    
                    user_role = user_result.data[0].get('role_id')
                    if user_role != 1:  # 1 = Admin
                        return {'success': False, 'message': 'Solo Admin può resettare tutte le task'}
                    
                    # Reset di tutte le task
                    result = self.supabase.table('tasks').delete().neq('id', 0).execute()
                    deleted_count = len(result.data) if result.data else 0
                    
                    return {
                        'success': True, 
                        'message': f'Reset completato: {deleted_count} task eliminate',
                        'deleted_count': deleted_count
                    }
                
                else:
                    # Reset solo delle task dell'utente specifico
                    if not user_id:
                        return {'success': False, 'message': 'ID utente richiesto per reset parziale'}
                    
                    # Ottieni le task dell'utente
                    user_tasks = self.supabase.table('tasks').select('id').eq('assigned_to', user_id).execute()
                    task_ids = [task['id'] for task in user_tasks.data]
                    
                    if not task_ids:
                        return {'success': True, 'message': 'Nessuna task trovata per questo utente', 'deleted_count': 0}
                    
                    # Elimina le task dell'utente
                    result = self.supabase.table('tasks').delete().in_('id', task_ids).execute()
                    deleted_count = len(result.data) if result.data else 0
                    
                    return {
                        'success': True, 
                        'message': f'Reset completato: {deleted_count} task eliminate per utente {user_id}',
                        'deleted_count': deleted_count
                    }
                    
            except Exception as e:
                logger.error(f"❌ Errore reset_tasks Supabase: {e}")
                return {'success': False, 'message': f'Errore durante il reset: {str(e)}'}
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return {'success': False, 'message': 'SQLite non supportato per produzione'}
    
    def assign_lead_to_group(self, lead_id: int, group_id: int) -> bool:
        """Assegna un lead a un gruppo"""
        if self.use_supabase:
            try:
                result = self.supabase.table('leads').update({'group_id': group_id}).eq('id', lead_id).execute()
                return len(result.data) > 0
            except Exception as e:
                logger.error(f"❌ Errore assign_lead_to_group Supabase: {e}")
                return False
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return False
    
    def get_group_statistics(self, group_id: int) -> Dict:
        """Ottiene statistiche per un gruppo di lead"""
        if self.use_supabase:
            try:
                # Conta lead per stato nel gruppo
                leads_result = self.supabase.table('leads').select('state_id').eq('group_id', group_id).execute()
                leads = leads_result.data
                
                # Conta utenti nel gruppo
                users_result = self.supabase.table('user_lead_groups').select('user_id').eq('group_id', group_id).execute()
                users = users_result.data
                
                return {
                    'total_leads': len(leads),
                    'total_users': len(users),
                    'leads_by_state': {},
                    'leads_by_category': {},
                    'leads_by_priority': {}
                }
            except Exception as e:
                logger.error(f"❌ Errore get_group_statistics Supabase: {e}")
                return {}
        else:
            logger.warning("⚠️ SQLite non supportato per produzione. Usa Supabase.")
            return {}

    def create_lead_category(self, category_data: Dict) -> Optional[int]:
        """Crea una nuova categoria lead"""
        if self.use_supabase:
            try:
                result = self.supabase.table('lead_categories').insert(category_data).execute()
                return result.data[0]['id'] if result.data else None
            except Exception as e:
                logger.error(f"❌ Errore create_lead_category Supabase: {e}")
                return None
        else:
            query = "INSERT INTO lead_categories (name, color, description) VALUES (?, ?, ?)"
            cursor = self.execute_query(query, (
                category_data['name'],
                category_data.get('color', '#2E86AB'),
                category_data.get('description', '')
            ))
            return cursor.lastrowid if cursor else None
    
    def get_lead_priorities(self) -> List[Dict]:
        """Ottiene le priorità dei lead"""
        if self.use_supabase:
            try:
                result = self.supabase.table('lead_priorities').select('*').execute()
                return result.data
            except Exception as e:
                logger.error(f"❌ Errore get_lead_priorities Supabase: {e}")
                return []
        else:
            return self.execute_query("SELECT * FROM lead_priorities ORDER BY id")
    

# Test della classe
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Test connessione
    print("✅ Test connessione database...")
    users = db.get_all_users()
    print(f"👥 Utenti trovati: {len(users)}")
    
    # Test statistiche
    print("📊 Test statistiche...")
    lead_stats = db.get_lead_stats()
    print(f"📈 Stati lead: {len(lead_stats['leads_by_state'])}")
    
    # Test broker links (se la tabella esiste)
    print("🔗 Test broker links...")
    try:
        broker_stats = db.get_broker_links_stats()
        print(f"📊 Statistiche broker: {broker_stats}")
    except Exception as e:
        print(f"⚠️ Tabella broker_links non ancora creata: {e}")
    
    print("✅ Database Manager testato con successo!")
