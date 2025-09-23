import os
import sqlite3


DATABASE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "f1.db")


def obtener_conexion() -> sqlite3.Connection:
    conexion = sqlite3.connect(DATABASE_FILE)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion


def inicializar_bd() -> None:
    conexion = obtener_conexion()
    cur = conexion.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            country TEXT NOT NULL,
            titles INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            points INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE RESTRICT
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS races (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grand_prix TEXT NOT NULL,
            date TEXT NOT NULL,
            country TEXT NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS race_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            race_id INTEGER NOT NULL,
            driver_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            points_awarded INTEGER NOT NULL,
            UNIQUE(race_id, driver_id),
            UNIQUE(race_id, position),
            FOREIGN KEY (race_id) REFERENCES races(id) ON DELETE CASCADE,
            FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE CASCADE
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS circuits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            country TEXT NOT NULL
        );
        """
    )

    conexion.commit()

    count = conexion.execute("SELECT COUNT(1) AS c FROM teams").fetchone()["c"]
    if count == 0:
        sembrar_datos(conexion)

    conexion.commit()
    conexion.close()


PUNTOS_POR_POSICION = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}


def sembrar_datos(conexion: sqlite3.Connection) -> None:
    equipos = [
        ("Red Bull Racing", "Austria", 6, [("Max Verstappen", "Países Bajos"), ("Sergio Pérez", "México")]),
        ("Ferrari", "Italia", 16, [("Charles Leclerc", "Mónaco"), ("Carlos Sainz", "España")]),
        ("Mercedes", "Alemania", 8, [("Lewis Hamilton", "Reino Unido"), ("George Russell", "Reino Unido")]),
        ("McLaren", "Reino Unido", 8, [("Lando Norris", "Reino Unido"), ("Oscar Piastri", "Australia")]),
        ("Aston Martin", "Reino Unido", 0, [("Fernando Alonso", "España"), ("Lance Stroll", "Canadá")]),
        ("Alpine", "Francia", 2, [("Pierre Gasly", "Francia"), ("Esteban Ocon", "Francia")]),
        ("Williams", "Reino Unido", 9, [("Alex Albon", "Tailandia"), ("Logan Sargeant", "Estados Unidos")]),
        ("RB", "Italia", 0, [("Yuki Tsunoda", "Japón"), ("Daniel Ricciardo", "Australia")]),
        ("Stake F1 Sauber", "Suiza", 0, [("Valtteri Bottas", "Finlandia"), ("Zhou Guanyu", "China")]),
        ("Haas", "Estados Unidos", 0, [("Nico Hülkenberg", "Alemania"), ("Kevin Magnussen", "Dinamarca")]),
    ]
    for nombre, pais, titulos, pilotos in equipos:
        cur = conexion.execute(
            "INSERT INTO teams(name, country, titles) VALUES (?, ?, ?)",
            (nombre, pais, titulos),
        )
        team_id = cur.lastrowid
        for piloto_nombre, piloto_pais in pilotos:
            conexion.execute(
                "INSERT INTO drivers(name, country, team_id, points) VALUES (?, ?, ?, 0)",
                (piloto_nombre, piloto_pais, team_id),
            )

    circuitos = [
        ("Sakhir (Bahréin)", "Baréin"),
        ("Jeddah Corniche", "Arabia Saudita"),
        ("Albert Park", "Australia"),
        ("Imola", "Italia"),
        ("Mónaco", "Mónaco"),
        ("Silverstone", "Reino Unido"),
        ("Monza", "Italia"),
        ("Suzuka", "Japón"),
        ("COTA (Austin)", "Estados Unidos"),
        ("Interlagos", "Brasil"),
    ]
    for nombre_circuito, pais_circuito in circuitos:
        conexion.execute(
            "INSERT INTO circuits(name, country) VALUES (?, ?)",
            (nombre_circuito, pais_circuito),
        )


