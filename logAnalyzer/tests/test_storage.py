from analyzer.storage import save_entries, get_stats

def test_save_entries_and_get_stats(conn, sample_entries):
    save_entries(sample_entries, conn)
    stats = get_stats(conn)

    expected_stats = [
        ("Brak polaczenia z baza WMSDB", 2),
        ("Polaczenie z baza WMSDB nawiazane", 1)
    ]

    assert stats == expected_stats

def test_save_entries_count(conn, sample_entries):
    save_entries(sample_entries, conn)
    count = conn.execute("SELECT COUNT(*) FROM log_entries").fetchone()[0]

    assert count == 4

def test_save_entries_deduplication(conn, sample_entries):
    save_entries(sample_entries, conn)
    save_entries(sample_entries, conn)
    count = conn.execute("SELECT COUNT(*) FROM log_entries").fetchone()[0]

    assert count == 4