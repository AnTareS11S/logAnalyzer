import sqlite3

from analyzer.storage import save_entries, get_stats, create_database

def test_save_entries_and_get_stats():
    conn = sqlite3.connect(":memory:")
   
    create_database(conn)
    entries = [
        {
            "date": "2026-08-20",
            "time": "08:14:25",
            "level": "ERROR",
            "message": "Brak polaczenia z baza WMSDB"
        },
        {
            "date": "2026-08-22",
            "time": "10:14:25",
            "level": "ERROR",
            "message": "Brak polaczenia z baza WMSDB"
        },
        {
            "date": "2026-08-22",
            "time": "11:14:25",
            "level": "ERROR",
            "message": "Polaczenie z baza WMSDB nawiazane"
        },
        {
            "date": "2026-08-22",
            "time": "11:14:25",
            "level": "INFO",
            "message": "Polaczenie z baza WMSDB nawiazane"
        }
    ]

    save_entries(entries, conn)
    stats = get_stats(conn)

    expected_stats = [
        ("Brak polaczenia z baza WMSDB", 2),
        ("Polaczenie z baza WMSDB nawiazane", 1)
    ]

    assert stats == expected_stats

def test_save_entries_count():
    conn = sqlite3.connect(":memory:")
    create_database(conn)
    entries = [
        {
            "date": "2026-08-20",
            "time": "08:14:25",
            "level": "ERROR",
            "message": "Brak polaczenia z baza WMSDB"
        },
        {
            "date": "2026-08-22",
            "time": "10:14:25",
            "level": "ERROR",
            "message": "Brak polaczenia z baza WMSDB"
        },
        {
            "date": "2026-08-22",
            "time": "11:14:25",
            "level": "ERROR",
            "message": "Polaczenie z baza WMSDB nawiazane"
        }
    ]

    save_entries(entries, conn)
    count = conn.execute("SELECT COUNT(*) FROM log_entries").fetchone()[0]

    assert count == 3

def test_save_entries_deduplication():
    conn = sqlite3.connect(":memory:")
    create_database(conn)
    entries = [
        {
            "date": "2026-08-20",
            "time": "08:14:25",
            "level": "ERROR",
            "message": "Brak polaczenia z baza WMSDB"
        },
        {
            "date": "2026-08-22",
            "time": "10:14:25",
            "level": "ERROR",
            "message": "Niepoprawny wpis do testu deduplikacji"
        }
    ]

    save_entries(entries, conn)
    save_entries(entries, conn) 
    count = conn.execute("SELECT COUNT(*) FROM log_entries").fetchone()[0]

    assert count == 2