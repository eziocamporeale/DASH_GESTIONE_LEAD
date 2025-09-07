#!/usr/bin/env python3
"""
Core AI Assistant - Integrazione DeepSeek API
Gestisce le chiamate API e la logica base dell'assistente AI
Creato da Ezio Camporeale
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import streamlit as st
from pathlib import Path
import sys

# Aggiungi il percorso della directory principale
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

from config import (
    DEEPSEEK_API_KEY, 
    DEEPSEEK_API_URL, 
    DEEPSEEK_MODEL,
    AI_ASSISTANT_CONFIG,
    AI_PROMPTS
)

class AIAssistant:
    """
    Classe principale per l'integrazione con DeepSeek API
    Gestisce le chiamate API, cache e gestione errori
    """
    
    def __init__(self):
        """Inizializza l'assistente AI con configurazione DeepSeek"""
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = DEEPSEEK_API_URL
        self.model = DEEPSEEK_MODEL
        self.config = AI_ASSISTANT_CONFIG
        
        # Cache per le risposte (in memoria per questa sessione)
        self.cache = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def _make_api_call(self, prompt: str, system_message: str = None) -> Optional[str]:
        """
        Effettua una chiamata all'API DeepSeek
        
        Args:
            prompt: Il prompt da inviare all'AI
            system_message: Messaggio di sistema opzionale
            
        Returns:
            Risposta dell'AI o None in caso di errore
        """
        try:
            # Prepara i messaggi
            messages = []
            
            if system_message:
                messages.append({
                    "role": "system",
                    "content": system_message
                })
            
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            # Headers per l'API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Payload per la richiesta
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.config['max_tokens'],
                "temperature": self.config['temperature'],
                "stream": False
            }
            
            # Effettua la chiamata con retry
            for attempt in range(self.config['retry_attempts']):
                try:
                    response = requests.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=self.config['timeout']
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'choices' in data and len(data['choices']) > 0:
                            content = data['choices'][0]['message']['content']
                            self.logger.info(f"✅ Chiamata API DeepSeek riuscita (tentativo {attempt + 1})")
                            return content
                        else:
                            self.logger.error("❌ Risposta API senza contenuto valido")
                            return None
                    else:
                        self.logger.warning(f"⚠️ Errore API: {response.status_code} - {response.text}")
                        if attempt < self.config['retry_attempts'] - 1:
                            time.sleep(2 ** attempt)  # Backoff esponenziale
                            
                except requests.exceptions.Timeout:
                    self.logger.warning(f"⚠️ Timeout API (tentativo {attempt + 1}) - Timeout: {self.config['timeout']}s")
                    if attempt < self.config['retry_attempts'] - 1:
                        time.sleep(3 ** attempt)  # Backoff più lungo per timeout
                        
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"❌ Errore richiesta API: {e}")
                    if attempt < self.config['retry_attempts'] - 1:
                        time.sleep(2 ** attempt)
            
            self.logger.error("❌ Tutti i tentativi API falliti")
            return self._get_fallback_response(prompt_type)
            
        except Exception as e:
            self.logger.error(f"❌ Errore generico chiamata API: {e}")
            return self._get_fallback_response(prompt_type)
    
    def _get_fallback_response(self, prompt_type: str) -> str:
        """Risposta di fallback quando l'API non è disponibile"""
        fallback_responses = {
            'sales_script': """
**Script di Vendita (Modalità Offline)**

**Apertura:**
"Ciao [Nome], sono [Tuo Nome] di [Azienda]. Ho visto che sei interessato a [Prodotto/Servizio]. Posso dedicarti 5 minuti per spiegarti come possiamo aiutarti?"

**Presentazione Valore:**
"Il nostro [Prodotto/Servizio] ha aiutato aziende simili alla tua a [Beneficio specifico]. Ad esempio, [Cliente] ha ottenuto [Risultato concreto]."

**Gestione Obiezioni:**
"Capisco la tua preoccupazione su [Obiezione]. Molti nostri clienti avevano lo stesso dubbio, ma poi hanno scoperto che [Contro-argomentazione]."

**Chiusura:**
"Perfetto! Quando preferiresti iniziare? Possiamo fissare un appuntamento per [Data] o preferisci [Alternativa]?"

**Note:** Script generato in modalità offline. Per personalizzazioni avanzate, riprova quando la connessione AI è disponibile.
            """,
            'marketing_advice': """
**Consigli Marketing (Modalità Offline)**

**Analisi Generale:**
- Focus sui lead ad alta conversione
- Ottimizza i canali che generano più ROI
- Personalizza i messaggi per settore

**Raccomandazioni Immediate:**
1. Segmenta i lead per settore
2. Crea contenuti specifici per ogni segmento
3. Implementa follow-up automatizzati
4. Monitora le metriche di conversione

**Strategie a Lungo Termine:**
- Sviluppa contenuti educativi
- Costruisci relazioni con influencer del settore
- Investi in strumenti di marketing automation

**Note:** Consigli generati in modalità offline. Per analisi personalizzate, riprova quando la connessione AI è disponibile.
            """,
            'lead_analysis': """
**Analisi Lead (Modalità Offline)**

**Score Qualità:** 75/100 (Stima)

**Probabilità Conversione:** Media-Alta

**Approccio Consigliato:**
1. Contatto telefonico entro 24h
2. Presentazione personalizzata
3. Focus sui benefici specifici
4. Follow-up regolare

**Timing Ottimale:**
- Chiamata: Mattina (9-11) o Pomeriggio (15-17)
- Email: Martedì-Giovedì, ore 10-14

**Red Flags da Monitorare:**
- Mancanza di budget definito
- Processo decisionale lungo
- Competitor già coinvolti

**Note:** Analisi generata in modalità offline. Per insights dettagliati, riprova quando la connessione AI è disponibile.
            """
        }
        
        return fallback_responses.get(prompt_type, "Risposta non disponibile in modalità offline.")
    
    def _get_cache_key(self, prompt_type: str, data_hash: str) -> str:
        """Genera una chiave di cache per la risposta"""
        return f"{prompt_type}_{data_hash}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se la cache è ancora valida"""
        if not self.config['cache_responses']:
            return False
            
        if cache_key not in self.cache:
            return False
            
        cache_time = self.cache[cache_key]['timestamp']
        cache_duration = timedelta(hours=self.config['cache_duration_hours'])
        
        return datetime.now() - cache_time < cache_duration
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Recupera una risposta dalla cache"""
        if self._is_cache_valid(cache_key):
            self.logger.info("📋 Risposta recuperata dalla cache")
            return self.cache[cache_key]['response']
        return None
    
    def _cache_response(self, cache_key: str, response: str):
        """Salva una risposta nella cache"""
        if self.config['cache_responses']:
            self.cache[cache_key] = {
                'response': response,
                'timestamp': datetime.now()
            }
            self.logger.info("💾 Risposta salvata in cache")
    
    def generate_response(self, prompt_type: str, data: Dict[str, Any], 
                         custom_prompt: str = None) -> Optional[str]:
        """
        Genera una risposta AI basata sul tipo di prompt e i dati forniti
        
        Args:
            prompt_type: Tipo di prompt (sales_script, marketing_advice, lead_analysis)
            data: Dati da utilizzare per personalizzare il prompt
            custom_prompt: Prompt personalizzato opzionale
            
        Returns:
            Risposta dell'AI o None in caso di errore
        """
        try:
            # Genera chiave cache basata sui dati
            data_str = json.dumps(data, sort_keys=True)
            data_hash = str(hash(data_str))
            cache_key = self._get_cache_key(prompt_type, data_hash)
            
            # Controlla cache
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return cached_response
            
            # Prepara il prompt
            if custom_prompt:
                prompt = custom_prompt
            elif prompt_type in AI_PROMPTS:
                prompt_template = AI_PROMPTS[prompt_type]
                prompt = prompt_template.format(**data)
            else:
                self.logger.error(f"❌ Tipo prompt non riconosciuto: {prompt_type}")
                return None
            
            # Effettua chiamata API
            response = self._make_api_call(prompt)
            
            if response:
                # Salva in cache
                self._cache_response(cache_key, response)
                return response
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Errore generazione risposta: {e}")
            return None
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Recupera la cronologia delle conversazioni (per implementazioni future)
        """
        # Implementazione futura per persistenza conversazioni
        return []
    
    def clear_cache(self):
        """Pulisce la cache delle risposte"""
        self.cache.clear()
        self.logger.info("🗑️ Cache AI pulita")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Restituisce statistiche sulla cache"""
        total_cached = len(self.cache)
        valid_cached = sum(1 for key in self.cache.keys() if self._is_cache_valid(key))
        
        return {
            'total_cached': total_cached,
            'valid_cached': valid_cached,
            'cache_hit_rate': valid_cached / max(total_cached, 1) * 100,
            'cache_enabled': self.config['cache_responses']
        }
    
    def test_connection(self) -> bool:
        """
        Testa la connessione con l'API DeepSeek
        
        Returns:
            True se la connessione funziona, False altrimenti
        """
        try:
            test_prompt = "Rispondi semplicemente 'OK' per confermare la connessione."
            response = self._make_api_call(test_prompt)
            
            if response and "OK" in response.upper():
                self.logger.info("✅ Connessione DeepSeek API funzionante")
                return True
            else:
                self.logger.error("❌ Connessione DeepSeek API non funzionante")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Errore test connessione: {e}")
            return False

# Funzione di utilità per inizializzare l'assistente AI
def get_ai_assistant() -> AIAssistant:
    """
    Factory function per ottenere un'istanza dell'assistente AI
    Utilizza il pattern singleton per evitare multiple istanze
    """
    if 'ai_assistant' not in st.session_state:
        st.session_state.ai_assistant = AIAssistant()
    
    return st.session_state.ai_assistant
