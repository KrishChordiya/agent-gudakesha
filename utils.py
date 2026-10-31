def get_prompt(file_path):
    try:
        with open("prompts/"+file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt {file_path} does not exits")
        