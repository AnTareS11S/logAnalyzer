import argparse
import sqlite3
import sys
from contextlib import closing

from .analysis import filter_by_time, filter_errors, summarize
from .parser import read_file
from .storage import (
    count_entries,
    create_database,
    get_day_summary,
    get_days_with_min_errors,
    get_errors_by_day,
    get_stats,
    get_top_days,
    save_csv,
    save_entries,
)


def cmd_import(args):
    try:
        entries = read_file(args.filename)
    except FileNotFoundError:
        print(f"Błąd podczas odczytywania pliku: {args.filename}")
        return

    with closing(sqlite3.connect(args.db)) as conn:
        create_database(conn)
        save_entries(entries, conn)

def cmd_analyze(args):
    if (args.from_hour is None) != (args.to_hour is None):
        print("Musisz podać jednocześnie --from i --to.", file=sys.stderr)
        sys.exit(2)

    try:
        entries = read_file(args.filename)
    except FileNotFoundError:
        print(f"Błąd podczas odczytywania pliku: {args.filename}", file=sys.stderr)
        sys.exit(1)

    has_time_range = args.from_hour is not None and args.to_hour is not None

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
    

def cmd_stats(args):
    with closing(sqlite3.connect(args.db)) as conn:
        stats = get_stats(conn)
        total = count_entries(conn)

        print(f"STATYSTYKI Z BAZY ({total} wpisów):")
        for message, count in stats:
            print(f"{count}x {message}")

def cmd_by_day(args):
    with closing(sqlite3.connect(args.db)) as conn:
        by_day = get_errors_by_day(conn)
                
        print("BLEDY WG DNI:")
        for date, count in by_day:
            print(f"{date}: {count}")

def cmd_top_days(args):
    with closing(sqlite3.connect(args.db)) as conn:
        top_days = get_top_days(conn, args.limit)
            
        print(f"TOP {args.limit} DNI Z NAJWIEKSZA LICZBA BLEDOW:")
        for date, count in top_days:
            print(f"{date}: {count}")

def cmd_min_errors(args):
    with closing(sqlite3.connect(args.db)) as conn:
        min_errors = get_days_with_min_errors(conn, args.min_count)
        
        print(f"DNI Z LICZBA BLEDOW > {args.min_count}:")
        for date, count in min_errors:
            print(f"{date}: {count}")

def cmd_day_summary(args):
    with closing(sqlite3.connect(args.db)) as conn:
        day_summary = get_day_summary(conn, args.date)

        print(f"PODSUMOWANIE DLA DNIA {args.date}:")
        for message, count in day_summary:
            print(f"{count}x {message}")

def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    db_parser = argparse.ArgumentParser(add_help=False)
    db_parser.add_argument("--db", default="logs.db")

    import_parser = subparsers.add_parser("import", parents=[db_parser])
    import_parser.add_argument("filename")
    import_parser.set_defaults(func=cmd_import)
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("filename")
    analyze_parser.add_argument("--from", dest="from_hour")
    analyze_parser.add_argument("--to", dest="to_hour")
    analyze_parser.add_argument("--out")
    analyze_parser.set_defaults(func=cmd_analyze)
    stats_parser = subparsers.add_parser("stats", parents=[db_parser])
    stats_parser.set_defaults(func=cmd_stats)
    by_day_parser = subparsers.add_parser("by-day", parents=[db_parser])
    by_day_parser.set_defaults(func=cmd_by_day)
    top_days_parser = subparsers.add_parser("top-days", parents=[db_parser])
    top_days_parser.add_argument("limit", type=int)
    top_days_parser.set_defaults(func=cmd_top_days)
    min_errors_parser = subparsers.add_parser("min-errors", parents=[db_parser])
    min_errors_parser.add_argument("min_count", type=int)
    min_errors_parser.set_defaults(func=cmd_min_errors)
    day_parser = subparsers.add_parser("day", parents=[db_parser])
    day_parser.add_argument("date")
    day_parser.set_defaults(func=cmd_day_summary)

    args = parser.parse_args()     
    args.func(args)


if __name__ == "__main__":
    main()
