#!/usr/bin/env python3
"""
Portal Builder per DASH_GESTIONE_LEAD
Costruttore per assemblare portali web completi
Creato da Ezio Camporeale
"""

import os
import zipfile
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json

from .template_engine import TemplateEngine
from .ai_content_generator import AIContentGenerator

class PortalBuilder:
    """Costruttore per assemblare portali web completi"""
    
    def __init__(self):
        """Inizializza il costruttore"""
        self.template_engine = TemplateEngine()
        self.ai_generator = AIContentGenerator()
        self.output_dir = Path(__file__).parent / "generated_portals"
        self.output_dir.mkdir(exist_ok=True)
    
    def build_portal(self, portal_data: Dict) -> Dict:
        """
        Costruisce un portale completo
        
        Args:
            portal_data: Dati del portale da costruire
            
        Returns:
            Dict con informazioni sul portale costruito
        """
        try:
            # Prepara i dati per la generazione
            portal_id = portal_data.get('id', f"portal_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            portal_name = portal_data.get('portal_name', 'Portale')
            portal_type = portal_data.get('portal_type', 'landing_page')
            sector = portal_data.get('sector', 'finanza')
            
            # Crea directory del portale
            portal_dir = self.output_dir / portal_id
            portal_dir.mkdir(exist_ok=True)
            
            # Genera contenuti AI se necessario
            enhanced_data = self.ai_generator.enhance_portal_data(portal_data)
            
            # Ottieni template
            template = self.template_engine.get_template(portal_type)
            if not template:
                raise ValueError(f"Template {portal_type} non trovato")
            
            # Genera file HTML
            html_files = self._generate_html_files(portal_type, enhanced_data, template)
            
            # Genera CSS
            css_content = self.template_engine.get_template_css(
                portal_type, 
                portal_data.get('color_scheme', 'Blu Professionale')
            )
            
            # Genera JavaScript
            js_content = self.template_engine.get_template_js(
                portal_type,
                {
                    'include_contact_form': portal_data.get('include_contact_form', True),
                    'include_analytics': portal_data.get('include_analytics', True),
                    'mobile_responsive': portal_data.get('mobile_responsive', True)
                }
            )
            
            # Salva i file
            self._save_portal_files(portal_dir, html_files, css_content, js_content, enhanced_data)
            
            # Genera ZIP per download
            zip_path = self._create_portal_zip(portal_dir, portal_name)
            
            # Genera anteprima
            preview_path = self._generate_preview(portal_dir, portal_name)
            
            return {
                'success': True,
                'portal_id': portal_id,
                'portal_dir': str(portal_dir),
                'zip_path': str(zip_path),
                'preview_path': str(preview_path),
                'files_generated': len(html_files) + 2,  # +2 per CSS e JS
                'template_used': portal_type,
                'enhanced_data': enhanced_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'portal_id': portal_id if 'portal_id' in locals() else None
            }
    
    def _generate_html_files(self, portal_type: str, data: Dict, template: Dict) -> Dict[str, str]:
        """Genera tutti i file HTML per il portale"""
        html_files = {}
        
        # Genera index.html principale
        html_files['index.html'] = self._generate_main_html(portal_type, data, template)
        
        # Genera file aggiuntivi se necessario
        if portal_type == 'business_website':
            html_files['about.html'] = self._generate_about_html(data)
            html_files['services.html'] = self._generate_services_html(data)
            html_files['contact.html'] = self._generate_contact_html(data)
        
        elif portal_type == 'ecommerce':
            html_files['products.html'] = self._generate_products_html(data)
            html_files['cart.html'] = self._generate_cart_html(data)
            html_files['checkout.html'] = self._generate_checkout_html(data)
        
        elif portal_type == 'portfolio':
            html_files['portfolio.html'] = self._generate_portfolio_html(data)
            html_files['about.html'] = self._generate_about_html(data)
        
        elif portal_type == 'blog':
            html_files['post.html'] = self._generate_post_html(data)
            html_files['category.html'] = self._generate_category_html(data)
        
        elif portal_type == 'dashboard':
            html_files['dashboard.html'] = self._generate_dashboard_html(data)
        
        elif portal_type == 'saas':
            html_files['login.html'] = self._generate_login_html(data)
            html_files['dashboard.html'] = self._generate_dashboard_html(data)
            html_files['pricing.html'] = self._generate_pricing_html(data)
        
        return html_files
    
    def _generate_main_html(self, portal_type: str, data: Dict, template: Dict) -> str:
        """Genera il file HTML principale"""
        
        # Genera le sezioni
        sections_html = ""
        for section in template.get('sections', []):
            section_html = self.template_engine.get_template_html(portal_type, section, data)
            sections_html += section_html + "\n"
        
        # Template HTML completo
        html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data.get('portal_name', 'Portale')} - {data.get('company_name', 'Azienda')}</title>
    <meta name="description" content="{data.get('business_goals', 'Portale professionale')}">
    <meta name="keywords" content="{data.get('sector', 'business')}, {data.get('target_audience', 'clienti')}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    
    <!-- CSS -->
    <link rel="stylesheet" href="style.css">
    
    <!-- Font Awesome per icone -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    {sections_html}
    
    <!-- JavaScript -->
    <script src="script.js"></script>
    
    <!-- Analytics -->
    {self._generate_analytics_code(data) if data.get('include_analytics', True) else ''}
