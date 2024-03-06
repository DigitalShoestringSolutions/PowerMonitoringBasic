import os
import ast
import pathlib 
import packaging.version

def collect_requirements():
    print("Starting...")
    module_paths = get_module_path_list()
    print(f"Collected modules:\n{module_paths}")
    all_requirements = fetch_all_requirements(module_paths)
    print(f"\nAll requirements:\n{all_requirements}")
    final_requirements = reconcile_requirements_sets(all_requirements)
    print(f"\nFinal requirements:\n{final_requirements}")
    write_to_file('./generated_requirements.txt',final_requirements)
    print("\nOutput to file: ")
    print(pathlib.Path('./generated_requirements.txt').read_text())
    print("\nFinished")

def get_module_path_list():
    module_paths = []
    for root, dirs, files in os.walk('./core'):
        for file in files:
            fullpath = os.path.join(root,file)
            filename, ext = os.path.splitext(file)
            if ext.lower() == '.py' and filename != "__init__":
                module_paths.append(fullpath)

    return module_paths

def fetch_all_requirements(module_paths):
    all_results = {}
    for path in module_paths:
        result = extract_pip_requirements_dict(path)
        # combine all requirements - using a set to capture multiple version requirements for the same library
        for k,v in result.items():
            if k not in all_results:
                all_results[k] = set()
            all_results[k].add(v)
    return all_results

def extract_pip_requirements_dict(path):
    ast_tree = ast.parse(pathlib.Path(path).read_text())  # read file and compile into Abstract Syntax Tree
    for node in ast_tree.body:  # Look at top level in module
        if isinstance(node, ast.Assign): # If a variable assignment
            if isinstance(node.value,ast.Dict): # If assigned value was a dict
                if node.targets[0].id == "pip_requirements": # if variable name is "pip_requirements"
                    return eval(compile(ast.Expression(node.value), "<ast expression>", "eval")) # Recompile the AST expression into a dict
    return {}

def reconcile_requirements_sets(set_dict):
    reconciled = {}
    for key,set in set_dict.items():
        versions = {packaging.version.parse(v_string) for v_string in set}
        reconciled[key] = max(versions)
    return reconciled
         
def write_to_file(filename, requirements):
    with open(filename, "w") as f:
        for library, version in requirements.items():
            f.write(f"{library}=={version}\n")



if __name__ == "__main__":
    collect_requirements()
