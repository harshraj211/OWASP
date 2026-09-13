import os
import re

challenges_dir = "/home/kali/Desktop/OSWAP/challenges"

for level in ['easy', 'medium', 'hard']:
    src_dir = os.path.join(challenges_dir, f'a06-{level}', 'src')
    if not os.path.exists(src_dir):
        continue
    
    for fname in os.listdir(src_dir):
        if fname.endswith('.php'):
            filepath = os.path.join(src_dir, fname)
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Regex to find: <a class="brand... href="./"...> ... </a>
            # We want to inject the img right after the <a ...> opening tag.
            
            def replace_logo(match):
                a_tag = match.group(0)
                # If already injected, skip
                if 'logo.webp' in a_tag:
                    return a_tag
                
                # Split at the end of the opening <a> tag
                split_idx = a_tag.find('>') + 1
                
                img_tag = ' <img src="assets/logo.webp" alt="RedTeam Hacker Academy" style="height:32px; border-radius:4px; vertical-align:middle; margin-right:8px;"> '
                
                return a_tag[:split_idx] + img_tag + a_tag[split_idx:]
            
            # This matches the full <a> tag that contains class="brand"
            pattern = re.compile(r'<a[^>]*class="[^"]*brand[^"]*"[^>]*>.*?</a>', re.DOTALL)
            
            new_content = pattern.sub(replace_logo, content)
            
            with open(filepath, 'w') as f:
                f.write(new_content)
                
print("A06 Logo injected.")
