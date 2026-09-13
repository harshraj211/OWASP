import os
import re

challenges_dir = "/home/kali/Desktop/OSWAP/challenges"

themes = {
    "a07-easy": {
        "company": "AeroFleet Global",
        "category": "A07: Identification and Authentication Failures",
        "color": "#D4AF37",
        "color_hover": "#F3E5AB",
        "bg_color": "#0A192F",
        "bg_css": "linear-gradient(135deg, #0A192F 0%, #172A45 100%), radial-gradient(circle at 50% 50%, rgba(212, 175, 55, 0.1) 0%, transparent 60%)",
        "stat_labels": ["Active Flights", "Crew on Duty", "Dispatch Status"],
        "stat_vals": ["1,242", "4,810", "NOMINAL"],
        "field1": "Crew ID",
        "field2": "Dispatch Code"
    },
    "a07-medium": {
        "company": "Aegis Global Treasury",
        "category": "A07: Identification and Authentication Failures",
        "color": "#50C878",
        "color_hover": "#5CE68A",
        "bg_color": "#1C1C1C",
        "bg_css": "linear-gradient(135deg, #1C1C1C 0%, #2A2A2A 100%), repeating-linear-gradient(45deg, rgba(80,200,120,0.03) 0px, rgba(80,200,120,0.03) 2px, transparent 2px, transparent 10px)",
        "stat_labels": ["Assets Under Management", "Active Clearances", "Threat Level"],
        "stat_vals": ["$1.4T", "342", "ELEVATED"],
        "field1": "Operator ID",
        "field2": "Clearance Token"
    },
    "a07-hard": {
        "company": "Apex BioLogistics",
        "category": "A07: Identification and Authentication Failures",
        "color": "#87CEEB",
        "color_hover": "#AEE2FF",
        "bg_color": "#001F3F",
        "bg_css": "linear-gradient(to right, #001f3f, #003366), radial-gradient(circle at top left, rgba(255,255,255,0.05), transparent)",
        "stat_labels": ["Active Shipments", "Cold Chain Integrity", "Compliance Status"],
        "stat_vals": ["8,941", "99.98%", "VERIFIED"],
        "field1": "Staff ID",
        "field2": "Biometric PIN"
    },
    "a08-easy": {
        "company": "Novus CMS",
        "category": "A08: Software and Data Integrity Failures",
        "color": "#00BFFF",
        "color_hover": "#4DD2FF",
        "bg_color": "#111111",
        "bg_css": "linear-gradient(180deg, #111 0%, #222 100%), radial-gradient(circle at 80% 20%, rgba(0,191,255,0.15) 0%, transparent 50%)",
        "stat_labels": ["Published Articles", "Active Editors", "CMS Version"],
        "stat_vals": ["142,501", "1,204", "v9.4.1-STABLE"],
        "field1": "Editor Handle",
        "field2": "Access Key"
    },
    "a08-medium": {
        "company": "VortexEdge SCADA",
        "category": "A08: Software and Data Integrity Failures",
        "color": "#FFBF00",
        "color_hover": "#FFD147",
        "bg_color": "#2F4F4F",
        "bg_css": "linear-gradient(45deg, #2F4F4F 0%, #1a2c2c 100%), repeating-radial-gradient(circle at center, rgba(255,191,0,0.03) 0, rgba(255,191,0,0.03) 10px, transparent 10px, transparent 20px)",
        "stat_labels": ["Grid Load", "Active Substations", "Last OTA Update"],
        "stat_vals": ["84.2%", "412", "02:14:00 UTC"],
        "field1": "Engineer ID",
        "field2": "Gateway Token"
    },
    "a08-hard": {
        "company": "AeroData Analytics",
        "category": "A08: Software and Data Integrity Failures",
        "color": "#00BFFF",
        "color_hover": "#4DD2FF",
        "bg_color": "#050505",
        "bg_css": "linear-gradient(135deg, #050505 0%, #151525 100%), linear-gradient(0deg, rgba(0, 191, 255, 0.05) 1px, transparent 1px)",
        "stat_labels": ["Pipeline Jobs", "Data Ingested (24h)", "Anomaly Score"],
        "stat_vals": ["1,402", "42.8 PB", "0.012 (LOW)"],
        "field1": "Analyst ID",
        "field2": "Pipeline Key"
    },
    "a09-easy": {
        "company": "Sentinel SOC",
        "category": "A09: Security Logging and Alerting Failures",
        "color": "#DC143C",
        "color_hover": "#E84A68",
        "bg_color": "#0A0A0A",
        "bg_css": "linear-gradient(135deg, #0a0a0a 0%, #1a0505 100%), radial-gradient(circle at center, rgba(220,20,60,0.1) 0%, transparent 70%)",
        "stat_labels": ["Active Alerts", "Events Per Second", "SIEM Status"],
        "stat_vals": ["4", "14,502", "ACTIVE"],
        "field1": "Operator Handle",
        "field2": "SOC Token"
    },
    "a09-medium": {
        "company": "Apex Global Bank",
        "category": "A09: Security Logging and Alerting Failures",
        "color": "#50C878",
        "color_hover": "#5CE68A",
        "bg_color": "#222222",
        "bg_css": "linear-gradient(180deg, #222 0%, #111 100%), repeating-linear-gradient(90deg, rgba(80,200,120,0.02) 0px, rgba(80,200,120,0.02) 1px, transparent 1px, transparent 20px)",
        "stat_labels": ["Daily Transaction Vol", "Compliance Score", "Audit Status"],
        "stat_vals": ["$12.4B", "99.8/100", "LOCKED"],
        "field1": "Banker ID",
        "field2": "Compliance PIN"
    },
    "a09-hard": {
        "company": "Titan Defense",
        "category": "A09: Security Logging and Alerting Failures",
        "color": "#DC143C",
        "color_hover": "#E84A68",
        "bg_color": "#000000",
        "bg_css": "linear-gradient(to right, #000000, #1a0000), repeating-radial-gradient(circle at center, rgba(220,20,60,0.05) 0, rgba(220,20,60,0.05) 5px, transparent 5px, transparent 15px)",
        "stat_labels": ["Clearance Level", "Active Operations", "Audit Chain Status"],
        "stat_vals": ["TOP SECRET // SCI", "14", "VERIFIED"],
        "field1": "Operative ID",
        "field2": "Command Token"
    },
    "a10-easy": {
        "company": "QuantEdge Capital",
        "category": "A10: Mishandling of Exceptional Conditions",
        "color": "#50C878",
        "color_hover": "#5CE68A",
        "bg_color": "#111111",
        "bg_css": "linear-gradient(135deg, #111 0%, #2a2a2a 100%), linear-gradient(0deg, rgba(80,200,120,0.05) 1px, transparent 1px)",
        "stat_labels": ["Portfolio Value", "Active Strategies", "Sharpe Ratio"],
        "stat_vals": ["$4.2B", "214", "2.84"],
        "field1": "Quant ID",
        "field2": "Vault Token"
    },
    "a10-medium": {
        "company": "Synapse SCADA Grid",
        "category": "A10: Mishandling of Exceptional Conditions",
        "color": "#FFBF00",
        "color_hover": "#FFD147",
        "bg_color": "#1f2833",
        "bg_css": "linear-gradient(135deg, #1f2833 0%, #0b0c10 100%), radial-gradient(circle at 20% 50%, rgba(255, 191, 0, 0.1) 0%, transparent 60%)",
        "stat_labels": ["Grid Frequency", "Active Substations", "Safety Status"],
        "stat_vals": ["60.01 Hz", "1,804", "NOMINAL"],
        "field1": "Grid Engineer ID",
        "field2": "Interlock Code"
    },
    "a10-hard": {
        "company": "OmniPress Media",
        "category": "A10: Mishandling of Exceptional Conditions",
        "color": "#00BFFF",
        "color_hover": "#4DD2FF",
        "bg_color": "#0a1128",
        "bg_css": "linear-gradient(180deg, #111 0%, #0a1128 100%), radial-gradient(circle at 50% 0%, rgba(0, 191, 255, 0.2) 0%, transparent 50%)",
        "stat_labels": ["Active Campaigns", "Assets Uploaded Today", "CDN Status"],
        "stat_vals": ["4,102", "84,102", "HEALTHY"],
        "field1": "Producer ID",
        "field2": "Media Key"
    }
}

