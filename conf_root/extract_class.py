import ast
import importlib.util
import os
import sys
from conf_root import is_config_class

from conf_root.parse_field import dataclass_to_wtform


def extract_classes_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    tree = ast.parse(file_content)
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    return classes


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_classes.py <path_to_python_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    classes_name = extract_classes_from_file(file_path)

    # Dynamically import the module
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Load the classes from the module
    classes = [getattr(module, class_name) for class_name in classes_name]

    if classes:
        print(f"Classes defined in {file_path}:")
        for cls in classes:
            if is_config_class(cls):
                form = dataclass_to_wtform(cls)
                print(form)

    else:
        print(f"No classes found in {file_path}.")


if __name__ == "__main__":
    main()
