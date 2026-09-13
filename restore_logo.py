import os
import re

challenges_dir = "/home/kali/Desktop/OSWAP/challenges"

for item in os.listdir(challenges_dir):
    chal_path = os.path.join(challenges_dir, item)
    if os.path.isdir(chal_path) and item.startswith('a') and int(item[1:3]) >= 7:
        base_path = os.path.join(chal_path, 'templates', 'base.html')
        if os.path.exists(base_path):
            with open(base_path, 'r') as f:
                content = f.read()

            # Find the navbar-brand block
            # <a href="/" class="navbar-brand">
            #     {{company}}
            # </a>
            
            # The current content inside navbar-brand is just the company name with whitespace.
            # We will use regex to replace it.
            
            pattern = re.compile(r'(<a href="/" class="navbar-brand">)(\s*)(.*?)(\s*</a>)', re.DOTALL)
            
            def replace_brand(match):
                company_name = match.group(3).strip()
                # If there's already an img, don't double add
                if "<img" in company_name:
                    return match.group(0)
                
                replacement = f'{match.group(1)}\n            <img src="{{{{ url_for(\'static\', filename=\'images/logo.webp\') }}}}" alt="RedTeam Hacker Academy" style="height: 38px; width: auto; margin-right: 10px; border-radius: 4px;">\n            {company_name}\n        </a>'
                return replacement

            new_content = pattern.sub(replace_brand, content)
            
            with open(base_path, 'w') as f:
                f.write(new_content)
                
print("Logo restored.")
