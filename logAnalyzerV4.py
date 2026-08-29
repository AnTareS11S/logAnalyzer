import argparse   # do obsługi argumentów podawanych w linii poleceń (np. --from 08:00:00)
import csv        # do zapisu podsumowania do pliku .csv
from collections import Counter  # gotowa klasa do zliczania wystąpień elementów
import sys        # do zakończenia programu (sys.exit) w razie błędu
import sqlite3    # wbudowana baza danych SQLite - zapisywanie wpisów logu na trwałe

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

def filter_errors(entries):
    """Zwraca tylko wpisy o poziomie ERROR (list comprehension - skrócona wersja pętli for)."""
    return [entry for entry in entries if entry['level'] == "ERROR"]

def filter_by_time(entries, from_hour, to_hour):
    """Zwraca wpisy, których czas mieści się w przedziale [from_hour, to_hour] (włącznie).
    Porównanie stringów "HH:MM:SS" działa leksykograficznie jak liczby, ale tylko w obrębie jednej doby."""
    return [entry for entry in entries if from_hour <= entry['time'] <= to_hour]

def summarize(errors):
    """Liczy wystąpienia każdej unikalnej treści błędu i zwraca listę (treść, liczba)
    posortowaną malejąco wg liczby wystąpień (Counter.most_common())."""
    return Counter(error['message'] for error in errors).most_common()

def save_csv(summary_data, filename):
    """Zapisuje podsumowanie błędów do pliku CSV z kolumnami: message, count."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["message", "count"])  # nagłówek pliku CSV
        for message, count in summary_data:
            writer.writerow([message, count])

def create_database(conn):
    """Tworzy tabelę log_entries, jeśli jeszcze nie istnieje.
    UNIQUE(date, time, level, message) sprawia, że baza sama pilnuje unikalności wpisu -
    ta sama kombinacja tych czterech pól nie może się powtórzyć (patrz save_entries)."""
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS log_entries (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, time TEXT, level TEXT, message TEXT, UNIQUE(date, time, level, message))')

def save_entries(entries, conn):
    """Zapisuje listę wpisów do bazy danych za jednym razem (executemany = wiele wstawień w jednym wywołaniu,
    szybsze niż osobny INSERT dla każdego wpisu w pętli).
    Znaki zapytania (?) w zapytaniu SQL to placeholdery - biblioteka sama bezpiecznie
    podstawia w ich miejsce wartości z krotek, chroniąc przed SQL injection.
    "INSERT OR IGNORE" oznacza: jeśli wpis o takich samych (date, time, level, message)
    już istnieje w bazie (patrz UNIQUE w create_database), po prostu go pomiń zamiast rzucać błąd.
    Dzięki temu można bezpiecznie uruchamiać --save wielokrotnie na tym samym pliku
    bez duplikowania wpisów."""
    cursor = conn.cursor()
    cursor.executemany("""INSERT OR IGNORE INTO log_entries (date, time, level, message) VALUES (?, ?, ?, ?) """, [(
        entry['date'],
        entry['time'],
        entry['level'],
        entry['message']
    )
        for entry in entries
    ])

def get_stats(conn):
    """Pobiera z bazy statystyki błędów: dla każdej unikalnej treści komunikatu z poziomem ERROR
    liczy, ile razy wystąpiła (GROUP BY message), i sortuje malejąco wg tej liczby.
    Znak zapytania (?) jest tu bezpiecznie podstawiony wartością "ERROR" z drugiego argumentu execute()."""
    cursor = conn.cursor()
    cursor.execute("""SELECT message, COUNT(*) FROM log_entries WHERE level = ? GROUP BY message ORDER BY COUNT(*) DESC """, ("ERROR",))
    return cursor.fetchall()

def count_entries(conn):
    """Zwraca całkowitą liczbę wszystkich wpisów w tabeli log_entries.
    fetchone() zwraca jeden wiersz wyniku jako krotkę, np. (42,) - stąd [0], żeby wyciągnąć samą liczbę."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM log_entries")
    return cursor.fetchone()[0]

def main():
    # Konfiguracja argumentów wywołania programu z linii poleceń, np.:
    # python logAnalyzerV4.py wms.log --save --stats --db logs.db --from 08:15:00 --to 08:20:00 --out summary.csv
    parser = argparse.ArgumentParser()

    parser.add_argument("filename")                    # argument pozycyjny - ścieżka do pliku logu
    parser.add_argument("--from", dest="from_hour")     # "--from" jest słowem kluczowym w Pythonie,
                                                         # dlatego wynik trzeba zapisać pod inną nazwą (dest="from_hour")
    parser.add_argument("--to", dest="to_hour")
    parser.add_argument("--out")                        # opcjonalna ścieżka do zapisu wyniku jako CSV
    parser.add_argument("--db", default="logs.db")      # ścieżka do pliku bazy SQLite (domyślnie logs.db)
    parser.add_argument("--save", action="store_true")  # flaga bez wartości: obecność "--save" ustawia True
    parser.add_argument("--stats", action="store_true") # flaga bez wartości: obecność "--stats" ustawia True

    args = parser.parse_args()

    # Sprawdzenie "XOR": błąd, jeśli podano TYLKO jeden z --from/--to (a nie oba albo żaden).
    if (args.from_hour is None) != (args.to_hour is None):
        parser.error("Musisz podać jednocześnie --from i --to.")

    # Flaga informująca, czy użytkownik w ogóle poprosił o filtrowanie po czasie
    has_time_range = args.from_hour is not None and args.to_hour is not None

    entries = read_file(args.filename)

    # Otwarcie (lub utworzenie, jeśli nie istnieje) pliku bazy danych SQLite
    conn = sqlite3.connect(args.db)

    try:
        # "with conn:" otacza operacje transakcją: jeśli wszystko pójdzie dobrze,
        # zmiany są automatycznie zatwierdzane (commit); jeśli wystąpi wyjątek,
        # wszystkie zmiany w tym bloku są wycofywane (rollback).
        with conn:
            create_database(conn)

            if args.save:
                save_entries(entries, conn)

            if args.stats:
                stats = get_stats(conn)
                total = count_entries(conn)

                print(f"STATYSTYKI Z BAZY ({total} wpisów):")
                for message, count in stats:
                    print(f"{count}x {message}")

    finally:
        # Połączenie z bazą zamykamy zawsze, niezależnie od tego, czy blok try się powiódł, czy nie
        conn.close()

    # Poniższa część działa niezależnie od bazy danych - liczy statystyki
    # bezpośrednio z wpisów wczytanych z pliku logu w tym uruchomieniu
    errors = filter_errors(entries)
    summary_data = summarize(errors)

    if has_time_range:
        filtered_errors = filter_by_time(
            errors,
            args.from_hour,
            args.to_hour
        )

    print("PODSUMOWANIE (caly plik):")
    for key, value in summary_data:
        print(f"{value}x {key}")

    if has_time_range:
        print(f"BLEDY {args.from_hour} - {args.to_hour}")

        if not filtered_errors:
            print("Nie ma żadnych błędów")
        else:
            for error in filtered_errors:
                print(f"{error['time']} {error['message']}")

    if args.out:
        save_csv(summary_data, args.out)

# Ten warunek sprawia, że main() uruchomi się tylko wtedy, gdy plik jest odpalony
# bezpośrednio (np. "python logAnalyzerV4.py ..."), a nie gdy jest importowany jako moduł w innym pliku.
if __name__ == "__main__":
    main()