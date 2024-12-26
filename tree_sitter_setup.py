from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import re, json, os

PYTHON_LANGUAGE = Language(tspython.language())
parser = Parser(PYTHON_LANGUAGE)

def summarize_function_body(body_text):
    """
    Create a basic summary of what the function does based on its body.
    """
    summary = []
    if "return" in body_text:
        summary.append("returns a value")
    if "print" in body_text:
        summary.append("prints output")
    if re.search(r"\bif\b", body_text):
        summary.append("contains conditional statements")
    if re.search(r"\bfor\b|\bwhile\b", body_text):
        summary.append("contains loops")
    if re.search(r"\bdef\b", body_text):
        summary.append("defines a nested function")

    return "; ".join(summary) if summary else "function body not analyzed"

def extract_functions(node, source_code, parent_name=None):
    """
    Extracts function information from a tree-sitter AST node.
    """
    functions = []
    if node.type == "function_definition":
        name_node = node.child_by_field_name("name")
        function_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
        
        body_node = node.child_by_field_name("body")
        parameters_node = node.child_by_field_name("parameters")
        
        function_body_text = source_code[body_node.start_byte:body_node.end_byte].decode("utf-8")
        parameters = source_code[parameters_node.start_byte:parameters_node.end_byte].decode("utf-8")

        summary = summarize_function_body(function_body_text)
        
        function_info = {
            "name": function_name,
            "parent": parent_name,
            "parameters": parameters,
            "summary": summary,
            "children": []
        }

        for child in body_node.children:
            function_info["children"].extend(extract_functions(child, source_code, function_name))

        functions.append(function_info)
    else:
        for child in node.children:
            functions.extend(extract_functions(child, source_code, parent_name))
    return functions

def extract_classes(node, source_code):
    """
    Extracts class information from a tree-sitter AST node.
    """
    classes = []
    if node.type == "class_definition":
        name_node = node.child_by_field_name("name")
        class_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")

        body_node = node.child_by_field_name("body")
        
        class_info = {
            "class_name": class_name,
            "methods": [],
            "children": []
        }

        # Extract functions within the class
        for child in body_node.children:
            class_info["methods"].extend(extract_functions(child, source_code, class_name))

        classes.append(class_info)
    else:
        for child in node.children:
            classes.extend(extract_classes(child, source_code))
    return classes

def extract_imports(node, source_code):
    """
    Extracts import statements from the tree-sitter AST node.
    """
    imports = []
    if node.type == "import_statement" or node.type == "import_from_statement":
        # Get the full import statement text
        import_text = source_code[node.start_byte:node.end_byte].decode("utf-8")
        imports.append(import_text)
    else:
        for child in node.children:
            imports.extend(extract_imports(child, source_code))
    return imports

def func(node, source_code, func_names):
  if(node.type=="function_definition"):
    name_node = node.child_by_field_name("name")
    func_names.append(source_code[name_node.start_byte:name_node.end_byte].decode("utf-8"))
  else:
    for child in node.children:
      func(child, source_code, func_names)

def relate(node, source_code, relations, func_names):
    if node.type == "function_definition":
        name_node = node.child_by_field_name("name")
        function_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
        relations[function_name] = []

        body_node = node.child_by_field_name("body")
        find_calls(body_node, function_name, source_code, relations, func_names)

    for child in node.children:
        relate(child, source_code, relations, func_names)
    return

def find_calls(node, function_name, source_code, relations, func_names):
    if node.type == "call":
        func_node = node.child_by_field_name("function")
        if func_node and func_node.type == "identifier":
            call_name = source_code[func_node.start_byte:func_node.end_byte].decode("utf-8")
            if call_name in func_names:
                relations[function_name].append(call_name)
    for child in node.children:
        find_calls(child, function_name, source_code, relations, func_names)

def parse_file(file_path):
    with open(file_path, "rb") as f:
        source_code = f.read()
    
    tree = parser.parse(source_code)
    root_node = tree.root_node
    
    # Extract classes and standalone functions in the file
    classes = extract_classes(root_node, source_code)
    functions = extract_functions(root_node, source_code)
    imports = extract_imports(root_node, source_code)

    func_names = []
    func(root_node, source_code, func_names)

    relations = {}
    for f in func_names:
        relations[f] = []
    relate(root_node, source_code, relations, func_names)
    
    for f in functions:
        f["related_functions"] = relations[f["name"]]

    return {
        "imports":imports,
        "classes": classes,
        "functions": functions  # standalone functions not inside any class
    }

def main(directory = 'codebase'):
    data = {}
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            file_path = os.path.join(directory, filename)
            data[filename] = parse_file(file_path)
    
    # Save to JSON or print
    with open("AST.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == '__main__':
    main()