from collections import Counter 

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