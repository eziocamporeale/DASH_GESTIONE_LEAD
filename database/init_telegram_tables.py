#!/usr/bin/env python3
"""
📱 TELEGRAM DATABASE INIT - Dashboard Gestione Lead
Script per inizializzazione tabelle Telegram nel database
Creato da Ezio Camporeale
"""

import sqlite3
import os
from pathlib import Path
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_telegram_tables():
    """Inizializza le tabelle Telegram nel database"""
    try:
        # Percorso del database
        db_path = Path(__file__).parent / "database.db"
        
        # Leggi lo schema SQL
        schema_path = Path(__file__).parent / "telegram_schema.sql"
        
        if not schema_path.exists():
            logger.error(f"❌ File schema Telegram non trovato: {schema_path}")
            return False
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Connessione al database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Esegui lo schema
        cursor.executescript(schema_sql)
        
        # Commit e chiusura
        conn.commit()
        conn.close()
        
        logger.info("✅ Tabelle Telegram inizializzate con successo!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore inizializzazione tabelle Telegram: {e}")
        return False

def check_telegram_tables():
    """Verifica che le tabelle Telegram esistano"""
    try:
        db_path = Path(__file__).parent / "database.db"
        
        if not db_path.exists():
            logger.error("❌ Database non trovato")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Controlla le tabelle
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('telegram_config', 'notification_settings', 'notification_logs')
        """)
        
        tables = cursor.fetchall()
        conn.close()
        
        expected_tables = ['telegram_config', 'notification_settings', 'notification_logs']
        found_tables = [table[0] for table in tables]
        
        missing_tables = set(expected_tables) - set(found_tables)
        
        if missing_tables:
            logger.warning(f"⚠️ Tabelle Telegram mancanti: {missing_tables}")
            return False
        else:
            logger.info("✅ Tutte le tabelle Telegram presenti")
            return True
            
    except Exception as e:
        logger.error(f"❌ Errore verifica tabelle Telegram: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Inizializzazione tabelle Telegram per Dashboard Lead...")
    
    # Verifica tabelle esistenti
    if check_telegram_tables():
        print("✅ Tabelle Telegram già presenti")
    else:
        print("📋 Creazione tabelle Telegram...")
        if init_telegram_tables():
            print("✅ Tabelle Telegram create con successo!")
        else:
            print("❌ Errore nella creazione delle tabelle")
