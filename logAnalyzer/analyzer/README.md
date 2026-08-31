# analyzer

Pakiet Pythona do analizy logów magazynowych. Wczytuje plik logu, wyszukuje w nim błędy (`ERROR`), pozwala je filtrować po zakresie czasu, tworzy podsumowanie najczęściej występujących błędów oraz umożliwia zapis wyników do pliku CSV lub bazy danych SQLite.

## Uruchamianie

Ponieważ `cli.py` używa importów względnych (`from .parser import ...`), plik należy uruchamiać jako moduł pakietu, z katalogu nadrzędnego (`logAnalyzer/`):

```bash
python -m analyzer.cli <plik_logu> [opcje]
```

### Dostępne opcje

| Opcja            | Opis                                                                                |
| ---------------- | ------------------------------------------------------------------------------------|
| `filename`       | (wymagane) ścieżka do pliku logu                                                    |
| `--from`, `--to` | zakres czasu do filtrowania błędów, format `HH:MM:SS` (oba muszą być podane razem)  |
| `--out`          | ścieżka do pliku CSV, do którego zapisane zostanie podsumowanie                     |
| `--db`           | ścieżka do pliku bazy SQLite (domyślnie `logs.db`)                                  |
| `--save`         | zapisuje wczytane wpisy do bazy danych                                              |
| `--stats`        | wypisuje statystyki błędów odczytane z bazy danych                                  |

### Przykład

```bash
python -m analyzer.cli wms.log --from 08:15:00 --to 08:20:00 --save --stats --out summary.csv
```

Powyższe polecenie: wczyta `wms.log`, zapisze wpisy do `logs.db`, wypisze statystyki błędów z bazy, podsumowanie i błędy z przedziału 08:15:00–08:20:00 na ekranie, a podsumowanie zapisze też do `summary.csv`.

## Wymagania

Wyłącznie biblioteka standardowa Pythona (`argparse`, `csv`, `sqlite3`, `collections`, `sys`) — brak dodatkowych zależności do zainstalowania.
