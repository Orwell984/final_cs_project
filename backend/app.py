import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymysql
import json
from flask import Response
from sqlalchemy import create_engine, text

app = Flask(__name__)
CORS(app)

# -------- DB helpers (no classes, just functions) --------
DB_HOST = os.getenv("DB_HOST", "db")       
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "pass")
DB_NAME = os.getenv("DB_NAME", "groceries")

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,        
    pool_recycle=1800,         
    future=True
)
# general function to run any SQL command
def dynamic_function(command, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(command), params or {})

        
        try:
            rows = result.mappings().all()
            return [dict(r) for r in rows]
        except Exception:
            conn.commit()
            return {"status": "ok"}


# -------- Flask app --------
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)  # allow front-end JS to call API

# Serve the static index
@app.route("/")
def root():
    return send_from_directory("static", "index.html")


# -------- REST API (only instructional messages here)(app.routes) --------

@app.get("/api/items")
def api_list_items():
    sql = """
        SELECT p.id, p.name,
               d.name AS department,
               o.name AS origin,
               p.price, p.stock
        FROM products p
        JOIN dept d ON p.dept_id = d.id
        JOIN origin o ON p.origin_id = o.id
        ORDER BY p.id;
    """
    data = dynamic_function(sql)
    return Response(json.dumps(data, default=str), mimetype='application/json')


@app.get("/api/items/<int:product_id>")
def api_get_item(product_id):
    sql = f"""
        SELECT p.id, p.name,
               d.name AS department,
               o.name AS origin,
               p.price, p.stock
        FROM products p
        JOIN dept d ON p.dept_id = d.id
        JOIN origin o ON p.origin_id = o.id
        WHERE p.id = {product_id}
        LIMIT 1;
    """
    data = dynamic_function(sql)
    if not data:
        return Response(json.dumps({"error": "not found"}), mimetype='application/json', status=404)
    return Response(json.dumps(data[0], default=str), mimetype='application/json')

@app.post("/api/items")
def api_create_item():
    d = request.get_json(force=True)

    name = d["name"]
    dept = d["department"]
    origin = d.get("origin", "MX")
    price = d["price"]
    stock = d["stock"]

    dynamic_function(f"""
        INSERT INTO dept(name)
        SELECT '{dept}' WHERE NOT EXISTS
        (SELECT id FROM dept WHERE name='{dept}');
    """)

    dynamic_function(f"""
        INSERT INTO origin(name)
        SELECT '{origin}' WHERE NOT EXISTS
        (SELECT id FROM origin WHERE name='{origin}');
    """)

    
    dept_id = dynamic_function(f"SELECT id FROM dept WHERE name='{dept}'")[0]["id"]
    origin_id = dynamic_function(f"SELECT id FROM origin WHERE name='{origin}'")[0]["id"]

    new_id = dynamic_function("""
        SELECT COALESCE(
            (
                SELECT t1.id + 1
                FROM products t1
                LEFT JOIN products t2
                    ON t1.id + 1 = t2.id
                WHERE t2.id IS NULL
                ORDER BY t1.id
                LIMIT 1
            ),
            1
        ) AS new_id;
    """)[0]["new_id"]

    dynamic_function(f"""
        INSERT INTO products(id, name, dept_id, origin_id, price, stock)
        VALUES ({new_id}, '{name}', {dept_id}, {origin_id}, {price}, {stock});
    """)

    return Response(json.dumps({"id": new_id}, default=str), mimetype='application/json', status=201)


@app.put("/api/items/<int:product_id>")
def api_update_item(product_id):
    d = request.get_json(force=True)

    name = d["name"]
    dept = d["department"]
    origin = d.get("origin", "MX")
    price = d["price"]
    stock = d["stock"]


    dynamic_function(f"""
        INSERT INTO dept(name)
        SELECT '{dept}' WHERE NOT EXISTS
        (SELECT id FROM dept WHERE name='{dept}');
    """)


    dynamic_function(f"""
        INSERT INTO origin(name)
        SELECT '{origin}' WHERE NOT EXISTS
        (SELECT id FROM origin WHERE name='{origin}');
    """)

    dept_id = dynamic_function(f"SELECT id FROM dept WHERE name='{dept}'")[0]["id"]
    origin_id = dynamic_function(f"SELECT id FROM origin WHERE name='{origin}'")[0]["id"]

    
    dynamic_function(f"""
        UPDATE products
        SET name='{name}',
            dept_id={dept_id},
            origin_id={origin_id},
            price={price},
            stock={stock}
        WHERE id={product_id};
    """)

    return Response(json.dumps({"updated": True}, default=str), mimetype='application/json')

@app.delete("/api/items/<int:product_id>")
def api_delete_item(product_id):
    dynamic_function(f"DELETE FROM products WHERE id={product_id}")
    return Response(json.dumps({"deleted": True}, default=str), mimetype='application/json')

@app.get("/api/departments")
def api_departments():
    data = dynamic_function("SELECT id, name FROM dept ORDER BY name")
    return Response(json.dumps(data, default=str), mimetype='application/json')

@app.get("/api/origins")
def api_origins():
    return jsonify({
        "message": "GET /api/origins should return a list like: [{id, code}, ...] ordered by code."
    })

@app.route('/v1/data/all')
def test(): 
    command = "SELECT * FROM products"
    data = dynamic_function(command)
    try:
        return Response(json.dumps(data, default=str), mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"status": "error", "message": str(e)}), mimetype='application/json', status=500)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)