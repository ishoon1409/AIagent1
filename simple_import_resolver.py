#!/usr/bin/env python3
import re
import sys

def extract_imports(text):
    """Extract import statements from a block of text."""
    imports = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('import ') or line.startswith('from '):
            imports.append(line)
    return imports

def sort_imports(imports):
    """Sort imports according to PEP 8 guidelines."""
    stdlib_modules = ['os', 'sys', 'datetime', 'time', 'json', 're', 'math', 'random', 
                      'collections', 'functools', 'itertools', 'pathlib', 'shutil', 
                      'argparse', 'logging']
    
    stdlib_imports = []
    third_party_imports = []
    local_imports = []
    
    for imp in imports:
        if imp.startswith('import '):
            module = imp.split()[1].split('.')[0]
            if module in stdlib_modules:
                stdlib_imports.append(imp)
            else:
                third_party_imports.append(imp)
        elif imp.startswith('from '):
            module = imp.split()[1].split('.')[0]
            if module in stdlib_modules:
                stdlib_imports.append(imp)
            elif module == 'app' or module.startswith('app.'):
                local_imports.append(imp)
            else:
                third_party_imports.append(imp)
    
    # Sort each group alphabetically
    stdlib_imports.sort()
    third_party_imports.sort()
    local_imports.sort()
    
    # Combine groups with blank lines between them
    result = stdlib_imports[:]
    if stdlib_imports and third_party_imports:
        result.append('')
    result.extend(third_party_imports)
    if (stdlib_imports or third_party_imports) and local_imports:
        result.append('')
    result.extend(local_imports)
    
    return result

def resolve_import_conflicts(file_path):
    """Resolve import order conflicts in the given file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex to find git merge conflict markers with their content
        conflict_pattern = re.compile(
            r'<<<<<<< .*?\n(.*?)\n=======\n(.*?)\n>>>>>>> .*?\n', 
            re.DOTALL
        )
        
        def resolve_conflict(match):
            head_content = match.group(1)
            feature_content = match.group(2)
            
            # Extract imports from both branches
            head_imports = extract_imports(head_content)
            feature_imports = extract_imports(feature_content)
            
            # Combine unique imports
            all_imports = []
            for imp in head_imports + feature_imports:
                if imp not in all_imports:
                    all_imports.append(imp)
            
            # Sort according to PEP 8
            sorted_imports = sort_imports(all_imports)
            
            # Return the sorted imports as a string
            return '\n'.join(sorted_imports)
        
        # Replace each conflict with the resolved imports
        resolved_content = conflict_pattern.sub(resolve_conflict, content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(resolved_content)
        
        print(f"Successfully resolved import conflicts in {file_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python simple_import_resolver.py <file.py>")
    else:
        file_path = sys.argv[1]
        resolve_import_conflicts(file_path)