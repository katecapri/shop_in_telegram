from datetime import datetime


def save_log_file(error_text, func_name):
    file_name = f"{datetime.now()} - {func_name}"
    with open(f"/application/src/logs/{file_name}", "w") as file:
        file.write(str(error_text))
