import json
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def mocks_folder_path():
    """Fixture to provide the path to the mocks folder."""
    return Path(__file__).parent / "mocks"


@pytest.fixture
def open_mock_file(mocks_folder_path: Path):
    """
    Fixture that returns a callable to open mock files relative to the mocks folder.
    """

    def _open_mock_file(filename: str, mode: str = "r", encoding: str = "utf-8"):
        """
        The actual utility function, simplified for tests.
        """
        filepath = mocks_folder_path / filename

        # Ensure the file exists before opening (good practice)
        if not filepath.exists():
            raise FileNotFoundError(f"Mock file not found: {filepath}")

        with open(filepath, mode, encoding=encoding) as f:
            content = f.read()

        if ".json" in filename:
            return json.loads(content)

        return content

    return _open_mock_file
