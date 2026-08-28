import argparse
import csv
from collections import Counter
import sys
import sqlite3

def parse_line(line):
    parts = line.split()
    if len(parts) <  4:
        return None
    entry = {
                "date": parts[0],
                "time": parts[1],
                "level": parts[2],
                "message": " ".join(parts[3:])
            }
    return entry

def read_file(filename): 
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
    return [entry for entry in entries if entry['level'] == "ERROR"]

def filter_by_time(entries, from_hour, to_hour):
    return [entry for entry in entries if from_hour <= entry['time'] <= to_hour]

def summarize(errors):
    return Counter(error['message'] for error in errors).most_common()

def save_csv(summary_data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile: 
        writer = csv.writer(csvfile)
        writer.writerow(["message", "count"])
        for message, count in summary_data:
            writer.writerow([message, count])

def create_database(conn):
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS log_entries (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, time TEXT, level TEXT, message TEXT, UNIQUE(date, time, level, message))')

def save_entries(entries, conn):
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
    cursor = conn.cursor()
    cursor.execute("""SELECT message, COUNT(*) FROM log_entries WHERE level = ? GROUP BY message ORDER BY COUNT(*) DESC """, ("ERROR",))
    return cursor.fetchall()


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

                print("STATYSTYKI Z BAZY:")
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