</body>
</html>"""
        
        return html_content
    
    def _generate_about_html(self, data: Dict) -> str:
        """Genera pagina About"""
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chi Siamo - {data.get('company_name', 'Azienda')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="about.html" class="active">Chi Siamo</a></li>
                <li><a href="services.html">Servizi</a></li>
                <li><a href="contact.html">Contatti</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main-content">
        <section class="about-section">
            <div class="container">
                <h1>Chi Siamo</h1>
                <div class="about-content">
                    <div class="about-text">
                        <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
                        <p>{data.get('business_goals', 'Siamo un\'azienda dedicata a fornire soluzioni innovative e di qualità per i nostri clienti.')}</p>
                        <p>Il nostro team è composto da professionisti esperti nel settore {data.get('sector', 'business')}, pronti ad aiutarti a raggiungere i tuoi obiettivi.</p>
                    </div>
                    <div class="about-image">
                        <img src="https://via.placeholder.com/400x300?text=Team+Photo" alt="Il nostro team">
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {data.get('company_name', 'La Tua Azienda')}. Tutti i diritti riservati.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _generate_services_html(self, data: Dict) -> str:
        """Genera pagina Servizi"""
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Servizi - {data.get('company_name', 'Azienda')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="about.html">Chi Siamo</a></li>
                <li><a href="services.html" class="active">Servizi</a></li>
                <li><a href="contact.html">Contatti</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main-content">
        <section class="services-section">
            <div class="container">
                <h1>I Nostri Servizi</h1>
                <div class="services-grid">
                    <div class="service-card">
                        <div class="service-icon">🚀</div>
                        <h3>Consulenza Strategica</h3>
                        <p>Ti aiutiamo a definire la strategia migliore per il tuo business nel settore {data.get('sector', 'business')}.</p>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">💼</div>
                        <h3>Supporto Operativo</h3>
                        <p>Forniamo supporto completo per le operazioni quotidiane della tua azienda.</p>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">📈</div>
                        <h3>Crescita e Sviluppo</h3>
                        <p>Accompagniamo la crescita del tuo business con soluzioni innovative e scalabili.</p>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {data.get('company_name', 'La Tua Azienda')}. Tutti i diritti riservati.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _generate_contact_html(self, data: Dict) -> str:
        """Genera pagina Contatti"""
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contatti - {data.get('company_name', 'Azienda')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="about.html">Chi Siamo</a></li>
                <li><a href="services.html">Servizi</a></li>
                <li><a href="contact.html" class="active">Contatti</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main-content">
        <section class="contact-section">
            <div class="container">
                <h1>Contattaci</h1>
                <div class="contact-content">
                    <div class="contact-info">
                        <h2>Informazioni di Contatto</h2>
                        <div class="contact-item">
                            <i class="fas fa-envelope"></i>
                            <span>info@{data.get('company_name', 'azienda').lower().replace(' ', '')}.com</span>
                        </div>
                        <div class="contact-item">
                            <i class="fas fa-phone"></i>
                            <span>+39 123 456 7890</span>
                        </div>
                        <div class="contact-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>Via Roma 123, Milano, Italia</span>
                        </div>
                    </div>
                    
                    <div class="contact-form">
                        <h2>Invia un Messaggio</h2>
                        <form id="contactForm">
                            <div class="form-group">
                                <input type="text" name="name" placeholder="Nome" required>
                            </div>
                            <div class="form-group">
                                <input type="email" name="email" placeholder="Email" required>
                            </div>
                            <div class="form-group">
                                <input type="text" name="subject" placeholder="Oggetto" required>
                            </div>
                            <div class="form-group">
                                <textarea name="message" placeholder="Messaggio" required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">Invia Messaggio</button>
                        </form>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {data.get('company_name', 'La Tua Azienda')}. Tutti i diritti riservati.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _generate_products_html(self, data: Dict) -> str:
        """Genera pagina Prodotti per E-commerce"""
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prodotti - {data.get('company_name', 'Azienda')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="products.html" class="active">Prodotti</a></li>
                <li><a href="cart.html">Carrello</a></li>
                <li><a href="contact.html">Contatti</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main-content">
        <section class="products-section">
            <div class="container">
                <h1>I Nostri Prodotti</h1>
                <div class="products-grid">
                    <div class="product-card">
                        <img src="https://via.placeholder.com/300x200?text=Prodotto+1" alt="Prodotto 1">
                        <h3>Prodotto Premium</h3>
                        <p>Descrizione del prodotto premium</p>
                        <div class="product-price">€99.99</div>
                        <button class="btn btn-primary">Aggiungi al Carrello</button>
                    </div>
                    <div class="product-card">
                        <img src="https://via.placeholder.com/300x200?text=Prodotto+2" alt="Prodotto 2">
                        <h3>Prodotto Standard</h3>
                        <p>Descrizione del prodotto standard</p>
                        <div class="product-price">€49.99</div>
                        <button class="btn btn-primary">Aggiungi al Carrello</button>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {data.get('company_name', 'La Tua Azienda')}. Tutti i diritti riservati.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _generate_cart_html(self, data: Dict) -> str:
        """Genera pagina Carrello"""
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carrello - {data.get('company_name', 'Azienda')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="products.html">Prodotti</a></li>
                <li><a href="cart.html" class="active">Carrello</a></li>
                <li><a href="contact.html">Contatti</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main-content">
        <section class="cart-section">
            <div class="container">
                <h1>Il Tuo Carrello</h1>
                <div class="cart-content">
                    <div class="cart-items">
                        <p>Il carrello è vuoto</p>
                    </div>
                    <div class="cart-summary">
                        <h3>Riepilogo Ordine</h3>
                        <div class="summary-line">
                            <span>Totale:</span>
                            <span>€0.00</span>
                        </div>
                        <button class="btn btn-primary">Procedi al Checkout</button>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {data.get('company_name', 'La Tua Azienda')}. Tutti i diritti riservati.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _generate_checkout_html(self, data: Dict) -> str:
        """Genera pagina Checkout"""
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checkout - {data.get('company_name', 'Azienda')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
            </div>
        </nav>
    </header>
    
    <main class="main-content">
        <section class="checkout-section">
            <div class="container">
                <h1>Checkout</h1>
                <div class="checkout-content">
                    <div class="checkout-form">
                        <h2>Informazioni di Pagamento</h2>
                        <form id="checkoutForm">
                            <div class="form-group">
                                <input type="text" name="card_number" placeholder="Numero Carta" required>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <input type="text" name="expiry" placeholder="MM/AA" required>
                                </div>
                                <div class="form-group">
                                    <input type="text" name="cvv" placeholder="CVV" required>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary">Completa Ordine</button>
                        </form>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {data.get('company_name', 'La Tua Azienda')}. Tutti i diritti riservati.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _generate_portfolio_html(self, data: Dict) -> str:
        """Genera pagina Portfolio"""
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio - {data.get('company_name', 'Azienda')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="portfolio.html" class="active">Portfolio</a></li>
                <li><a href="about.html">Chi Siamo</a></li>
                <li><a href="contact.html">Contatti</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main-content">
        <section class="portfolio-section">
            <div class="container">
                <h1>Il Nostro Portfolio</h1>
                <div class="portfolio-grid">
                    <div class="portfolio-item">
                        <img src="https://via.placeholder.com/400x300?text=Progetto+1" alt="Progetto 1">
                        <div class="portfolio-overlay">
                            <h3>Progetto 1</h3>
                            <p>Descrizione del progetto</p>
                        </div>
                    </div>
                    <div class="portfolio-item">
                        <img src="https://via.placeholder.com/400x300?text=Progetto+2" alt="Progetto 2">
                        <div class="portfolio-overlay">
                            <h3>Progetto 2</h3>
                            <p>Descrizione del progetto</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {data.get('company_name', 'La Tua Azienda')}. Tutti i diritti riservati.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _generate_post_html(self, data: Dict) -> str:
        """Genera pagina Post per Blog"""
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post - {data.get('company_name', 'Azienda')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="post.html" class="active">Blog</a></li>
                <li><a href="contact.html">Contatti</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main-content">
        <article class="post-article">
            <div class="container">
                <h1>Titolo del Post</h1>
                <div class="post-meta">
                    <span>Pubblicato il: {datetime.now().strftime('%d/%m/%Y')}</span>
                    <span>Autore: {data.get('company_name', 'Azienda')}</span>
                </div>
                <div class="post-content">
                    <p>Contenuto del post del blog...</p>
                </div>
            </div>
        </article>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {data.get('company_name', 'La Tua Azienda')}. Tutti i diritti riservati.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _generate_category_html(self, data: Dict) -> str:
        """Genera pagina Categoria per Blog"""
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Categoria - {data.get('company_name', 'Azienda')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="category.html" class="active">Categorie</a></li>
                <li><a href="contact.html">Contatti</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main-content">
        <section class="category-section">
            <div class="container">
                <h1>Categorie</h1>
                <div class="category-grid">
                    <div class="category-item">
                        <h3>{data.get('sector', 'Business')}</h3>
                        <p>Articoli sul settore {data.get('sector', 'business')}</p>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {data.get('company_name', 'La Tua Azienda')}. Tutti i diritti riservati.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _generate_dashboard_html(self, data: Dict) -> str:
        """Genera pagina Dashboard"""
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - {data.get('company_name', 'Azienda')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="dashboard.html" class="active">Dashboard</a></li>
                <li><a href="contact.html">Contatti</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main-content">
        <section class="dashboard-section">
            <div class="container">
                <h1>Dashboard</h1>
                <div class="dashboard-grid">
                    <div class="dashboard-card">
                        <h3>Metriche Chiave</h3>
                        <div class="metric">100</div>
                        <p>Totale Utenti</p>
                    </div>
                    <div class="dashboard-card">
                        <h3>Performance</h3>
                        <div class="metric">95%</div>
                        <p>Soddisfazione</p>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {data.get('company_name', 'La Tua Azienda')}. Tutti i diritti riservati.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _generate_login_html(self, data: Dict) -> str:
        """Genera pagina Login per SaaS"""
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - {data.get('company_name', 'Azienda')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <main class="login-main">
        <div class="login-container">
            <div class="login-form">
                <h1>Accedi</h1>
                <form id="loginForm">
                    <div class="form-group">
                        <input type="email" name="email" placeholder="Email" required>
                    </div>
                    <div class="form-group">
                        <input type="password" name="password" placeholder="Password" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Accedi</button>
                </form>
                <p>Non hai un account? <a href="#">Registrati</a></p>
            </div>
        </div>
    </main>
</body>
</html>"""
    
    def _generate_pricing_html(self, data: Dict) -> str:
        """Genera pagina Pricing per SaaS"""
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prezzi - {data.get('company_name', 'Azienda')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="pricing.html" class="active">Prezzi</a></li>
                <li><a href="login.html">Login</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main-content">
        <section class="pricing-section">
            <div class="container">
                <h1>I Nostri Prezzi</h1>
                <div class="pricing-grid">
                    <div class="pricing-card">
                        <h3>Base</h3>
                        <div class="price">€29<span>/mese</span></div>
                        <ul>
                            <li>Funzionalità base</li>
                            <li>Supporto email</li>
                            <li>5GB storage</li>
                        </ul>
                        <button class="btn btn-primary">Scegli Piano</button>
                    </div>
                    <div class="pricing-card featured">
                        <h3>Pro</h3>
                        <div class="price">€59<span>/mese</span></div>
                        <ul>
                            <li>Tutte le funzionalità</li>
                            <li>Supporto prioritario</li>
                            <li>50GB storage</li>
                        </ul>
                        <button class="btn btn-primary">Scegli Piano</button>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {data.get('company_name', 'La Tua Azienda')}. Tutti i diritti riservati.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _save_portal_files(self, portal_dir: Path, html_files: Dict, css_content: str, js_content: str, data: Dict):
        """Salva tutti i file del portale"""
        
        # Salva file HTML
        for filename, content in html_files.items():
            file_path = portal_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Salva CSS
        css_path = portal_dir / 'style.css'
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # Salva JavaScript
        js_path = portal_dir / 'script.js'
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        # Salva file di configurazione
        config_path = portal_dir / 'portal_config.json'
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Salva README
        readme_content = f"""# {data.get('portal_name', 'Portale')}

Portale generato automaticamente per {data.get('company_name', 'Azienda')}

## Informazioni
- Tipo: {data.get('portal_type', 'landing_page')}
- Settore: {data.get('sector', 'business')}
- Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## File Inclusi
- index.html: Pagina principale
- style.css: Fogli di stile
- script.js: JavaScript
- portal_config.json: Configurazione

## Deployment
1. Carica tutti i file su un server web
2. Configura il dominio
3. Testa tutte le funzionalità

## Supporto
Per supporto tecnico, contatta l'amministratore del sistema.
"""
        
        readme_path = portal_dir / 'README.md'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _create_portal_zip(self, portal_dir: Path, portal_name: str) -> Path:
        """Crea un file ZIP del portale per il download"""
        zip_path = portal_dir.parent / f"{portal_name.replace(' ', '_')}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in portal_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(portal_dir)
                    zipf.write(file_path, arcname)
        
        return zip_path
    
    def _generate_preview(self, portal_dir: Path, portal_name: str) -> Path:
        """Genera un'anteprima del portale"""
        preview_path = portal_dir / 'preview.html'
        
        # Leggi il contenuto di index.html
        index_path = portal_dir / 'index.html'
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Aggiungi informazioni di anteprima
            preview_content = content.replace(
                '<title>',
                f'<title>[ANTEPRIMA] '
            ).replace(
                '<body>',
                '''<body>
                <div style="position: fixed; top: 0; left: 0; right: 0; background: #ff6b6b; color: white; padding: 10px; text-align: center; z-index: 9999;">
                    <strong>ANTEPRIMA</strong> - {portal_name} - Generato il {datetime.now().strftime('%d/%m/%Y %H:%M')}
                </div>
                <div style="margin-top: 50px;">'''
            ).replace(
                '</body>',
                '</div></body>'
            )
            
            with open(preview_path, 'w', encoding='utf-8') as f:
                f.write(preview_content)
        
        return preview_path
    
    def _generate_analytics_code(self, data: Dict) -> str:
        """Genera codice analytics"""
        if not data.get('include_analytics', True):
            return ""
        
        return """
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'GA_TRACKING_ID');
    </script>
        """
