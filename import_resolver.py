import re

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
    stdlib_imports = []
    third_party_imports = []
    local_imports = []
    
    # Common standard library modules
    stdlib_modules = [
        'abc', 'argparse', 'array', 'asyncio', 'base64', 'collections', 'copy', 
        'csv', 'datetime', 'decimal', 'enum', 'functools', 'glob', 'io', 'itertools', 
        'json', 'logging', 'math', 'os', 'pathlib', 're', 'random', 'shutil', 'socket', 
        'sqlite3', 'string', 'sys', 'tempfile', 'threading', 'time', 'typing', 'unittest', 
        'urllib', 'uuid', 'warnings', 'weakref', 'xml', 'zipfile'
    ]
    
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
            elif module.startswith(('app', 'project')):  # Customize for your project
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

def resolve_import_conflicts(content):
    """Resolve import order conflicts in the given file content."""
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
    return resolved_content