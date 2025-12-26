import random
import string
from pathlib import Path

import pandas as pd


def generate_random_string(length):
    letters = string.ascii_letters + "_"
    return "".join(random.choice(letters) for _ in range(length))


def df_reader(file_path: str):
    file_path: Path = Path(file_path)
    if file_path.suffix.lower() == ".xlsx":
        engine = "calamine"
    elif file_path.suffix.lower() == ".xls":
        engine = "xlrd"
    elif file_path.suffix.lower() == ".xlsb":
        engine = "pyxlsb"
    else:
        engine = None  # let pandas decide
    return pd.read_excel(file_path, engine=engine)
