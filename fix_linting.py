#!/usr/bin/env python3
"""
Auto-fix linting issues for flake8 compliance
"""
import re
import os

def fix_file_linting(filepath):
    """Fix common linting issues in a Python file"""
    print(f"Fixing linting issues in {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix trailing whitespace (W291)
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Fix blank lines with whitespace (W293)
    content = re.sub(r'^[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Fix multiple statements on one line with colon (E701)
    # Handle if x: return y patterns
    content = re.sub(r'(\s+)if ([^:]+): return (.+)', r'\1if \2:\n\1    return \3', content)
    content = re.sub(r'(\s+)if ([^:]+): ([^r][^e][^t][^u][^r][^n].+)', r'\1if \2:\n\1    \3', content)
    
    # Fix line break after binary operator (W504) - move operator to next line
    content = re.sub(r'(\w+)\s+(and|or)\s*\n(\s+)', r'\1 \\\n\3\2 ', content)
    
    # Fix continuation line indentation (E128, E129)
    # This is complex and context-dependent, so we'll handle manually
    
    # Remove unused imports that are clearly unused
    # Remove unused 'time' import if it's there
    if 'import time' in content and 'time.' not in content and 'time(' not in content:
        content = re.sub(r'^import time\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^from .* import .*time.*\n', '', content, flags=re.MULTILINE)
    
    # Fix bare except statements (E722)
    content = re.sub(r'except:', 'except Exception:', content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Fixed basic linting issues in {filepath}")
        return True
    else:
        print(f"  ℹ️ No automatic fixes needed for {filepath}")
        return False

def main():
    files_to_fix = [
        'main.py',
        'config_manager.py', 
        'hack_data_manager.py'
    ]
    
    for filename in files_to_fix:
        if os.path.exists(filename):
            fix_file_linting(filename)
        else:
            print(f"⚠️ File not found: {filename}")

if __name__ == "__main__":
    main()
