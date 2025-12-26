from pathlib import Path
from unittest.mock import patch

from src.df_comparer import utils


def test_load_other_formats(tmp_path: Path):
    for ext, engine in {"xls": "xlrd", "xlsm": None, "xlsb": "pyxlsb"}.items():
        file_path = tmp_path / f"test_other_format.{ext}"
        file_path.touch()
        with patch("pandas.read_excel", return_value={}) as mock_read_excel:
            utils.df_reader(file_path)
            mock_read_excel.assert_called_once_with(file_path, engine=engine)
