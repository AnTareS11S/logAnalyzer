import sys

def parse_line(line):
    """Zamienia pojedynczą linię logu na słownik {date, time, level, message} albo None, jeśli linia jest niepoprawna."""
    parts = line.split()
    if len(parts) <  4:
        # Za mało pól, żeby zbudować poprawny wpis (np. pusta linia) - pomijamy ją
        return None
    entry = {
                "date": parts[0],                # zakładany format: <data> <czas> <poziom> <wiadomość...>
                "time": parts[1],
                "level": parts[2],
                "message": " ".join(parts[3:])   # reszta linii sklejona z powrotem jako treść komunikatu
            }
    return entry

def read_file(filename):
    """Czyta plik logu i zwraca listę sparsowanych wpisów.
    Jeśli plik nie istnieje, wypisuje komunikat i kończy program (sys.exit(1) = zakończenie z kodem błędu)."""
    try:
        with open(filename, encoding="utf-8") as file:
            entries = []
            for line in file:
                result = parse_line(line)
                if result is None:
                    continue
                entries.append(result)
            return entries
    except FileNotFoundError:
        print(f"Nie znaleziono pliku: {filename}")
        sys.exit(1)