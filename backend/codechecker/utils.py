import ast

def find_unused_imports(code):
    """
    Detect unused imports in the given code string.
    """
    try:
        tree = ast.parse(code)
        imports = [node for node in ast.walk(tree) if isinstance(node, ast.Import)]
        import_froms = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        all_imports = imports + import_froms

        used_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}

        unused_imports = []

        for node in all_imports:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        if alias.asname not in used_names:
                            unused_imports.append(alias.asname)
                    else:
                        if alias.name.split('.')[0] not in used_names:
                            unused_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.asname:
                        if alias.asname not in used_names:
                            unused_imports.append(alias.asname)
                    else:
                        if alias.name not in used_names:
                            unused_imports.append(alias.name)

        return unused_imports

    except Exception as e:
        return [f"Error analyzing imports: {e}"]
    

def remove_unused_imports(code):
    """
    Remove unused imports from the given code string.
    """
    try:
        tree = ast.parse(code)
        
        # Collect all import names
        all_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    all_imports.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    all_imports.append(alias.name.split('.')[0])
        
        # Collect all used names
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
        
        # Determine which imports are used
        used_imports = set()
        for name in all_imports:
            if name in used_names:
                used_imports.add(name)

        # Generate a new code string with only used imports
        new_code_lines = []
        lines = code.splitlines()
        inside_import_block = False
        
        for line in lines:
            if line.strip().startswith("import") or line.strip().startswith("from"):
                inside_import_block = True
                # Check if the import is used
                import_name = line.split()[1].split('.')[0]
                if import_name in used_imports:
                    new_code_lines.append(line)
            else:
                if inside_import_block:
                    inside_import_block = False
                new_code_lines.append(line)
        
        return "\n".join(new_code_lines)

    except Exception as e:
        return f"Error analyzing imports: {e}"