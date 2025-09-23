import requests


def run(base_url: str = "http://127.0.0.1:5000") -> None:
    races = requests.get(f"{base_url}/api/races", timeout=10).json()
    drivers = requests.get(f"{base_url}/api/drivers", timeout=10).json()
    if not races or not drivers:
        print("Faltan carreras o pilotos para registrar resultados")
        return
    race_id = races[0]['id']
    posiciones = [1, 2, 3]
    for i, pos in enumerate(posiciones):
        driver_id = drivers[min(i, len(drivers) - 1)]['id']
        payload = {"race_id": race_id, "driver_id": driver_id, "position": pos}
        r = requests.post(f"{base_url}/api/race_results", json=payload, timeout=10)
        print("resultado:", r.json() if r.headers.get('content-type','').startswith('application/json') else r.status_code)


if __name__ == "__main__":
    run()


