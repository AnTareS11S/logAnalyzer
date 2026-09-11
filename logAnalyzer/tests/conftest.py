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
        {
            "date": "2026-08-20",
            "time": "08:14:25",
            "level": "ERROR",
            "message": "Brak polaczenia z baza WMSDB",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-22",
            "time": "10:14:25",
            "level": "ERROR",
            "message": "Brak polaczenia z baza WMSDB",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-22",
            "time": "11:14:25",
            "level": "ERROR",
            "message": "Polaczenie z baza WMSDB nawiazane",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-22",
            "time": "11:15:25",
            "level": "INFO",
            "message": "Polaczenie z baza WMSDB nawiazane",
            "source_file": "wms.log",
        },
    ]


@pytest.fixture
def sample_entries_no_errors():
    return [
        {
            "date": "2026-08-20",
            "time": "08:14:25",
            "level": "DEBUG",
            "message": "Polaczenie z baza WMSDB",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-22",
            "time": "10:14:25",
            "level": "INFO",
            "message": "Polaczenie z baza WMSDB",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-22",
            "time": "11:14:25",
            "level": "DEBUG",
            "message": "Polaczenie z baza WMSDB nawiazane",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-22",
            "time": "11:15:25",
            "level": "INFO",
            "message": "Polaczenie z baza WMSDB nawiazane",
            "source_file": "wms.log",
        },
    ]


@pytest.fixture
def storage_entries():
    """Bogatszy zestaw wpisów do testow storage.py: kilka dni z rozna liczba
    bledow (w tym dzien bez zadnego bledu), powtarzajace sie tresci komunikatow
    oraz dwa wpisy o identycznych date/time/level/message ale roznym source_file
    (test unikalnosci wpisu z uwzglednieniem source_file)."""
    return [
        {
            "date": "2026-08-20",
            "time": "08:00:00",
            "level": "ERROR",
            "message": "Brak polaczenia z baza WMSDB",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-20",
            "time": "08:05:00",
            "level": "ERROR",
            "message": "Timeout przy zapisie do bazy",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-20",
            "time": "09:00:00",
            "level": "INFO",
            "message": "Polaczenie z baza WMSDB nawiazane",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-21",
            "time": "07:00:00",
            "level": "WARNING",
            "message": "Wolne zapytanie SQL",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-21",
            "time": "07:30:00",
            "level": "DEBUG",
            "message": "Sprawdzanie stanu polaczenia",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-22",
            "time": "10:00:00",
            "level": "ERROR",
            "message": "Brak polaczenia z baza WMSDB",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-22",
            "time": "10:05:00",
            "level": "ERROR",
            "message": "Timeout przy zapisie do bazy",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-22",
            "time": "10:05:00",
            "level": "ERROR",
            "message": "Timeout przy zapisie do bazy",
            "source_file": "app.log",
        },
        {
            "date": "2026-08-22",
            "time": "11:00:00",
            "level": "INFO",
            "message": "Polaczenie z baza WMSDB nawiazane",
            "source_file": "wms.log",
        },
        {
            "date": "2026-08-23",
            "time": "06:00:00",
            "level": "ERROR",
            "message": "Utrata polaczenia sieciowego",
            "source_file": "wms.log",
        },
    ]
