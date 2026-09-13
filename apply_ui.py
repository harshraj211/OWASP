import os
import shutil
import re

challenges_dir = "/home/kali/Desktop/OSWAP/challenges"
logo_src = "/home/kali/Desktop/OSWAP/challenges/a01-easy/static/images/logo.webp"

themes = {
    "a07": {
        "name": "AeroFleet Global Operations",
        "bg1": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Airbus_A380_F-WWDD_first_flight_2.jpg/1920px-Airbus_A380_F-WWDD_first_flight_2.jpg",
        "bg2": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Flight_attendants_in_November_2015_02.jpg/1280px-Flight_attendants_in_November_2015_02.jpg",
        "navbar_color": "rgba(9, 13, 22, 0.85)"
    },
    "a08": {
        "name": "AeroData Analytics",
        "bg1": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Data_Center_-_G%C3%A4vle_borg_-_Korsn%C3%A4s_3.jpg/1280px-Data_Center_-_G%C3%A4vle_borg_-_Korsn%C3%A4s_3.jpg",
        "bg2": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Server_Room_in_the_Library_of_Congress.jpg/1280px-Server_Room_in_the_Library_of_Congress.jpg",
        "navbar_color": "rgba(10, 15, 25, 0.9)"
    },
    "a09": {
        "name": "Titan Defense Strategic Systems",
        "bg1": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/USS_Nimitz_%28CVN_68%29.jpg/1280px-USS_Nimitz_%28CVN_68%29.jpg",
        "bg2": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/F-35A_flight_%28cropped%29.jpg/1280px-F-35A_flight_%28cropped%29.jpg",
        "navbar_color": "rgba(5, 20, 10, 0.9)"
    },
    "a10": {
        "name": "QuantEdge Capital",
        "bg1": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/New_York_Stock_Exchange_building.jpg/1280px-New_York_Stock_Exchange_building.jpg",
        "bg2": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Frankfurt_B%C3%B6rse_Bulle_und_B%C3%A4r.jpg/1280px-Frankfurt_B%C3%B6rse_Bulle_und_B%C3%A4r.jpg",
        "navbar_color": "rgba(20, 15, 10, 0.9)"
    }
}

dummy_pages = ['about', 'services', 'contact', 'careers']

dummy_html_template = """{% extends "base.html" %}
{% block title %} {{ page_title }} {% endblock %}
{% block content %}
<div class="card glass-card">
    <h2>{{ page_title }}</h2>
    <p>Welcome to the {{ page_title }} page for {{ company_name }}. We pride ourselves on top-tier professional services and cutting-edge operational excellence. This section is currently undergoing maintenance and some interactive features might be disabled.</p>
    <div style="margin-top:20px; padding:20px; background:rgba(0,0,0,0.4); border-radius:8px;">
        <p style="color:#a8b2d1;"><strong>Notice:</strong> Internal communications and secure portals should be accessed via your designated operational endpoint.</p>
    </div>
</div>
{% endblock %}
"""

base_html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ company_name }}{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --bg-dark: #0f172a;
            --bg-card: rgba(30, 41, 59, 0.7);
            --border: rgba(255, 255, 255, 0.1);
            --text-light: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --danger: #ef4444;
            --success: #22c55e;
            --warning: #f59e0b;
        }

        body, html {
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-light);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* Slideshow Background */
        .bg-slideshow {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: -2;
            background: #000;
        }
        
        .bg-slideshow div {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-size: cover;
            background-position: center;
            opacity: 0;
            animation: slideAnim 20s infinite;
        }

        .bg-slideshow div:nth-child(1) {
            background-image: url('{{ bg1 }}');
            animation-delay: 0s;
        }
        .bg-slideshow div:nth-child(2) {
            background-image: url('{{ bg2 }}');
            animation-delay: 10s;
        }

        @keyframes slideAnim {
            0% { opacity: 0; transform: scale(1.05); }
            10% { opacity: 0.5; }
            40% { opacity: 0.5; }
            50% { opacity: 0; transform: scale(1); }
            100% { opacity: 0; }
        }

        /* Overlay */
        .bg-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(135deg, rgba(15,23,42,0.9) 0%, rgba(15,23,42,0.6) 100%);
            z-index: -1;
            backdrop-filter: blur(4px);
        }

        .navbar {
            background: {{ navbar_color }};
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 0 2rem;
            height: 70px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .navbar-brand {
            display: flex;
            align-items: center;
            gap: 1rem;
            color: #fff;
            text-decoration: none;
            font-weight: 700;
            font-size: 1.25rem;
            letter-spacing: 0.05em;
        }

        .navbar-brand img {
            height: 40px;
            width: auto;
        }

        .nav-links {
            display: flex;
            gap: 1.5rem;
            align-items: center;
        }

        .nav-links a {
            color: var(--text-light);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s ease-in-out;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
        }

        .nav-links a:hover, .nav-links a.active {
            color: var(--accent);
            background: rgba(255, 255, 255, 0.05);
        }

        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
            padding: 2rem;
            margin-bottom: 2rem;
        }

        .container {
            max-width: 1200px;
            margin: 3rem auto;
            padding: 0 1.5rem;
            flex: 1;
            width: 100%;
        }

        .footer {
            background: {{ navbar_color }};
            backdrop-filter: blur(12px);
            border-top: 1px solid var(--border);
            padding: 1.5rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
        }

        /* Generic element overrides to look good on glass */
        input, select, textarea {
            background: rgba(0,0,0,0.3) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            color: #fff !important;
        }
        
        table th, table td {
            border-color: rgba(255,255,255,0.1) !important;
        }
    </style>
