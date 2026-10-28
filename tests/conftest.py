import pytest
from src.sinks.store import Store

@pytest.fixture
def store(tmp_path):
    return Store("sqlite:///" + str(tmp_path / "test.db"))
