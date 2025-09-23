import requests


def run(base_url: str = "http://127.0.0.1:5000") -> None:
    carreras = [
        {"grand_prix": "Gran Premio Escolar 1", "country": "Argentina", "date": "2025-11-01"},
        {"grand_prix": "Gran Premio Escolar 2", "country": "Argentina", "date": "2025-11-15"},
    ]
    for c in carreras:
        r = requests.post(f"{base_url}/api/races", json=c, timeout=10)
        print("crear carrera:", r.json() if r.headers.get('content-type','').startswith('application/json') else r.status_code)
    print("ranking:", requests.get(f"{base_url}/api/ranking", timeout=10).json())
    print("circuitos:", requests.get(f"{base_url}/api/circuits", timeout=10).json())


if __name__ == "__main__":
    run()


