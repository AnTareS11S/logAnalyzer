import csv


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