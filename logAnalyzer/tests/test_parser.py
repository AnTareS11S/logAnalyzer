from analyzer.parser import parse_line

def test_correct_line():
    line = "2026-08-20 08:14:25 ERROR Brak polaczenia z baza WMSDB"
    result = parse_line(line)
    assert result["time"] == "08:14:25"
    assert result["level"] == "ERROR"
    assert result["message"] == "Brak polaczenia z baza WMSDB"

def test_short_line():
    line = "ERROR"
    result = parse_line(line)
    assert result is None

def test_empty_line():
    line = ""
    result = parse_line(line)
    assert result is None

def test_whitespaces_line():
    line = "2026-08-20 08:14:25 ERROR Brak      polaczenia"
    result = parse_line(line)
    assert result["time"] == "08:14:25"
    assert result["level"] == "ERROR"
    assert result["message"] == "Brak      polaczenia"