import argparse
import sqlite3

from .parser import read_file
from .analysis import filter_errors, summarize, filter_by_time
from .storage import (
    save_csv,
    create_database,
    save_entries,
    get_stats,
    count_entries,
    get_errors_by_day,
    get_top_days,
    get_days_with_min_errors,
    get_day_summary,
)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("filename", help="ścieżka do pliku logu lub katalogu z plikami *.log")
    parser.add_argument("--from", dest="from_hour", help="początek zakresu czasu, format HH:MM:SS (wymaga --to)")

    parser.add_argument("--to", dest="to_hour", help="koniec zakresu czasu, format HH:MM:SS (wymaga --from)")
    parser.add_argument("--out", help="ścieżka do pliku CSV, do którego zapisane zostanie podsumowanie")
    parser.add_argument("--db", default="logs.db", help="ścieżka do pliku bazy SQLite (domyślnie logs.db)")
    parser.add_argument("--save", action="store_true", help="zapisuje wczytane wpisy do bazy danych")
    parser.add_argument("--stats", action="store_true", help="wypisuje statystyki błędów odczytane z bazy danych")
    parser.add_argument("--by-day", action="store_true", help="wypisuje liczbę błędów w bazie danych dla każdego dnia")
    parser.add_argument("--top-days", type=int, metavar="N", help="wypisuje N dni z bazy danych z największą liczbą błędów")
    parser.add_argument("--min-errors", type=int, metavar="N", help="wypisuje dni z bazy danych z liczbą błędów większą niż N")
    parser.add_argument("--day", metavar="DATA", help="wypisuje podsumowanie wszystkich wpisów z bazy danych dla podanego dnia (format YYYY-MM-DD)")

    args = parser.parse_args()

    if (args.from_hour is None) != (args.to_hour is None):
        parser.error("Musisz podać jednocześnie --from i --to.")

    has_time_range = args.from_hour is not None and args.to_hour is not None

    try:
        entries = read_file(args.filename)
    except FileNotFoundError:
        print(f"Błąd podczas odczytywania pliku: {args.filename}")
        return

    conn = sqlite3.connect(args.db)

    try:
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

            if args.by_day:
                by_day = get_errors_by_day(conn)

                print("BLEDY WG DNI:")
                for date, count in by_day:
                    print(f"{date}: {count}")

            if args.top_days is not None:
                top_days = get_top_days(conn, args.top_days)

                print(f"TOP {args.top_days} DNI Z NAJWIEKSZA LICZBA BLEDOW:")
                for date, count in top_days:
                    print(f"{date}: {count}")

            if args.min_errors is not None:
                days_over_threshold = get_days_with_min_errors(conn, args.min_errors)

                print(f"DNI Z LICZBA BLEDOW > {args.min_errors}:")
                for date, count in days_over_threshold:
                    print(f"{date}: {count}")

            if args.day:
                day_summary = get_day_summary(conn, args.day)

                print(f"PODSUMOWANIE DLA DNIA {args.day}:")
                for message, count in day_summary:
                    print(f"{count}x {message}")

    finally:
        conn.close()

    errors = filter_errors(entries)
    summary_data = summarize(errors)

    if has_time_range:
        filtered_errors = filter_by_time(errors, args.from_hour, args.to_hour)

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


if __name__ == "__main__":
    main()
