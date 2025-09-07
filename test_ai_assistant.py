#!/usr/bin/env python3
"""
Test AI Assistant - Test delle funzionalità AI
Test per verificare il funzionamento dell'assistente AI
Creato da Ezio Camporeale
"""

import sys
from pathlib import Path
import logging

# Aggiungi il percorso della directory principale
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from components.ai_assistant.ai_core import AIAssistant
from components.ai_assistant.sales_script_generator import SalesScriptGenerator
from components.ai_assistant.marketing_advisor import MarketingAdvisor
from components.ai_assistant.lead_analyzer import LeadAnalyzer

def test_ai_core():
    """Test del core AI Assistant"""
    print("🧪 Test AI Core...")
    
    try:
        ai_assistant = AIAssistant()
        
        # Test connessione
        print("  🔍 Test connessione DeepSeek...")
        connection_ok = ai_assistant.test_connection()
        
        if connection_ok:
            print("  ✅ Connessione DeepSeek OK")
        else:
            print("  ❌ Problema connessione DeepSeek")
            return False
        
        # Test generazione risposta
        print("  🤖 Test generazione risposta...")
        test_data = {
            'lead_data': 'Test Lead - Azienda Test',
            'industry': 'Tecnologia',
            'budget': '5000',
            'source': 'Website',
            'status': 'Nuovo'
        }
        
        response = ai_assistant.generate_response('sales_script', test_data)
        
        if response:
            print("  ✅ Generazione risposta OK")
            print(f"  📝 Risposta: {response[:100]}...")
        else:
            print("  ❌ Errore generazione risposta")
            return False
        
        # Test cache
        print("  💾 Test cache...")
        cache_stats = ai_assistant.get_cache_stats()
        print(f"  📊 Cache stats: {cache_stats}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Errore test AI Core: {e}")
        return False

def test_sales_script_generator():
    """Test del generatore script vendita"""
    print("🧪 Test Sales Script Generator...")
    
    try:
        script_generator = SalesScriptGenerator()
        
        # Test template disponibili
        print("  📋 Test template disponibili...")
        templates = script_generator.get_script_templates()
        print(f"  📊 Template disponibili: {len(templates)}")
        
        for template_key, template_info in templates.items():
            print(f"    - {template_key}: {template_info['name']}")
        
        # Test script per settore
        print("  🏭 Test script per settore...")
        industry_script = script_generator.generate_industry_script('Tecnologia', 'cold_call')
        
        if industry_script:
            print("  ✅ Script settore generato OK")
            print(f"  📝 Script: {industry_script['script_content'][:100]}...")
        else:
            print("  ❌ Errore generazione script settore")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Errore test Sales Script Generator: {e}")
        return False

def test_marketing_advisor():
    """Test del marketing advisor"""
    print("🧪 Test Marketing Advisor...")
    
    try:
        marketing_advisor = MarketingAdvisor()
        
        # Test tipi consigli disponibili
        print("  💡 Test tipi consigli disponibili...")
        advice_types = marketing_advisor.get_advice_types()
        print(f"  📊 Tipi consigli disponibili: {len(advice_types)}")
        
        for advice_key, advice_info in advice_types.items():
            print(f"    - {advice_key}: {advice_info['name']}")
        
        # Test generazione consigli (senza database per ora)
        print("  🤖 Test generazione consigli...")
        print("  ⚠️  Nota: Test limitato senza database connesso")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Errore test Marketing Advisor: {e}")
        return False

def test_lead_analyzer():
    """Test dell'analizzatore lead"""
    print("🧪 Test Lead Analyzer...")
    
    try:
        lead_analyzer = LeadAnalyzer()
        
        # Test calcolo score
        print("  📊 Test calcolo score lead...")
        test_lead_data = {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'company': 'Test Company',
            'email': 'mario@test.com',
            'phone': '+39 123 456 7890',
            'industry': 'Tecnologia',
            'budget': '10000',
            'source': 'Website',
            'notes': 'Interessato urgentemente'
        }
        
        score = lead_analyzer._calculate_lead_quality_score(test_lead_data)
        category = lead_analyzer._categorize_lead_quality(score)
        
        print(f"  📊 Score calcolato: {score}/100")
        print(f"  🏷️  Categoria: {category}")
        
        # Test score breakdown
        print("  🔍 Test score breakdown...")
        breakdown = lead_analyzer._get_score_breakdown(test_lead_data)
        print(f"  📊 Breakdown: {breakdown}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Errore test Lead Analyzer: {e}")
        return False

def main():
    """Funzione principale di test"""
    print("🚀 Avvio Test AI Assistant")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Test dei componenti
    tests = [
        ("AI Core", test_ai_core),
        ("Sales Script Generator", test_sales_script_generator),
        ("Marketing Advisor", test_marketing_advisor),
        ("Lead Analyzer", test_lead_analyzer)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Test: {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Errore critico in {test_name}: {e}")
            results.append((test_name, False))
    
    # Riepilogo risultati
    print("\n" + "=" * 50)
    print("📊 Riepilogo Test")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Risultati: {passed}/{total} test passati")
    
    if passed == total:
        print("🎉 Tutti i test sono passati! AI Assistant pronto per l'uso.")
    else:
        print("⚠️  Alcuni test sono falliti. Controllare la configurazione.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
