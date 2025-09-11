"""
Componente Storage per DASH_GESTIONE_LEAD
Gestione file con permessi differenziati per Admin e utenti
Creato da Ezio Camporeale
"""

from .storage_manager import StorageManager
from .storage_ui import render_storage_wrapper

__all__ = ['StorageManager', 'render_storage_wrapper']

