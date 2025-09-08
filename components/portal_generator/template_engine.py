#!/usr/bin/env python3
"""
Template Engine per DASH_GESTIONE_LEAD
Motore per generazione template portali web
Creato da Ezio Camporeale
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
import os

class TemplateEngine:
    """Motore per la gestione dei template dei portali"""
    
    def __init__(self):
        """Inizializza il motore template"""
        self.templates_dir = Path(__file__).parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        self.templates = self.load_templates()
    
    def load_templates(self) -> Dict:
        """Carica tutti i template disponibili"""
        templates = {}
        
        # Template per Landing Page
        templates['landing_page'] = {
            'name': 'Landing Page',
            'description': 'Pagina di destinazione semplice ed efficace',
            'sections': ['header', 'hero', 'features', 'testimonials', 'contact', 'footer'],
            'files': ['index.html', 'style.css', 'script.js'],
            'responsive': True,
            'seo_optimized': True
        }
        
        # Template per Sito Aziendale
        templates['business_website'] = {
            'name': 'Sito Aziendale',
            'description': 'Sito web completo per aziende',
            'sections': ['header', 'hero', 'about', 'services', 'team', 'contact', 'footer'],
            'files': ['index.html', 'about.html', 'services.html', 'contact.html', 'style.css', 'script.js'],
            'responsive': True,
            'seo_optimized': True
        }
        
        # Template per E-commerce
        templates['ecommerce'] = {
            'name': 'E-commerce',
            'description': 'Negozio online completo',
            'sections': ['header', 'hero', 'products', 'cart', 'checkout', 'footer'],
            'files': ['index.html', 'products.html', 'cart.html', 'checkout.html', 'style.css', 'script.js'],
            'responsive': True,
            'seo_optimized': True
        }
        
        # Template per Portfolio
        templates['portfolio'] = {
            'name': 'Portfolio',
            'description': 'Sito portfolio professionale',
            'sections': ['header', 'hero', 'portfolio', 'about', 'contact', 'footer'],
            'files': ['index.html', 'portfolio.html', 'about.html', 'contact.html', 'style.css', 'script.js'],
            'responsive': True,
            'seo_optimized': True
        }
        
        # Template per Blog
        templates['blog'] = {
            'name': 'Blog',
            'description': 'Blog professionale',
            'sections': ['header', 'hero', 'posts', 'sidebar', 'footer'],
            'files': ['index.html', 'post.html', 'category.html', 'style.css', 'script.js'],
            'responsive': True,
            'seo_optimized': True
        }
        
        # Template per Dashboard
        templates['dashboard'] = {
            'name': 'Dashboard',
            'description': 'Dashboard interattiva',
            'sections': ['header', 'sidebar', 'main', 'charts', 'footer'],
            'files': ['index.html', 'dashboard.html', 'style.css', 'script.js', 'charts.js'],
            'responsive': True,
            'seo_optimized': False
        }
        
        # Template per SaaS Platform
        templates['saas'] = {
            'name': 'SaaS Platform',
            'description': 'Piattaforma SaaS completa',
            'sections': ['header', 'hero', 'features', 'pricing', 'login', 'dashboard', 'footer'],
            'files': ['index.html', 'login.html', 'dashboard.html', 'pricing.html', 'style.css', 'script.js'],
            'responsive': True,
            'seo_optimized': True
        }
        
        return templates
    
    def get_template(self, template_type: str) -> Optional[Dict]:
        """Ottiene un template specifico"""
        return self.templates.get(template_type)
    
    def get_all_templates(self) -> Dict:
        """Ottiene tutti i template disponibili"""
        return self.templates
    
    def get_template_html(self, template_type: str, section: str, data: Dict) -> str:
        """Genera l'HTML per una sezione specifica del template"""
        
        if template_type == 'landing_page':
            return self._generate_landing_page_html(section, data)
        elif template_type == 'business_website':
            return self._generate_business_website_html(section, data)
        elif template_type == 'ecommerce':
            return self._generate_ecommerce_html(section, data)
        elif template_type == 'portfolio':
            return self._generate_portfolio_html(section, data)
        elif template_type == 'blog':
            return self._generate_blog_html(section, data)
        elif template_type == 'dashboard':
            return self._generate_dashboard_html(section, data)
        elif template_type == 'saas':
            return self._generate_saas_html(section, data)
        else:
            return self._generate_default_html(section, data)
    
    def get_template_css(self, template_type: str, color_scheme: str) -> str:
        """Genera il CSS per un template specifico"""
        
        # Schema colori
        color_schemes = {
            "Blu Professionale": {
                "primary": "#2E86AB",
                "secondary": "#A23B72", 
                "accent": "#F18F01",
                "text": "#2C3E50",
                "background": "#FFFFFF"
            },
            "Verde Finanza": {
                "primary": "#27AE60",
                "secondary": "#2ECC71",
                "accent": "#F39C12",
                "text": "#2C3E50",
                "background": "#FFFFFF"
            },
            "Rosso Energia": {
                "primary": "#E74C3C",
                "secondary": "#C0392B",
                "accent": "#F39C12",
                "text": "#2C3E50",
                "background": "#FFFFFF"
            },
            "Viola Creativo": {
                "primary": "#8E44AD",
                "secondary": "#9B59B6",
                "accent": "#F39C12",
                "text": "#2C3E50",
                "background": "#FFFFFF"
            }
        }
        
        colors = color_schemes.get(color_scheme, color_schemes["Blu Professionale"])
        
        if template_type == 'landing_page':
            return self._generate_landing_page_css(colors)
        elif template_type == 'business_website':
            return self._generate_business_website_css(colors)
        elif template_type == 'ecommerce':
            return self._generate_ecommerce_css(colors)
        elif template_type == 'portfolio':
            return self._generate_portfolio_css(colors)
        elif template_type == 'blog':
            return self._generate_blog_css(colors)
        elif template_type == 'dashboard':
            return self._generate_dashboard_css(colors)
        elif template_type == 'saas':
            return self._generate_saas_css(colors)
        else:
            return self._generate_default_css(colors)
    
    def get_template_js(self, template_type: str, features: Dict) -> str:
        """Genera il JavaScript per un template specifico"""
        
        if template_type == 'landing_page':
            return self._generate_landing_page_js(features)
        elif template_type == 'business_website':
            return self._generate_business_website_js(features)
        elif template_type == 'ecommerce':
            return self._generate_ecommerce_js(features)
        elif template_type == 'portfolio':
            return self._generate_portfolio_js(features)
        elif template_type == 'blog':
            return self._generate_blog_js(features)
        elif template_type == 'dashboard':
            return self._generate_dashboard_js(features)
        elif template_type == 'saas':
            return self._generate_saas_js(features)
        else:
            return self._generate_default_js(features)
    
    def _generate_landing_page_html(self, section: str, data: Dict) -> str:
        """Genera HTML per Landing Page"""
        
        if section == 'header':
            return f"""
            <header class="header">
                <nav class="navbar">
                    <div class="nav-brand">
                        <h2>{data.get('company_name', 'La Tua Azienda')}</h2>
                    </div>
                    <ul class="nav-menu">
                        <li><a href="#home">Home</a></li>
                        <li><a href="#features">Caratteristiche</a></li>
                        <li><a href="#testimonials">Testimonianze</a></li>
                        <li><a href="#contact">Contatti</a></li>
                    </ul>
                </nav>
            </header>
            """
        
        elif section == 'hero':
            return f"""
            <section id="home" class="hero">
                <div class="hero-content">
                    <h1>{data.get('portal_name', 'Benvenuto')}</h1>
                    <p class="hero-subtitle">{data.get('business_goals', 'La soluzione perfetta per le tue esigenze')}</p>
                    <div class="hero-buttons">
                        <a href="#contact" class="btn btn-primary">Inizia Ora</a>
                        <a href="#features" class="btn btn-secondary">Scopri di Più</a>
                    </div>
                </div>
            </section>
            """
        
        elif section == 'features':
            return f"""
            <section id="features" class="features">
                <div class="container">
                    <h2>Caratteristiche Principali</h2>
                    <div class="features-grid">
                        <div class="feature-card">
                            <div class="feature-icon">🚀</div>
                            <h3>Velocità</h3>
                            <p>Performance ottimizzate per risultati eccellenti</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🔒</div>
                            <h3>Sicurezza</h3>
                            <p>Protezione avanzata per i tuoi dati</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">📱</div>
                            <h3>Mobile</h3>
                            <p>Completamente responsive su tutti i dispositivi</p>
                        </div>
                    </div>
                </div>
            </section>
            """
        
        elif section == 'contact':
            contact_form = ""
            if data.get('include_contact_form', True):
                contact_form = f"""
                <div class="contact-form">
                    <h3>Contattaci</h3>
                    <form id="contactForm">
                        <div class="form-group">
                            <input type="text" name="name" placeholder="Nome" required>
                        </div>
                        <div class="form-group">
                            <input type="email" name="email" placeholder="Email" required>
                        </div>
                        <div class="form-group">
                            <textarea name="message" placeholder="Messaggio" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Invia Messaggio</button>
                    </form>
                </div>
                """
            
            return f"""
            <section id="contact" class="contact">
                <div class="container">
                    <h2>Contattaci</h2>
                    <div class="contact-content">
                        <div class="contact-info">
                            <h3>{data.get('company_name', 'La Tua Azienda')}</h3>
                            <p>{data.get('business_goals', 'Siamo qui per aiutarti')}</p>
                            <div class="contact-details">
                                <p>📧 info@azienda.com</p>
                                <p>📞 +39 123 456 7890</p>
                                <p>📍 Via Roma 123, Milano</p>
                            </div>
                        </div>
                        {contact_form}
                    </div>
                </div>
            </section>
            """
        
        elif section == 'footer':
            return f"""
            <footer class="footer">
                <div class="container">
                    <div class="footer-content">
                        <div class="footer-section">
                            <h3>{data.get('company_name', 'La Tua Azienda')}</h3>
                            <p>{data.get('business_goals', 'La tua soluzione di riferimento')}</p>
                        </div>
                        <div class="footer-section">
                            <h4>Link Utili</h4>
                            <ul>
                                <li><a href="#home">Home</a></li>
                                <li><a href="#features">Caratteristiche</a></li>
                                <li><a href="#contact">Contatti</a></li>
                            </ul>
                        </div>
                        <div class="footer-section">
                            <h4>Contatti</h4>
                            <p>📧 info@azienda.com</p>
                            <p>📞 +39 123 456 7890</p>
                        </div>
                    </div>
                    <div class="footer-bottom">
                        <p>&copy; 2024 {data.get('company_name', 'La Tua Azienda')}. Tutti i diritti riservati.</p>
                    </div>
                </div>
            </footer>
            """
        
        return ""
    
    def _generate_landing_page_css(self, colors: Dict) -> str:
        """Genera CSS per Landing Page"""
        return f"""
        /* Reset e Base */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: {colors['text']};
            background-color: {colors['background']};
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        /* Header */
        .header {{
            background: {colors['primary']};
            color: white;
            padding: 1rem 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
        }}
        
        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .nav-brand h2 {{
            color: white;
        }}
        
        .nav-menu {{
            display: flex;
            list-style: none;
            gap: 2rem;
        }}
        
        .nav-menu a {{
            color: white;
            text-decoration: none;
            transition: color 0.3s;
        }}
        
        .nav-menu a:hover {{
            color: {colors['accent']};
        }}
        
        /* Hero Section */
        .hero {{
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            color: white;
            padding: 120px 0 80px;
            text-align: center;
        }}
        
        .hero-content h1 {{
            font-size: 3.5rem;
            margin-bottom: 1rem;
            font-weight: bold;
        }}
        
        .hero-subtitle {{
            font-size: 1.3rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }}
        
        .hero-buttons {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        /* Buttons */
        .btn {{
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s;
            cursor: pointer;
            display: inline-block;
        }}
        
        .btn-primary {{
            background: {colors['accent']};
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #e67e22;
            transform: translateY(-2px);
        }}
        
        .btn-secondary {{
            background: transparent;
            color: white;
            border: 2px solid white;
        }}
        
        .btn-secondary:hover {{
            background: white;
            color: {colors['primary']};
        }}
        
        /* Features Section */
        .features {{
            padding: 80px 0;
            background: #f8f9fa;
        }}
        
        .features h2 {{
            text-align: center;
            margin-bottom: 3rem;
            font-size: 2.5rem;
            color: {colors['text']};
        }}
        
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }}
        
        .feature-card {{
            background: white;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .feature-card:hover {{
            transform: translateY(-5px);
        }}
        
        .feature-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        
        .feature-card h3 {{
            margin-bottom: 1rem;
            color: {colors['primary']};
        }}
        
        /* Contact Section */
        .contact {{
            padding: 80px 0;
            background: {colors['primary']};
            color: white;
        }}
        
        .contact h2 {{
            text-align: center;
            margin-bottom: 3rem;
            font-size: 2.5rem;
        }}
        
        .contact-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: start;
        }}
        
        .contact-info h3 {{
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }}
        
        .contact-details p {{
            margin-bottom: 0.5rem;
        }}
        
        .contact-form {{
            background: rgba(255,255,255,0.1);
            padding: 2rem;
            border-radius: 10px;
        }}
        
        .form-group {{
            margin-bottom: 1rem;
        }}
        
        .form-group input,
        .form-group textarea {{
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
        }}
        
        .form-group textarea {{
            height: 120px;
            resize: vertical;
        }}
        
        /* Footer */
        .footer {{
            background: {colors['text']};
            color: white;
            padding: 3rem 0 1rem;
        }}
        
        .footer-content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .footer-section h3,
        .footer-section h4 {{
            margin-bottom: 1rem;
            color: {colors['accent']};
        }}
        
        .footer-section ul {{
            list-style: none;
        }}
        
        .footer-section ul li {{
            margin-bottom: 0.5rem;
        }}
        
        .footer-section a {{
            color: white;
            text-decoration: none;
            transition: color 0.3s;
        }}
        
        .footer-section a:hover {{
            color: {colors['accent']};
        }}
        
        .footer-bottom {{
            text-align: center;
            padding-top: 2rem;
            border-top: 1px solid #555;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .hero-content h1 {{
                font-size: 2.5rem;
            }}
            
            .hero-buttons {{
                flex-direction: column;
                align-items: center;
            }}
            
            .contact-content {{
                grid-template-columns: 1fr;
            }}
            
            .nav-menu {{
                display: none;
            }}
        }}
        """
    
    def _generate_landing_page_js(self, features: Dict) -> str:
        """Genera JavaScript per Landing Page"""
        js_code = """
        // Smooth scrolling per i link di navigazione
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Animazioni al scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);
        
        // Osserva gli elementi da animare
        document.querySelectorAll('.feature-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });
        """
        
        # Aggiungi gestione form contatto se abilitato
        if features.get('include_contact_form', True):
            js_code += """
        
        // Gestione form contatto
        document.getElementById('contactForm')?.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Simula invio (qui potresti aggiungere una chiamata API reale)
            console.log('Dati form:', data);
            
            // Mostra messaggio di successo
            alert('Messaggio inviato con successo! Ti contatteremo presto.');
            
            // Reset form
            this.reset();
        });
            """
        
        # Aggiungi analytics se abilitato
        if features.get('include_analytics', True):
            js_code += """
        
        // Google Analytics (sostituisci con il tuo tracking ID)
        // gtag('config', 'GA_TRACKING_ID');
        
        // Tracking eventi personalizzati
        function trackEvent(eventName, eventData) {
            console.log('Evento tracciato:', eventName, eventData);
            // gtag('event', eventName, eventData);
        }
        
        // Traccia click sui pulsanti
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', function() {
                trackEvent('button_click', {
                    button_text: this.textContent,
                    button_class: this.className
                });
            });
        });
            """
        
        return js_code
    
    # Metodi per altri template (implementazione base)
    def _generate_business_website_html(self, section: str, data: Dict) -> str:
        """Genera HTML per Sito Aziendale"""
        return self._generate_default_html(section, data)
    
    def _generate_ecommerce_html(self, section: str, data: Dict) -> str:
        """Genera HTML per E-commerce"""
        return self._generate_default_html(section, data)
    
    def _generate_portfolio_html(self, section: str, data: Dict) -> str:
        """Genera HTML per Portfolio"""
        return self._generate_default_html(section, data)
    
    def _generate_blog_html(self, section: str, data: Dict) -> str:
        """Genera HTML per Blog"""
        return self._generate_default_html(section, data)
    
    def _generate_dashboard_html(self, section: str, data: Dict) -> str:
        """Genera HTML per Dashboard"""
        return self._generate_default_html(section, data)
    
    def _generate_saas_html(self, section: str, data: Dict) -> str:
        """Genera HTML per SaaS Platform"""
        return self._generate_default_html(section, data)
    
    def _generate_default_html(self, section: str, data: Dict) -> str:
        """Genera HTML di default"""
        return f"<div class='{section}'><h2>{section.title()}</h2><p>Contenuto per {section}</p></div>"
    
    # Metodi CSS per altri template (implementazione base)
    def _generate_business_website_css(self, colors: Dict) -> str:
        return self._generate_default_css(colors)
    
    def _generate_ecommerce_css(self, colors: Dict) -> str:
        return self._generate_default_css(colors)
    
    def _generate_portfolio_css(self, colors: Dict) -> str:
        return self._generate_default_css(colors)
    
    def _generate_blog_css(self, colors: Dict) -> str:
        return self._generate_default_css(colors)
    
    def _generate_dashboard_css(self, colors: Dict) -> str:
        return self._generate_default_css(colors)
    
    def _generate_saas_css(self, colors: Dict) -> str:
        return self._generate_default_css(colors)
    
    def _generate_default_css(self, colors: Dict) -> str:
        return f"""
        body {{ 
            font-family: Arial, sans-serif; 
            color: {colors['text']}; 
            background: {colors['background']}; 
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        """
    
    # Metodi JS per altri template (implementazione base)
    def _generate_business_website_js(self, features: Dict) -> str:
        return self._generate_default_js(features)
    
    def _generate_ecommerce_js(self, features: Dict) -> str:
        return self._generate_default_js(features)
    
    def _generate_portfolio_js(self, features: Dict) -> str:
        return self._generate_default_js(features)
    
    def _generate_blog_js(self, features: Dict) -> str:
        return self._generate_default_js(features)
    
    def _generate_dashboard_js(self, features: Dict) -> str:
        return self._generate_default_js(features)
    
    def _generate_saas_js(self, features: Dict) -> str:
        return self._generate_default_js(features)
    
    def _generate_default_js(self, features: Dict) -> str:
        return "console.log('Portale caricato con successo!');"