base_template_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{company}}{% endblock %} - {{company}}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: {{color}};
            --primary-hover: {{color_hover}};
            --bg-color: {{bg_color}};
            --text-light: #f8fafc;
            --text-muted: #94a3b8;
            --danger: #ef4444;
            --success: #22c55e;
            --border: rgba(255, 255, 255, 0.15);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: {{bg_css}};
            background-color: var(--bg-color);
            color: var(--text-light);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            background-attachment: fixed;
        }

        /* Top Navbar */
        .navbar {
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }

        .navbar-brand {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text-light);
            text-decoration: none;
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .navbar-brand::before {
            content: '';
            display: inline-block;
            width: 12px;
            height: 12px;
            background-color: var(--primary);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--primary);
        }

        .category-badge {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid var(--primary);
            color: var(--primary);
            padding: 0.4rem 0.8rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Animated Status Bar */
        .status-bar {
            background: rgba(0, 0, 0, 0.8);
            border-bottom: 1px solid var(--border);
            padding: 0.5rem 2rem;
            display: flex;
            gap: 3rem;
            font-size: 0.75rem;
            font-family: 'Inter', monospace;
            color: var(--text-muted);
            overflow: hidden;
            white-space: nowrap;
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-value {
            color: var(--text-light);
            font-weight: 600;
        }

        .status-indicator {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: var(--primary);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 0.4; box-shadow: 0 0 0 0 rgba(var(--primary-rgb), 0.7); }
            70% { opacity: 1; box-shadow: 0 0 0 6px rgba(var(--primary-rgb), 0); }
            100% { opacity: 0.4; box-shadow: 0 0 0 0 rgba(var(--primary-rgb), 0); }
        }

        /* Container & Cards */
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1.5rem;
            flex: 1;
            width: 100%;
        }

        .card, .glass-card {
            background: rgba(10, 15, 25, 0.65);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 2.5rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            margin-bottom: 1.5rem;
        }

        /* Forms */
        label {
            display: block;
            font-size: 0.8rem;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
            font-weight: 600;
            letter-spacing: 0.05em;
        }

        input[type="text"], input[type="password"], input[type="email"], select, textarea {
            width: 100%;
            padding: 0.75rem 1rem;
            background: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid var(--border) !important;
            border-radius: 6px;
            color: var(--text-light) !important;
            font-size: 0.9rem;
            font-family: inherit;
            transition: all 0.2s;
            margin-bottom: 1.5rem;
        }

        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(var(--primary-rgb), 0.2);
        }

        button, .btn {
            width: 100%;
            padding: 0.875rem 1.5rem;
            background-color: var(--primary);
            color: #000;
            border: none;
            border-radius: 6px;
            font-size: 0.9rem;
            font-weight: 700;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        button:hover, .btn:hover {
            filter: brightness(1.1);
            transform: translateY(-1px);
        }
        
        .btn-primary {
            background: var(--primary) !important;
            color: #111 !important;
        }

        /* Nav Links */
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
            padding: 0.4rem 0.6rem;
            border-radius: 6px;
        }
        .nav-links a:hover, .nav-links a.active {
            color: var(--primary);
            background: rgba(255, 255, 255, 0.05);
        }

        /* Footer */
        .footer {
            background: rgba(0, 0, 0, 0.8);
            border-top: 1px solid var(--border);
            padding: 1.5rem;
            text-align: center;
            font-size: 0.8rem;
            color: var(--text-muted);
            letter-spacing: 0.05em;
        }
        
        .footer strong {
            color: var(--primary);
        }

        /* Utility */
        .badge {
            padding: 0.25rem 0.6rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-green { background: rgba(34, 197, 94, 0.15); color: var(--success); border: 1px solid rgba(34,197,94,0.3); }
        .badge-red { background: rgba(239, 68, 68, 0.15); color: var(--danger); border: 1px solid rgba(239,68,68,0.3); }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        th, td {
            padding: 0.85rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
            font-size: 0.875rem;
        }
        th {
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
        }
        tr:hover td {
            background: rgba(255, 255, 255, 0.03);
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="navbar-brand">
            {{company}}
        </a>
        <div class="nav-links">
            <a href="/" class="{% if request.path == '/' %}active{% endif %}">Home</a>
            {% block extra_nav %}{% endblock %}
            {% if session.get('user') or session.get('username') %}
                <span class="badge badge-green">Authorized</span>
                <a href="/logout" style="color: var(--danger); text-decoration: none; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Terminate Session</a>
            {% endif %}
            <div class="category-badge">{{category}}</div>
        </div>
    </nav>

    <div class="status-bar">
        <div class="status-item">
            <span class="status-indicator"></span>
            <span>{{stat_l1}}:</span>
            <span class="status-value dynamic-stat">{{stat_v1}}</span>
        </div>
        <div class="status-item">
            <span class="status-indicator" style="animation-delay: 0.5s;"></span>
            <span>{{stat_l2}}:</span>
            <span class="status-value dynamic-stat-2">{{stat_v2}}</span>
        </div>
        <div class="status-item">
            <span class="status-indicator" style="animation-delay: 1s;"></span>
            <span>{{stat_l3}}:</span>
            <span class="status-value">{{stat_v3}}</span>
        </div>
        <div class="status-item" style="margin-left: auto;">
            <span>SYS_TIME:</span>
            <span class="status-value" id="sys-time">00:00:00 UTC</span>
        </div>
    </div>

    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <footer class="footer">
        CONFIDENTIAL: <strong>{{company}}</strong> Internal Systems &copy; 2026. Unauthorized access is strictly prohibited and monitored.
    </footer>

    <script>
        // Decorative JS for live operational stats
        function updateTime() {
            const now = new Date();
            document.getElementById('sys-time').innerText = now.toISOString().substring(11, 19) + ' UTC';
        }
        setInterval(updateTime, 1000);
        updateTime();

        // Randomly tick numbers to make it look alive
        const stat1 = document.querySelector('.dynamic-stat');
        const stat2 = document.querySelector('.dynamic-stat-2');
        
        setInterval(() => {
            if(stat1 && stat1.innerText.includes(',')) {
                let val = parseInt(stat1.innerText.replace(/,/g, ''));
                val += Math.floor(Math.random() * 3);
                stat1.innerText = val.toLocaleString();
            }
        }, 4000);
    </script>
</body>
</html>
"""

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return f"{int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}"

for item in os.listdir(challenges_dir):
    chal_path = os.path.join(challenges_dir, item)
    if os.path.isdir(chal_path) and item in themes:
        theme = themes[item]
        templates_dir = os.path.join(chal_path, 'templates')
        if not os.path.exists(templates_dir):
            continue

        # 1. Update base.html
        base_path = os.path.join(templates_dir, 'base.html')
        
        if os.path.exists(base_path):
            with open(base_path, 'r') as f:
                old_base = f.read()

            # Extract any extra nav links that were added previously (excluding standard ones)
            extra_nav_links = []
            links = re.findall(r'<a href="(/[^"]+)"[^>]*>(.*?)</a>', old_base)
            for link, text in links:
                if link not in ['/', '/login', '/logout'] and not link.startswith('/static') and "Home" not in text and "Dashboard" not in text and "Terminate" not in text:
                    # Ignore the RedTeam hacker academy logo link text
                    if "<img" not in text and "{" not in link and "<" not in text:
                        extra_nav_links.append(f'<a href="{link}" class="{{% if request.path == \'{link}\' %}}active{{% endif %}}">{text}</a>')
            
            extra_nav_str = "\\n            ".join(extra_nav_links)

            new_base = base_template_html.replace("{{company}}", theme['company']) \
                .replace("{{category}}", theme['category']) \
                .replace("{{color}}", theme['color']) \
                .replace("{{color_hover}}", theme['color_hover']) \
                .replace("{{bg_color}}", theme['bg_color']) \
                .replace("{{bg_css}}", theme['bg_css']) \
                .replace("{{stat_l1}}", theme['stat_labels'][0]) \
                .replace("{{stat_l2}}", theme['stat_labels'][1]) \
                .replace("{{stat_l3}}", theme['stat_labels'][2]) \
                .replace("{{stat_v1}}", theme['stat_vals'][0]) \
                .replace("{{stat_v2}}", theme['stat_vals'][1]) \
                .replace("{{stat_v3}}", theme['stat_vals'][2]) \
                .replace("{% block extra_nav %}{% endblock %}", extra_nav_str)

            # We also need to inject RGB for the pulse animation:
            rgb_color = hex_to_rgb(theme['color'])
            new_base = new_base.replace("var(--primary-rgb)", rgb_color)

            with open(base_path, 'w') as f:
                f.write(new_base)

        # 2. Iterate through all other HTML files to update labels and generic text
        for tpl in os.listdir(templates_dir):
            if tpl.endswith('.html'):
                tpl_path = os.path.join(templates_dir, tpl)
                with open(tpl_path, 'r') as f:
                    content = f.read()

                # Regex replacement for Username -> Field 1
                # We want to catch >Username< or Username</label> or placeholder="Username"
                content = re.sub(r'(>|\b)Username(<|\b)', rf'\g<1>{theme["field1"]}\g<2>', content)
                content = re.sub(r'(>|\b)Password(<|\b)', rf'\g<1>{theme["field2"]}\g<2>', content)
                content = re.sub(r'placeholder="Username"', f'placeholder="{theme["field1"]}"', content)
                content = re.sub(r'placeholder="Password"', f'placeholder="{theme["field2"]}"', content)

                # Just to catch variations like > Username <
                content = re.sub(r'>\s*Username\s*<', f'>{theme["field1"]}<', content)
                content = re.sub(r'>\s*Password\s*<', f'>{theme["field2"]}<', content)

                # And remove references to RedTeam Academy if they snuck into other templates
                content = content.replace("RedTeam Hacker Academy", theme['company'])

                # Also replace buttons that say "Crew Sign In" or similar if they don't match
                # I'll just leave them since they might be okay.

                with open(tpl_path, 'w') as f:
                    f.write(content)

print("Redesign applied.")
