import requests


def run(base_url: str = "http://127.0.0.1:5000") -> None:
    equipos = [
        {"name": "Equipo Escuela A", "country": "Argentina", "titles": 0},
        {"name": "Equipo Escuela B", "country": "Argentina", "titles": 1},
    ]
    for e in equipos:
        r = requests.post(f"{base_url}/api/teams", json=e, timeout=10)
        print("crear equipo:", r.json() if r.headers.get('content-type','').startswith('application/json') else r.status_code)
    teams = requests.get(f"{base_url}/api/teams", timeout=10).json()
    if teams:
        team_id = teams[0]['id']
        for i in range(2):
            d = {"name": f"Piloto Escuela {i+1}", "country": "Argentina", "team_id": team_id}
            r = requests.post(f"{base_url}/api/drivers", json=d, timeout=10)
            print("crear piloto:", r.json() if r.headers.get('content-type','').startswith('application/json') else r.status_code)


if __name__ == "__main__":
    run()