</head>
<body>
    <div class="bg-slideshow">
        <div></div>
        <div></div>
    </div>
    <div class="bg-overlay"></div>

    <nav class="navbar">
        <a href="/" class="navbar-brand">
            <img src="{{ url_for('static', filename='images/logo.webp') }}" alt="RedTeam Hacker Academy">
            <span>{{ company_name }}</span>
        </a>
        <div class="nav-links">
            <a href="/" class="{% if request.path == '/' %}active{% endif %}">Home</a>
            <a href="/about" class="{% if request.path == '/about' %}active{% endif %}">About Us</a>
            <a href="/services" class="{% if request.path == '/services' %}active{% endif %}">Services</a>
            <a href="/contact" class="{% if request.path == '/contact' %}active{% endif %}">Contact</a>
            
            {% block extra_nav %}{% endblock %}
            
            {% if session.get('user') or session.get('username') %}
                <span style="color:var(--success); font-weight:600; font-size:0.85rem; padding: 0.25rem 0.75rem; background: rgba(34, 197, 94, 0.15); border-radius: 4px; border: 1px solid rgba(34, 197, 94, 0.3);">User Active</span>
                <a href="/logout" style="color: var(--danger);">Logout</a>
            {% else %}
                <a href="/login" class="btn btn-primary" style="background:var(--primary); color:#fff; padding:0.5rem 1rem;">Login / Portal</a>
            {% endif %}
        </div>
    </nav>

    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <footer class="footer">
        {{ company_name }} &copy; 2026. All rights reserved. | Security & Operations Gateway.
    </footer>
</body>
</html>
"""

def process_challenge(chal_path):
    chal_name = os.path.basename(chal_path)
    prefix = chal_name[:3] # e.g. a07
    if prefix not in themes:
        return
    
    theme = themes[prefix]
    
    # 1. Copy logo
    images_dir = os.path.join(chal_path, 'static', 'images')
    os.makedirs(images_dir, exist_ok=True)
    shutil.copy2(logo_src, os.path.join(images_dir, 'logo.webp'))
    
    # 2. Setup templates
    templates_dir = os.path.join(chal_path, 'templates')
    
    # Replace base.html
    base_path = os.path.join(templates_dir, 'base.html')
    if os.path.exists(base_path):
        # We want to preserve the old extra_nav if we can, but since it's hard to parse, 
        # we'll let individual pages inject their stuff or we just make base generic enough.
        # Actually, let's extract extra nav links from old base.html if they exist.
        with open(base_path, 'r') as f:
            old_base = f.read()
        
        extra_nav_links = []
        import re
        links = re.findall(r'<a href="(/[^"]+)"[^>]*>(.*?)</a>', old_base)
        for link, text in links:
            if link not in ['/', '/login', '/logout'] and not link.startswith('/static') and text.strip() not in ['Dashboard', 'Crew Sign In']:
                if "{" not in link and "<" not in text: # basic filter
                    extra_nav_links.append(f'<a href="{link}" class="{{% if request.path == \'{link}\' %}}active{{% endif %}}">{text}</a>')
        
        extra_nav_str = "\\n            ".join(extra_nav_links)
        
        new_base = base_html_template.replace("{{ company_name }}", theme['name']) \
                                     .replace("{{ bg1 }}", theme['bg1']) \
                                     .replace("{{ bg2 }}", theme['bg2']) \
                                     .replace("{{ navbar_color }}", theme['navbar_color']) \
                                     .replace("{% block extra_nav %}{% endblock %}", extra_nav_str)
        
        with open(base_path, 'w') as f:
            f.write(new_base)
            
    # Write dummy templates
    for page in dummy_pages:
        page_content = dummy_html_template.replace("{{ page_title }}", page.capitalize()) \
                                          .replace("{{ company_name }}", theme['name'])
        with open(os.path.join(templates_dir, f'{page}.html'), 'w') as f:
            f.write(page_content)
            
    # 3. Update app.py to serve dummy routes
    app_path = os.path.join(chal_path, 'app.py')
    if os.path.exists(app_path):
        with open(app_path, 'r') as f:
            app_code = f.read()
            
        dummy_routes_code = """
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/careers')
def careers():
    return render_template('careers.html')
"""
        if "@app.route('/about')" not in app_code:
            # find a good place to inject, like right before if __name__ == '__main__':
            if "if __name__ ==" in app_code:
                app_code = app_code.replace("if __name__ ==", dummy_routes_code + "\n\nif __name__ ==")
            else:
                app_code += dummy_routes_code
            
            with open(app_path, 'w') as f:
                f.write(app_code)

for item in os.listdir(challenges_dir):
    chal_path = os.path.join(challenges_dir, item)
    if os.path.isdir(chal_path) and item.startswith('a'):
        if int(item[1:3]) >= 7:
            process_challenge(chal_path)
            print(f"Processed {item}")
