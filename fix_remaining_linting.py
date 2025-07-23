#!/usr/bin/env python3
"""
Fix remaining specific linting issues
"""
import re

def fix_remaining_linting_issues():
    """Fix the specific remaining linting issues"""
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Fix E303: too many blank lines - remove excessive blank lines before certain patterns
    # Look for patterns like if log: followed by multiple blank lines
    i = 0
    while i < len(lines):
        if i > 0 and lines[i-1].strip().endswith('log:'):
            # Count consecutive blank lines
            blank_count = 0
            j = i
            while j < len(lines) and lines[j].strip() == '':
                blank_count += 1
                j += 1
            
            # If more than 1 blank line, reduce to 0 (since next line should be indented log call)
            if blank_count > 1:
                # Remove extra blank lines
                del lines[i:i+blank_count]
                continue
        i += 1
    
    # Rejoin content
    content = '\n'.join(lines)
    
    # Fix W504: line break after binary operator
    # Pattern: word and\n or word or\n  
    content = re.sub(r'(\w+) (and|or) \\\n(\s+)', r'\1 \\\n\3\2 ', content)
    
    # Fix E502: the backslash is redundant between brackets
    # Remove backslashes when they're inside parentheses
    content = re.sub(r'\(([^)]*) \\\n([^)]*)\)', r'(\1\n\2)', content)
    
    # Fix comment indentation issues (E114, E117)
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Fix over-indented comments
        if re.match(r'^\s+# ', line):
            # Get the indentation level
            indent = len(line) - len(line.lstrip())
            # If indentation is not a multiple of 4, fix it
            if indent % 4 != 0:
                new_indent = (indent // 4) * 4
                if new_indent < 4:
                    new_indent = 4  # Minimum indentation for comments
                lines[i] = ' ' * new_indent + line.lstrip()
    
    content = '\n'.join(lines)
    
    # Save the fixed content
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed remaining linting issues")

if __name__ == "__main__":
    fix_remaining_linting_issues()
