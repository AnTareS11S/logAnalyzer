from analyzer.storage import (
    get_day_summary,
    get_days_with_min_errors,
    get_errors_by_day,
    get_stats,
    get_top_days,
    save_entries,
)


def test_save_entries_and_get_stats(conn, storage_entries):
    save_entries(storage_entries, conn)
    stats = get_stats(conn)

    expected_stats = [
        ("Timeout przy zapisie do bazy", 3),
        ("Brak polaczenia z baza WMSDB", 2),
        ("Utrata polaczenia sieciowego", 1),
    ]

    assert stats == expected_stats


def test_save_entries_count(conn, storage_entries):
    save_entries(storage_entries, conn)
    count = conn.execute("SELECT COUNT(*) FROM log_entries").fetchone()[0]

    assert count == 10


def test_save_entries_deduplication(conn, storage_entries):
    save_entries(storage_entries, conn)
    save_entries(storage_entries, conn)
    count = conn.execute("SELECT COUNT(*) FROM log_entries").fetchone()[0]

    assert count == 10


def test_save_entries_keeps_same_content_from_different_source_files(
    conn, storage_entries
):
    save_entries(storage_entries, conn)
    rows = conn.execute(
        "SELECT source_file FROM log_entries WHERE date = ? AND time = ? AND message = ?",
        ("2026-08-22", "10:05:00", "Timeout przy zapisie do bazy"),
    ).fetchall()

    assert sorted(row[0] for row in rows) == ["app.log", "wms.log"]


def test_get_errors_by_day(conn, storage_entries):
    save_entries(storage_entries, conn)
    result = get_errors_by_day(conn)

    assert result == [
        ("2026-08-20", 2),
        ("2026-08-22", 3),
        ("2026-08-23", 1),
    ]


def test_get_errors_by_day_ignores_days_without_errors(conn, storage_entries):
    save_entries(storage_entries, conn)
    result = get_errors_by_day(conn)

    assert "2026-08-21" not in [date for date, _ in result]


def test_get_top_days(conn, storage_entries):
    save_entries(storage_entries, conn)
    result = get_top_days(conn, 2)

    assert result == [
        ("2026-08-22", 3),
        ("2026-08-20", 2),
    ]


def test_get_top_days_limit_larger_than_available_days(conn, storage_entries):
    save_entries(storage_entries, conn)
    result = get_top_days(conn, 10)

    assert result == [
        ("2026-08-22", 3),
        ("2026-08-20", 2),
        ("2026-08-23", 1),
    ]


def test_get_top_days_zero_limit(conn, storage_entries):
    save_entries(storage_entries, conn)
    result = get_top_days(conn, 0)

    assert result == []


def test_get_days_with_min_errors(conn, storage_entries):
    save_entries(storage_entries, conn)
    result = get_days_with_min_errors(conn, 2)

    assert result == [
        ("2026-08-22", 3),
    ]


def test_get_days_with_min_errors_no_matches(conn, storage_entries):
    save_entries(storage_entries, conn)
    result = get_days_with_min_errors(conn, 10)

    assert result == []


def test_get_days_with_min_errors_all_days(conn, storage_entries):
    save_entries(storage_entries, conn)
    result = get_days_with_min_errors(conn, 0)

    assert sorted(result) == sorted(
        [
            ("2026-08-20", 2),
            ("2026-08-22", 3),
            ("2026-08-23", 1),
        ]
    )


def test_get_day_summary(conn, storage_entries):
    save_entries(storage_entries, conn)
    result = get_day_summary(conn, "2026-08-22")

    assert result == [
        ("Timeout przy zapisie do bazy", 2),
        ("Brak polaczenia z baza WMSDB", 1),
    ]
