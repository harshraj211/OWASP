import os
import re

challenges_dir = "/home/kali/Desktop/OSWAP/challenges"

themes = {
    "a07-easy": {"company": "AeroFleet Global", "category": "A07", "color": "#D4AF37"},
    "a07-medium": {"company": "Aegis Global Treasury", "category": "A07", "color": "#50C878"},
    "a07-hard": {"company": "Apex BioLogistics", "category": "A07", "color": "#87CEEB"},
    "a08-easy": {"company": "Novus CMS", "category": "A08", "color": "#00BFFF"},
    "a08-medium": {"company": "VortexEdge SCADA", "category": "A08", "color": "#FFBF00"},
    "a08-hard": {"company": "AeroData Analytics", "category": "A08", "color": "#00BFFF"},
    "a09-easy": {"company": "Sentinel SOC", "category": "A09", "color": "#DC143C"},
    "a09-medium": {"company": "Apex Global Bank", "category": "A09", "color": "#50C878"},
    "a09-hard": {"company": "Titan Defense", "category": "A09", "color": "#DC143C"},
    "a10-easy": {"company": "QuantEdge Capital", "category": "A10", "color": "#50C878"},
    "a10-medium": {"company": "Synapse SCADA Grid", "category": "A10", "color": "#FFBF00"},
    "a10-hard": {"company": "OmniPress Media", "category": "A10", "color": "#00BFFF"}
}

base_template_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}{{company}}{% endblock %} - {{company}}</title>
    <style>
        :root {
            --bg-main: #0c0d10;
            --bg-surface: #14161b;
            --bg-card: #1c1f26;
            --border: #2a2e39;
            --accent: {{color}};
            --text-primary: #f0f2f5;
            --text-secondary: #9aa0ac;
            --text-muted: #646a78;
            --danger: #f87171;
            --success: #34d399;
            --radius: 8px;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg-main);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .site-header {
            height: 72px;
            padding: 0 clamp(1.5rem, 5vw, 4rem);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--text-primary);
            text-decoration: none;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        .nav-links { display: flex; gap: 1.5rem; align-items: center; }
        .nav-links a { color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: color 0.2s; }
        .nav-links a:hover, .nav-links a.active { color: var(--text-primary); }

        .container {
            max-width: 1200px;
            margin: 3rem auto;
            padding: 0 1.5rem;
            flex: 1;
            width: 100%;
        }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 2.5rem;
            width: 100%;
            max-width: 480px;
            margin: 0 auto 1.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        label {
            display: block;
            font-size: 0.8rem;
            text-transform: uppercase;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        input[type="text"], input[type="password"], input[type="email"], select, textarea {
            width: 100%;
            padding: 0.8rem 1rem;
            background: var(--bg-surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius);
            color: var(--text-primary) !important;
            font-size: 0.95rem;
            font-family: inherit;
            transition: all 0.2s;
            margin-bottom: 1.5rem;
        }

        input:focus {
            outline: none;
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 1px var(--accent);
        }

        button, .btn {
            width: 100%;
            padding: 0.8rem 1.5rem;
            background-color: var(--accent);
            color: #000;
            border: none;
            border-radius: var(--radius);
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        button:hover, .btn:hover { opacity: 0.9; }
        
        .btn-primary { background: var(--accent) !important; color: #111 !important; }

        .footer {
            background: var(--bg-surface);
            border-top: 1px solid var(--border);
            padding: 2rem;
            text-align: center;
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: auto;
        }

        .badge {
            padding: 0.25rem 0.6rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-green { background: rgba(52, 211, 153, 0.1); color: var(--success); border: 1px solid rgba(52, 211, 153, 0.2); }
        .badge-red { background: rgba(248, 113, 113, 0.1); color: var(--danger); border: 1px solid rgba(248, 113, 113, 0.2); }
        .badge-outline { border: 1px solid var(--border); color: var(--text-secondary); }

        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        th, td { padding: 1rem; text-align: left; border-bottom: 1px solid var(--border); font-size: 0.9rem; }
        th { color: var(--text-secondary); font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px; }
        tr:hover td { background: rgba(255, 255, 255, 0.02); }
    </style>
</head>
<body>
    <header class="site-header">
        <a class="brand" href="/">
            <img src="{{ url_for('static', filename='images/logo.webp') }}" alt="RedTeam Hacker Academy" style="height: 32px; border-radius: 4px;">
            <span>{{company}}</span>
        </a>
        <div class="nav-links">
            <a href="/" class="{% if request.path == '/' %}active{% endif %}">Home</a>
            {% block extra_nav %}{% endblock %}
            <span class="badge badge-outline">{{category}}</span>
            {% if session.get('user') or session.get('username') %}
                <span class="badge badge-green">Authorized</span>
                <a href="/logout" style="color: var(--danger); font-size: 0.85rem; font-weight: 600;">Log Out</a>
            {% endif %}
        </div>
    </header>

    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <footer class="footer">
        {{company}} Internal Systems &copy; 2026.
    </footer>
</body>
</html>
"""

for item in os.listdir(challenges_dir):
    chal_path = os.path.join(challenges_dir, item)
    if os.path.isdir(chal_path) and item in themes:
        theme = themes[item]
        templates_dir = os.path.join(chal_path, 'templates')
        if not os.path.exists(templates_dir):
            continue

        base_path = os.path.join(templates_dir, 'base.html')
        if os.path.exists(base_path):
            with open(base_path, 'r') as f:
                old_base = f.read()

            extra_nav_links = []
            links = re.findall(r'<a href="(/[^"]+)"[^>]*>(.*?)</a>', old_base)
            for link, text in links:
                if link not in ['/', '/login', '/logout'] and not link.startswith('/static') and "Home" not in text and "Log Out" not in text and "Terminate" not in text:
                    if "<img" not in text and "{" not in link and "<" not in text:
                        extra_nav_links.append(f'<a href="{link}" class="{{% if request.path == \'{link}\' %}}active{{% endif %}}">{text}</a>')
            
            extra_nav_str = "\\n            ".join(extra_nav_links)

            new_base = base_template_html.replace("{{company}}", theme['company']) \
                .replace("{{category}}", theme['category']) \
                .replace("{{color}}", theme['color']) \
                .replace("{% block extra_nav %}{% endblock %}", extra_nav_str)

            with open(base_path, 'w') as f:
                f.write(new_base)

print("A06-style minimalist clean UI applied to A07-A10.")
