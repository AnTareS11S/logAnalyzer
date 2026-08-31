import argparse
import sqlite3

from .parser import read_file
from .analysis import filter_errors, summarize, filter_by_time
from .storage import save_csv, create_database, save_entries, get_stats, count_entries


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("filename")                   
    parser.add_argument("--from", dest="from_hour")     
                                                         
    parser.add_argument("--to", dest="to_hour")
    parser.add_argument("--out")                        
    parser.add_argument("--db", default="logs.db")      
    parser.add_argument("--save", action="store_true")  
    parser.add_argument("--stats", action="store_true") 

    args = parser.parse_args()

    if (args.from_hour is None) != (args.to_hour is None):
        parser.error("Musisz podać jednocześnie --from i --to.")

    has_time_range = args.from_hour is not None and args.to_hour is not None

    entries = read_file(args.filename)

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

    finally:
        conn.close()

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

if __name__ == "__main__":
    main()