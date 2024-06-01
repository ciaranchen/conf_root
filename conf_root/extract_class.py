import ast
import importlib.util
import os
import argparse

from conf_root import is_config_class

from conf_root.parse_field import dataclass_to_wtform
from conf_root.run_http import run_http


def extract_classes_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    tree = ast.parse(file_content)
    classes_name = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    # Dynamically import the module
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Load the classes from the module
    classes = [getattr(module, class_name, None) for class_name in classes_name]
    classes = [cls for cls in classes if cls is not None and is_config_class(cls)]
    return classes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help="提取配置类的文件名")
    parser.add_argument('--host', '-H', default='127.0.0.1', help='服务器的host')
    parser.add_argument('--port', '-P', default=8080, help='服务器的port')
    args = parser.parse_args()

    classes = extract_classes_from_file(args.filename)
    if len(classes) == 0:
        print(f"No classes found in {args.filename}.")
        return
    print(f"Configuration classes defined in {args.filename}: {classes}")
    forms = {cls: dataclass_to_wtform(cls) for cls in classes}
    run_http(forms, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
