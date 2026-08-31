from analyzer.analysis import filter_by_time, filter_errors

def test_filter_errors_returns_only_errors():
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

    expected_result = [
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

    result = filter_errors(entries)
    assert result == expected_result



def test_empty_entries():
    entries = []
    result = filter_errors(entries)
    assert result == []

def test_no_errors():
    entries = [
        {
            "date": "2026-08-20",
            "time": "08:14:25",
            "level": "INFO",
            "message": "Brak polaczenia z baza WMSDB"
        },
        {
            "date": "2026-08-22",
            "time": "10:14:25",
            "level": "DEBUG",
            "message": "Brak polaczenia z baza WMSDB"
        },
        {
            "date": "2026-08-22",
            "time": "11:14:25",
            "level": "WARNING",
            "message": "Polaczenie z baza WMSDB nawiazane"
        }
    ]
    result = filter_errors(entries)
    assert result == []


def test_filter_by_time():
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

    from_hour = "09:00:00"
    to_hour = "11:00:00"

    expected_result = [
        {
            "date": "2026-08-22",
            "time": "10:14:25",
            "level": "ERROR",
            "message": "Brak polaczenia z baza WMSDB"
        }
    ]

    result = filter_by_time(entries, from_hour, to_hour)
    assert result == expected_result

def test_filter_by_time_empty_entries():
    entries = []

    result = filter_by_time(entries, "09:00:00", "11:00:00")

    assert result == []

def test_filter_by_time_no_matching_entries():
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

    from_hour = "12:00:00"
    to_hour = "13:00:00"

    result = filter_by_time(entries, from_hour, to_hour)

    assert result == []

def test_filter_by_time_entries_on_boundaries():
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

    from_hour = "10:14:25"
    to_hour = "11:14:25"

    expected_result = [
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

    result = filter_by_time(entries, from_hour, to_hour)
    assert result == expected_result