from flask import Flask, request, jsonify, render_template
from datetime import datetime
from datos.base_datos import obtener_conexion, inicializar_bd, PUNTOS_POR_POSICION


def parse_date_string(value: str) -> str:
    return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")


app = Flask(__name__, template_folder="../presentacion/templates", static_folder="../presentacion/static")
try:
    from flask_cors import CORS  
    CORS(app)
except Exception:
    pass


@app.get("/")
def inicio():
    return render_template("index.html")


@app.get("/escuderias")
def page_escuderias():
    return render_template("escuderias.html")


@app.get("/fanaticos")
def page_fanaticos():
    return render_template("fanaticos.html")


@app.get("/administrativo")
def page_admin():
    return render_template("administrativo.html")


@app.get("/api/teams")
def list_teams():
    with obtener_conexion() as con:
        rows = con.execute("SELECT * FROM teams ORDER BY name ASC").fetchall()
        return jsonify([dict(r) for r in rows])


@app.post("/api/teams")
def create_team():
    data = request.json or {}
    name = (data.get("name") or "").strip()
    country = (data.get("country") or "").strip()
    titles = int(data.get("titles", 0))
    if not name or not country:
        return jsonify({"error": "Nombre y país son obligatorios"}), 400
    try:
        with obtener_conexion() as con:
            cur = con.execute("INSERT INTO teams(name, country, titles) VALUES (?, ?, ?)", (name, country, titles))
            row = con.execute("SELECT * FROM teams WHERE id=?", (cur.lastrowid,)).fetchone()
            return jsonify(dict(row)), 201
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/drivers")
def list_drivers():
    with obtener_conexion() as con:
        rows = con.execute(
            """
            SELECT d.*, t.name AS team_name
            FROM drivers d JOIN teams t ON t.id = d.team_id
            ORDER BY d.points DESC, d.name ASC
            """
        ).fetchall()
        return jsonify([dict(r) for r in rows])


@app.post("/api/drivers")
def create_driver():
    data = request.json or {}
    name = (data.get("name") or "").strip()
    country = (data.get("country") or "").strip()
    team_id = data.get("team_id")
    if not name or not country or team_id is None:
        return jsonify({"error": "Nombre, país y team_id son obligatorios"}), 400
    with obtener_conexion() as con:
        team = con.execute("SELECT id FROM teams WHERE id=?", (team_id,)).fetchone()
        if not team:
            return jsonify({"error": "El equipo no existe"}), 400
        cur = con.execute("INSERT INTO drivers(name, country, team_id, points) VALUES (?, ?, ?, 0)", (name, country, team_id))
        row = con.execute("SELECT * FROM drivers WHERE id=?", (cur.lastrowid,)).fetchone()
        return jsonify(dict(row)), 201


@app.get("/api/races")
def list_races():
    with obtener_conexion() as con:
        rows = con.execute("SELECT * FROM races ORDER BY date ASC").fetchall()
        return jsonify([dict(r) for r in rows])


@app.post("/api/races")
def create_race():
    data = request.json or {}
    grand_prix = (data.get("grand_prix") or "").strip()
    country = (data.get("country") or "").strip()
    date_str = (data.get("date") or "").strip()
    if not grand_prix or not country or not date_str:
        return jsonify({"error": "Grand Prix, país y fecha son obligatorios"}), 400
    try:
        date_iso = parse_date_string(date_str)
    except Exception:
        return jsonify({"error": "La fecha debe tener formato YYYY-MM-DD"}), 400
    with obtener_conexion() as con:
        cur = con.execute("INSERT INTO races(grand_prix, date, country) VALUES (?, ?, ?)", (grand_prix, date_iso, country))
        row = con.execute("SELECT * FROM races WHERE id=?", (cur.lastrowid,)).fetchone()
        return jsonify(dict(row)), 201


@app.get("/api/race_results")
def list_race_results():
    with obtener_conexion() as con:
        rows = con.execute(
            """
            SELECT rr.*, r.grand_prix, r.date, d.name AS driver_name, t.name AS team_name
            FROM race_results rr
            JOIN races r ON r.id = rr.race_id
            JOIN drivers d ON d.id = rr.driver_id
            JOIN teams t ON t.id = d.team_id
            ORDER BY r.date DESC, rr.position ASC
            """
        ).fetchall()
        return jsonify([dict(r) for r in rows])


@app.post("/api/race_results")
def create_race_result():
    data = request.json or {}
    race_id = data.get("race_id")
    driver_id = data.get("driver_id")
    position = data.get("position")
    if race_id is None or driver_id is None or position is None:
        return jsonify({"error": "race_id, driver_id y position son obligatorios"}), 400
    try:
        position = int(position)
    except Exception:
        return jsonify({"error": "La posición debe ser numérica"}), 400
    if position <= 0:
        return jsonify({"error": "La posición debe ser mayor a 0"}), 400

    puntos = PUNTOS_POR_POSICION.get(position, 0)
    with obtener_conexion() as con:
        race = con.execute("SELECT id FROM races WHERE id=?", (race_id,)).fetchone()
        driver = con.execute("SELECT id FROM drivers WHERE id=?", (driver_id,)).fetchone()
        if not race or not driver:
            return jsonify({"error": "Carrera o Piloto inexistente"}), 400
        exists = con.execute("SELECT id FROM race_results WHERE race_id=? AND (driver_id=? OR position=?)", (race_id, driver_id, position)).fetchone()
        if exists:
            return jsonify({"error": "Resultado duplicado para la carrera"}), 409
        con.execute("INSERT INTO race_results(race_id, driver_id, position, points_awarded) VALUES (?, ?, ?, ?)", (race_id, driver_id, position, puntos))
        con.execute("UPDATE drivers SET points = points + ? WHERE id = ?", (puntos, driver_id))
        row = con.execute("SELECT * FROM race_results WHERE race_id=? AND driver_id=?", (race_id, driver_id)).fetchone()
        return jsonify(dict(row)), 201


@app.get("/api/ranking")
def ranking():
    with obtener_conexion() as con:
        rows = con.execute(
            """
            SELECT d.id, d.name, d.country, d.points, t.name AS team_name
            FROM drivers d JOIN teams t ON t.id = d.team_id
            ORDER BY d.points DESC, d.name ASC
            """
        ).fetchall()
        return jsonify([dict(r) for r in rows])


@app.get("/api/team_stats")
def team_stats():
    with obtener_conexion() as con:
        rows = con.execute(
            """
            SELECT t.id, t.name, t.country, t.titles,
                   COALESCE(SUM(d.points), 0) AS total_points,
                   COUNT(d.id) AS driver_count
            FROM teams t LEFT JOIN drivers d ON d.team_id = t.id
            GROUP BY t.id
            ORDER BY total_points DESC, t.name ASC
            """
        ).fetchall()
        return jsonify([dict(r) for r in rows])


@app.get("/api/circuits")
def list_circuits():
    with obtener_conexion() as con:
        rows = con.execute("SELECT * FROM circuits ORDER BY name ASC").fetchall()
        return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    inicializar_bd()
    app.run(host="0.0.0.0", port=5000, debug=True)

# python -m aplicacion.servidor (ya que no funciona con el run.py por las carpetas, se tiene que ejecutar desde la carpeta raiz)
