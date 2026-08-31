import sqlite3
import pytest
from analyzer.storage import create_database

@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    create_database(connection)
    yield connection
    connection.close()

@pytest.fixture
def sample_entries():
    return [
        {"date": "2026-08-20", "time": "08:14:25", "level": "ERROR",
         "message": "Brak polaczenia z baza WMSDB"},
        {"date": "2026-08-22", "time": "10:14:25", "level": "ERROR",
         "message": "Brak polaczenia z baza WMSDB"},
        {"date": "2026-08-22", "time": "11:14:25", "level": "ERROR",
         "message": "Polaczenie z baza WMSDB nawiazane"},
        {"date": "2026-08-22", "time": "11:14:25", "level": "INFO",
         "message": "Polaczenie z baza WMSDB nawiazane"},
    ]