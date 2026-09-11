from pathlib import Path


def parse_line(line):
    """Zamienia pojedynczą linię logu na słownik {date, time, level, message} albo None, jeśli linia jest niepoprawna."""
    parts = line.strip().split(maxsplit=3)
    if len(parts) < 4:
        # Za mało pól, żeby zbudować poprawny wpis (np. pusta linia) - pomijamy ją
        return None
    entry = {
        "date": parts[0],  # zakładany format: <data> <czas> <poziom> <wiadomość...>
        "time": parts[1],
        "level": parts[2],
        "message": parts[3],
    }
    return entry


def read_single_file(filename):
    """Czyta plik logu i zwraca listę sparsowanych wpisów."""
    with open(filename, encoding="utf-8") as file:
        entries = []
        for line in file:
            result = parse_line(line)
            if result is None:
                continue
            result["source_file"] = Path(filename).name
            entries.append(result)
        return entries


def read_file(filename):
    path = Path(filename)

    if path.is_dir():
        all_entries = []

        for log_file in path.glob("*.log"):
            entries = read_single_file(log_file)
            all_entries.extend(entries)

        return all_entries
    else:
        return read_single_file(filename)
