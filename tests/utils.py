def replace_text(filename, origin_text, replace_text):
    with open(filename, 'r') as file:
        content = file.read()
    content = content.replace(origin_text, replace_text)
    with open(filename, 'w') as file:
        file.write(content)
