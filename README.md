# analyzer

Pakiet Pythona do analizy logów magazynowych. Wczytuje plik logu, wyszukuje w nim błędy (`ERROR`), pozwala je filtrować po zakresie czasu, tworzy podsumowanie najczęściej występujących błędów oraz umożliwia zapis wyników do pliku CSV lub bazy danych SQLite.

## Uruchamianie

Ponieważ `cli.py` używa importów względnych (`from .parser import ...`), plik należy uruchamiać jako moduł pakietu, z katalogu nadrzędnego (`logAnalyzer/`):

```bash
python -m analyzer.cli <polecenie> [opcje]
```

### Dostępne polecenia

| Polecenie                   | Opis                                                                                   |
| ---------------------------- | ---------------------------------------------------------------------------------------|
| `analyze <plik>`             | wczytuje plik logu i wypisuje podsumowanie błędów (opcjonalnie w zakresie czasu)       |
| `import <plik>`              | wczytuje plik logu i zapisuje wpisy do bazy SQLite                                     |
| `stats`                      | wypisuje statystyki błędów odczytane z bazy danych                                     |
| `by-day`                     | wypisuje liczbę błędów w bazie danych dla każdego dnia                                 |
| `top-days <N>`               | wypisuje N dni z bazy danych z największą liczbą błędów                                |
| `min-errors <N>`             | wypisuje dni z bazy danych z liczbą błędów większą niż N                               |
| `day <DATA>`                 | wypisuje podsumowanie błędów z bazy danych dla podanego dnia (`YYYY-MM-DD`)            |

`stats`, `by-day`, `top-days`, `min-errors` i `day` czytają z bazy wskazanej przez `--db` — żeby zwróciły wyniki, wpisy muszą być w niej już zapisane wcześniejszym poleceniem `import`.

### Opcje poszczególnych poleceń

**`analyze <plik>`**

| Opcja             | Opis                                                                                   |
| ------------------ | ---------------------------------------------------------------------------------------|
| `filename`         | (wymagane) ścieżka do pliku logu lub katalogu z plikami `*.log`                        |
| `--from`, `--to`   | zakres czasu do filtrowania błędów, format `HH:MM:SS` (oba muszą być podane razem)     |
| `--out`            | ścieżka do pliku CSV, do którego zapisane zostanie podsumowanie                        |

**`import <plik>`, `stats`, `by-day`, `top-days`, `min-errors`, `day`**

| Opcja    | Opis                                              |
| -------- | -------------------------------------------------- |
| `--db`   | ścieżka do pliku bazy SQLite (domyślnie `logs.db`) |

### Przykład

```bash
python -m analyzer.cli analyze wms.log --from 08:15:00 --to 08:20:00 --out summary.csv
```

Powyższe polecenie: wczyta `wms.log`, wypisze podsumowanie błędów oraz błędy z przedziału 08:15:00–08:20:00 na ekranie, a podsumowanie zapisze też do `summary.csv`.

```bash
python -m analyzer.cli import wms.log
python -m analyzer.cli by-day
python -m analyzer.cli top-days 3
python -m analyzer.cli min-errors 5
python -m analyzer.cli day 2026-08-22
```

Powyższe polecenia: zapiszą wpisy z `wms.log` do bazy `logs.db`, a następnie wypiszą liczbę błędów dla każdego dnia, 3 dni z największą liczbą błędów, dni z liczbą błędów większą niż 5 oraz podsumowanie błędów z 2026-08-22.

## Wymagania

Wyłącznie biblioteka standardowa Pythona (`argparse`, `csv`, `sqlite3`, `collections`, `sys`) — brak dodatkowych zależności do zainstalowania.
