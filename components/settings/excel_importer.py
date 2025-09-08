#!/usr/bin/env python3
"""
Modulo Importazione Excel per DASH_GESTIONE_LEAD
Gestisce l'importazione di clienti da file Excel
Creato da Ezio Camporeale
"""

import streamlit as st
import pandas as pd
import io
from typing import Dict, List, Optional, Tuple
import sys
from pathlib import Path
from datetime import datetime
import traceback

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from database.database_manager import DatabaseManager
from components.auth.auth_manager import get_current_user
from config import CUSTOM_COLORS

class ExcelImporter:
    """Gestisce l'importazione di clienti da file Excel"""
    
    def __init__(self):
        """Inizializza l'importatore Excel"""
        self.db = DatabaseManager()
        self.current_user = get_current_user()
        
        # Mapping dei campi Excel ai campi del database
        self.field_mapping = {
            'nome': 'first_name',
            'cognome': 'last_name', 
            'email': 'email',
            'telefono': 'phone',
            'azienda': 'company',
            'posizione': 'position',
            'fonte': 'source_id',
            'categoria': 'category_id',
            'stato': 'state_id',
            'priorita': 'priority_id',
            'budget': 'budget',
            'data_chiusura': 'expected_close_date',
            'note': 'notes'
        }
        
        # Campi obbligatori
        self.required_fields = ['first_name', 'last_name']
        
        # Campi opzionali con valori di default
        self.default_values = {
            'state_id': 1,  # Nuovo
            'priority_id': 2,  # Media
            'created_by': self.current_user['user_id'] if self.current_user else 1
        }
    
    def render_import_page(self):
        """Renderizza la pagina di importazione Excel"""
        
        st.markdown("### 📊 Importazione Clienti da Excel")
        st.markdown("Importa i tuoi clienti da un file Excel")
        
        # Informazioni sul formato richiesto
        with st.expander("📋 Formato File Excel Richiesto", expanded=False):
            st.markdown("""
            **Il file Excel deve contenere le seguenti colonne:**
            
            | Colonna | Obbligatorio | Descrizione | Esempio |
            |---------|--------------|-------------|---------|
            | Nome | ✅ | Nome del cliente | Mario |
            | Cognome | ✅ | Cognome del cliente | Rossi |
            | Email | ❌ | Email del cliente | mario.rossi@email.com |
            | Telefono | ❌ | Numero di telefono | +39 123 456 7890 |
            | Azienda | ❌ | Nome dell'azienda | Azienda SRL |
            | Posizione | ❌ | Ruolo/Posizione | CEO |
            | Fonte | ❌ | Fonte del lead | Website, Telefono, etc. |
            | Categoria | ❌ | Categoria del lead | A, B, C |
            | Stato | ❌ | Stato del lead | Nuovo, Qualificato, etc. |
            | Priorità | ❌ | Priorità del lead | Bassa, Media, Alta |
            | Budget | ❌ | Budget stimato | 10000 |
            | Data Chiusura | ❌ | Data chiusura prevista | 2024-12-31 |
            | Note | ❌ | Note aggiuntive | Cliente interessato |
            
            **Note importanti:**
            - Le colonne possono essere in qualsiasi ordine
            - I nomi delle colonne sono case-insensitive
            - Le date devono essere nel formato YYYY-MM-DD
            - I valori numerici devono essere senza simboli di valuta
            """)
        
        # Upload del file
        uploaded_file = st.file_uploader(
            "📁 Carica File Excel",
            type=['xlsx', 'xls'],
            help="Seleziona un file Excel con i dati dei clienti"
        )
        
        if uploaded_file is not None:
            try:
                # Legge il file Excel
                df = self.read_excel_file(uploaded_file)
                
                if df is not None and not df.empty:
                    # Mostra anteprima dei dati
                    st.markdown("#### 👀 Anteprima Dati")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    # Mapping delle colonne
                    st.markdown("#### 🔗 Mapping Colonne")
                    column_mapping = self.render_column_mapping(df)
                    
                    if column_mapping:
                        # Validazione dati
                        st.markdown("#### ✅ Validazione Dati")
                        validation_result = self.validate_data(df, column_mapping)
                        
                        if validation_result['valid']:
                            # Opzioni di importazione
                            st.markdown("#### ⚙️ Opzioni Importazione")
                            import_options = self.render_import_options()
                            
                            # Pulsante di importazione
                            if st.button("🚀 Importa Clienti", type="primary", use_container_width=True):
                                self.import_data(df, column_mapping, import_options)
                        else:
                            st.error("❌ Dati non validi. Correggi gli errori prima di procedere.")
                            self.show_validation_errors(validation_result['errors'])
                
            except Exception as e:
                st.error(f"❌ Errore durante la lettura del file: {str(e)}")
                st.code(traceback.format_exc())
    
    def read_excel_file(self, uploaded_file) -> Optional[pd.DataFrame]:
        """Legge il file Excel caricato"""
        try:
            # Legge il file Excel
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            # Rimuove righe completamente vuote
            df = df.dropna(how='all')
            
            # Pulisce i nomi delle colonne
            df.columns = df.columns.str.strip().str.lower()
            
            st.success(f"✅ File caricato con successo! Trovate {len(df)} righe.")
            return df
            
        except Exception as e:
            st.error(f"❌ Errore durante la lettura del file Excel: {str(e)}")
            return None
    
    def render_column_mapping(self, df: pd.DataFrame) -> Optional[Dict]:
        """Renderizza l'interfaccia per il mapping delle colonne"""
        
        st.markdown("**Mappa le colonne del file Excel ai campi del database:**")
        
        column_mapping = {}
        excel_columns = df.columns.tolist()
        
        # Crea due colonne per il layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Colonne Excel:**")
            for col in excel_columns[:len(excel_columns)//2 + 1]:
                st.write(f"• {col}")
        
        with col2:
            st.markdown("**🗄️ Colonne Excel:**")
            for col in excel_columns[len(excel_columns)//2 + 1:]:
                st.write(f"• {col}")
        
        # Mapping automatico basato sui nomi delle colonne
        auto_mapping = self.auto_map_columns(excel_columns)
        
        # Mostra il mapping automatico
        st.markdown("**🔗 Mapping Automatico:**")
        mapping_df = pd.DataFrame([
            {"Colonna Excel": excel_col, "Campo Database": db_field, "Obbligatorio": "✅" if db_field in self.required_fields else "❌"}
            for excel_col, db_field in auto_mapping.items()
        ])
        st.dataframe(mapping_df, use_container_width=True)
        
        # Permette modifiche al mapping
        st.markdown("**✏️ Modifica Mapping (opzionale):**")
        
        for excel_col, db_field in auto_mapping.items():
            db_field_options = [""] + list(self.field_mapping.values())
            current_index = db_field_options.index(db_field) if db_field in db_field_options else 0
            
            new_field = st.selectbox(
                f"Colonna '{excel_col}' →",
                options=db_field_options,
                index=current_index,
                key=f"mapping_{excel_col}"
            )
            
            if new_field:
                column_mapping[excel_col] = new_field
        
        return column_mapping if column_mapping else auto_mapping
    
    def auto_map_columns(self, excel_columns: List[str]) -> Dict[str, str]:
        """Mappa automaticamente le colonne Excel ai campi del database"""
        
        mapping = {}
        
        # Mapping diretto per nomi comuni
        direct_mapping = {
            'nome': 'first_name',
            'name': 'first_name',
            'first_name': 'first_name',
            'cognome': 'last_name',
            'surname': 'last_name',
            'last_name': 'last_name',
            'email': 'email',
            'e-mail': 'email',
            'mail': 'email',
            'telefono': 'phone',
            'phone': 'phone',
            'tel': 'phone',
            'telephone': 'phone',
            'azienda': 'company',
            'company': 'company',
            'societa': 'company',
            'posizione': 'position',
            'position': 'position',
            'ruolo': 'position',
            'role': 'position',
            'fonte': 'source_id',
            'source': 'source_id',
            'origine': 'source_id',
            'categoria': 'category_id',
            'category': 'category_id',
            'stato': 'state_id',
            'state': 'state_id',
            'status': 'state_id',
            'priorita': 'priority_id',
            'priority': 'priority_id',
            'budget': 'budget',
            'data_chiusura': 'expected_close_date',
            'close_date': 'expected_close_date',
            'data_chiusura': 'expected_close_date',
            'note': 'notes',
            'notes': 'notes',
            'commenti': 'notes'
        }
        
        for excel_col in excel_columns:
            excel_col_lower = excel_col.lower().strip()
            
            if excel_col_lower in direct_mapping:
                mapping[excel_col] = direct_mapping[excel_col_lower]
            else:
                # Prova a trovare corrispondenze parziali
                for key, value in direct_mapping.items():
                    if key in excel_col_lower or excel_col_lower in key:
                        mapping[excel_col] = value
                        break
        
        return mapping
    
    def validate_data(self, df: pd.DataFrame, column_mapping: Dict) -> Dict:
        """Valida i dati prima dell'importazione"""
        
        errors = []
        warnings = []
        
        # Verifica campi obbligatori
        for required_field in self.required_fields:
            mapped_column = None
            for excel_col, db_field in column_mapping.items():
                if db_field == required_field:
                    mapped_column = excel_col
                    break
            
            if not mapped_column:
                errors.append(f"Campo obbligatorio '{required_field}' non mappato")
            else:
                # Verifica valori vuoti
                empty_count = df[mapped_column].isna().sum()
                if empty_count > 0:
                    errors.append(f"Colonna '{mapped_column}' ha {empty_count} valori vuoti")
        
        # Verifica email valide
        email_column = None
        for excel_col, db_field in column_mapping.items():
            if db_field == 'email':
                email_column = excel_col
                break
        
        if email_column:
            invalid_emails = 0
            for email in df[email_column].dropna():
                if '@' not in str(email) or '.' not in str(email):
                    invalid_emails += 1
            
            if invalid_emails > 0:
                warnings.append(f"Trovate {invalid_emails} email non valide")
        
        # Verifica duplicati email
        if email_column:
            duplicate_emails = df[email_column].duplicated().sum()
            if duplicate_emails > 0:
                warnings.append(f"Trovate {duplicate_emails} email duplicate")
        
        # Verifica date
        date_column = None
        for excel_col, db_field in column_mapping.items():
            if db_field == 'expected_close_date':
                date_column = excel_col
                break
        
        if date_column:
            invalid_dates = 0
            for date_val in df[date_column].dropna():
                try:
                    pd.to_datetime(date_val)
                except:
                    invalid_dates += 1
            
            if invalid_dates > 0:
                warnings.append(f"Trovate {invalid_dates} date non valide")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def show_validation_errors(self, errors: List[str]):
        """Mostra gli errori di validazione"""
        st.error("**❌ Errori di Validazione:**")
        for error in errors:
            st.write(f"• {error}")
    
    def render_import_options(self) -> Dict:
        """Renderizza le opzioni di importazione"""
        
        options = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            options['skip_duplicates'] = st.checkbox(
                "Salta Duplicati",
                value=True,
                help="Salta i record con email già esistenti"
            )
            
            options['update_existing'] = st.checkbox(
                "Aggiorna Esistenti",
                value=False,
                help="Aggiorna i record esistenti invece di saltarli"
            )
        
        with col2:
            options['create_tasks'] = st.checkbox(
                "Crea Task Automatici",
                value=True,
                help="Crea task automatici per i nuovi lead"
            )
            
            options['send_notifications'] = st.checkbox(
                "Invia Notifiche",
                value=False,
                help="Invia notifiche per i nuovi lead importati"
            )
        
        return options
    
    def import_data(self, df: pd.DataFrame, column_mapping: Dict, import_options: Dict):
        """Importa i dati nel database"""
        
        try:
            # Inizializza contatori
            imported_count = 0
            skipped_count = 0
            updated_count = 0
            error_count = 0
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_rows = len(df)
            
            for index, row in df.iterrows():
                try:
                    # Aggiorna progress bar
                    progress = (index + 1) / total_rows
                    progress_bar.progress(progress)
                    status_text.text(f"Importando riga {index + 1} di {total_rows}")
                    
                    # Prepara i dati del lead
                    lead_data = self.prepare_lead_data(row, column_mapping)
                    
                    if lead_data:
                        # Verifica duplicati se richiesto
                        if import_options.get('skip_duplicates', True) and lead_data.get('email'):
                            existing_lead = self.db.get_lead_by_email(lead_data['email'])
                            
                            if existing_lead:
                                if import_options.get('update_existing', False):
                                    # Aggiorna lead esistente
                                    self.db.update_lead(existing_lead['id'], lead_data)
                                    updated_count += 1
                                else:
                                    # Salta duplicato
                                    skipped_count += 1
                                continue
                        
                        # Crea nuovo lead
                        lead_id = self.db.create_lead(lead_data)
                        
                        if lead_id:
                            imported_count += 1
                            
                            # Crea task automatico se richiesto
                            if import_options.get('create_tasks', True):
                                self.create_automatic_task(lead_id, lead_data)
                            
                            # Invia notifica se richiesto
                            if import_options.get('send_notifications', False):
                                self.send_import_notification(lead_id, lead_data)
                        else:
                            error_count += 1
                    else:
                        error_count += 1
                
                except Exception as e:
                    error_count += 1
                    st.warning(f"Errore alla riga {index + 1}: {str(e)}")
            
            # Mostra risultati finali
            progress_bar.progress(1.0)
            status_text.text("Importazione completata!")
            
            # Risultati
            st.success("🎉 Importazione completata!")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("✅ Importati", imported_count)
            
            with col2:
                st.metric("🔄 Aggiornati", updated_count)
            
            with col3:
                st.metric("⏭️ Saltati", skipped_count)
            
            with col4:
                st.metric("❌ Errori", error_count)
            
            # Log dell'attività
            self.log_import_activity(imported_count, updated_count, skipped_count, error_count)
            
        except Exception as e:
            st.error(f"❌ Errore durante l'importazione: {str(e)}")
            st.code(traceback.format_exc())
    
    def prepare_lead_data(self, row: pd.Series, column_mapping: Dict) -> Optional[Dict]:
        """Prepara i dati del lead per l'inserimento nel database"""
        
        lead_data = {}
        
        try:
            # Mappa i dati dalle colonne Excel ai campi del database
            for excel_col, db_field in column_mapping.items():
                if excel_col in row.index:
                    value = row[excel_col]
                    
                    # Gestisce valori NaN e vuoti
                    if pd.isna(value) or str(value).strip() == '' or str(value).strip() == 'nan':
                        continue
                    
                    # Converte il valore in base al tipo di campo
                    if db_field in ['source_id', 'category_id', 'state_id', 'priority_id']:
                        # Per i campi ID, controlla se è già un numero
                        try:
                            # Se è già un numero, usalo direttamente
                            id_value = int(value)
                            if id_value > 0:  # Solo valori positivi
                                lead_data[db_field] = id_value
                        except (ValueError, TypeError):
                            # Se non è un numero, cerca per nome
                            id_value = self.get_id_by_name(db_field, str(value))
                            if id_value is not None:
                                lead_data[db_field] = id_value
                    elif db_field == 'expected_close_date':
                        # Converte la data
                        try:
                            date_str = pd.to_datetime(value).strftime('%Y-%m-%d')
                            if date_str and date_str != 'NaT':
                                lead_data[db_field] = date_str
                        except:
                            pass
                    elif db_field == 'budget':
                        # Converte il budget
                        try:
                            budget_value = float(str(value).replace(',', '.').replace('€', '').replace('$', '').strip())
                            if budget_value > 0:  # Solo valori positivi
                                lead_data[db_field] = budget_value
                        except:
                            pass
                    else:
                        # Campo di testo normale
                        text_value = str(value).strip()
                        if text_value and text_value != 'nan':
                            lead_data[db_field] = text_value
            
            # Aggiunge valori di default
            for field, default_value in self.default_values.items():
                if field not in lead_data:
                    lead_data[field] = default_value
            
            # Validazione finale - verifica campi obbligatori
            if not lead_data.get('first_name') or not lead_data.get('last_name'):
                return None
            
            return lead_data
            
        except Exception as e:
            st.warning(f"Errore nella preparazione dei dati: {str(e)}")
            return None
    
    def get_id_by_name(self, field_type: str, name: str) -> Optional[int]:
        """Ottiene l'ID di un campo per nome"""
        
        try:
            if field_type == 'source_id':
                sources = self.db.get_lead_sources()
                for source in sources:
                    if source['name'].lower() == name.lower():
                        return source['id']
                # Crea nuova fonte se non esiste
                return self.db.create_lead_source({'name': name, 'description': f'Importata da Excel - {datetime.now()}'})
            
            elif field_type == 'category_id':
                categories = self.db.get_lead_categories()
                for category in categories:
                    if category['name'].lower() == name.lower():
                        return category['id']
                # Crea nuova categoria se non esiste
                return self.db.create_lead_category({'name': name, 'color': '#2E86AB', 'description': f'Importata da Excel - {datetime.now()}'})
            
            elif field_type == 'state_id':
                states = self.db.get_lead_states()
                for state in states:
                    if state['name'].lower() == name.lower():
                        return state['id']
                # Usa stato di default se non trovato
                return 1
            
            elif field_type == 'priority_id':
                priorities = self.db.get_lead_priorities()
                for priority in priorities:
                    if priority['name'].lower() == name.lower():
                        return priority['id']
                # Usa priorità di default se non trovata
                return 2
            
        except Exception as e:
            st.warning(f"Errore nel recupero dell'ID per {field_type}: {str(e)}")
        
        return None
    
    def create_automatic_task(self, lead_id: int, lead_data: Dict):
        """Crea un task automatico per il lead importato"""
        
        try:
            # Assicurati che i valori siano del tipo corretto
            priority_id = lead_data.get('priority_id', 2)
            if isinstance(priority_id, str):
                # Gestisce casi speciali come "true", "false", etc.
                if priority_id.lower() in ['true', 'false']:
                    priority_id = 2  # Default
                else:
                    try:
                        priority_id = int(priority_id)
                    except (ValueError, TypeError):
                        priority_id = 2
            
            assigned_to = lead_data.get('assigned_to')
            if assigned_to and isinstance(assigned_to, str):
                # Gestisce casi speciali come "true", "false", etc.
                if assigned_to.lower() in ['true', 'false']:
                    assigned_to = None
                else:
                    try:
                        assigned_to = int(assigned_to)
                    except (ValueError, TypeError):
                        assigned_to = None
            
            task_data = {
                'title': f'Follow-up per {lead_data.get("first_name", "")} {lead_data.get("last_name", "")}',
                'description': f'Task automatico creato durante l\'importazione da Excel per il lead {lead_id}',
                'lead_id': lead_id,
                'task_type_id': 1,  # Follow-up
                'state_id': 1,  # Da fare
                'priority_id': priority_id,
                'assigned_to': assigned_to,
                'created_by': self.current_user['user_id'] if self.current_user else 1,
                'due_date': (datetime.now().replace(day=datetime.now().day + 1)).strftime('%Y-%m-%d')
            }
            
            self.db.create_task(task_data)
            
        except Exception as e:
            st.warning(f"Errore nella creazione del task automatico: {str(e)}")
    
    def send_import_notification(self, lead_id: int, lead_data: Dict):
        """Invia una notifica per il lead importato"""
        
        try:
            # Qui potresti implementare l'invio di notifiche
            # Per ora è solo un placeholder
            pass
            
        except Exception as e:
            st.warning(f"Errore nell'invio della notifica: {str(e)}")
    
    def log_import_activity(self, imported: int, updated: int, skipped: int, errors: int):
        """Registra l'attività di importazione"""
        
        try:
            activity_data = {
                'user_id': self.current_user['user_id'] if self.current_user else 1,
                'action': 'Excel Import',
                'entity_type': 'leads',
                'entity_id': None,
                'details': f'Importazione Excel completata: {imported} importati, {updated} aggiornati, {skipped} saltati, {errors} errori',
                'ip_address': None
            }
            
            self.db.log_activity(activity_data)
            
        except Exception as e:
            st.warning(f"Errore nel logging dell'attività: {str(e)}")

def render_excel_importer():
    """Wrapper per renderizzare l'importatore Excel"""
    importer = ExcelImporter()
    importer.render_import_page()
