import os
from flask import Flask, Response, engine, text, request, row, jsonify, send_from_directory
import json
from flask_cors import CORS
import pymysql
import json
from flask import Response
from sqlalchemy import create_engine, text

app = Flask(__name__)
CORS(app)

def fetch_all_products_from_db(command):
    com = f"{command}"
    with engine.connect() as conn:
        result=conn.execute(text(com)).mappings().all()
    return [dict(row) for row in result]

# -------- DB helpers (no classes, just functions) --------
DB_HOST = os.getenv("DB_HOST", "db")       
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "pass")
DB_NAME = os.getenv("DB_NAME", "groceries")

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,        # revalida conexiones muertas
    pool_recycle=1800,         # evita timeouts del lado MySQL
    future=True
)

def dynamic_function(command):
    com = f" {command}"
    with engine.connect() as conn:
        result=conn.execute(text(com)).mappings().all()
    return [dict(row) for row in result]


def get_or_create_dept_id(dept_name):
    """
    TODO (student):
      - Try to SELECT id FROM dept WHERE name=%s LIMIT 1
      - If exists, return that id
      - Else INSERT INTO dept(name) VALUES(%s) and return lastrowid
    """
    # Pseudocode only:
    # conn = get_conn()
    # with conn.cursor() as cur:
    #   cur.execute("SELECT id FROM dept WHERE name=%s LIMIT 1", (dept_name,))
    #   row = cur.fetchone()
    #   if row: return row["id"]
    #   cur.execute("INSERT INTO dept (name) VALUES (%s)", (dept_name,))
    #   return cur.lastrowid
    return None  # placeholder


def get_or_create_origin_id(origin_code):
    """
    TODO (student):
      - Default origin_code to 'MX' if missing
      - SELECT id FROM origin WHERE code=%s LIMIT 1
      - If exists, return it; otherwise INSERT and return lastrowid
    """
    return None  # placeholder


def fetch_all_products():
    """
    TODO (student):
      - Return a list of products joining dept and origin so the frontend sees:
        id, name, department (dept.name), origin (origin.code), price, stock
      - SQL idea:
        SELECT p.id, p.name, d.name AS department, o.code AS origin, p.price, p.stock
        FROM products p
        JOIN dept d ON p.dept_id = d.id
        JOIN origin o ON p.origin_id = o.id
        ORDER BY p.id;
    """
    return []  # placeholder


def fetch_product(product_id):
    """
    TODO (student):
      - Return a single product by id with the same join as above
      - If not found, return None
    """
    return None  # placeholder


def insert_product(name, department, origin, price, stock):
    """
    TODO (student):
      - Use get_or_create_dept_id and get_or_create_origin_id to get foreign keys
      - INSERT INTO products (name, dept_id, origin_id, price, stock) VALUES (...)
      - Return new product id (lastrowid)
    """
    return None  # placeholder


def update_product(product_id, name, department, origin, price, stock):
    """
    TODO (student):
      - Resolve dept_id/origin_id
      - UPDATE products SET ... WHERE id=%s
      - Return affected rows count
    """
    return 0  # placeholder


def delete_product(product_id):
    """
    TODO (student):
      - DELETE FROM products WHERE id=%s
      - Return affected rows count
    """
    return 0  # placeholder


# --- Helpers to list departments and origins ---
def fetch_departments():
    """
    TODO (student):
      - SELECT id, name FROM dept ORDER BY name;
      - Return list of dicts
    """
    return []  # placeholder


def fetch_origins():
    """
    TODO (student):
      - SELECT id, code FROM origin ORDER BY code;
      - Return list of dicts
    """
    return []  # placeholder


# -------- Flask app --------
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)  # allow front-end JS to call API

# Serve the static index
@app.route("/")
def root():
    return send_from_directory("static", "index.html")


# -------- REST API (only instructional messages here) --------

import json
from flask import Flask, Response, request
@app.route("/api/items", methods=["GET"])
def api_list_items():
    command = request.args.get('command', '')
    results = fetch_all_products_from_db(command) #"GET /api/items should return a list of products joined with dept.name and origin.code".



@app.get("/api/items/<int:product_id>")
def api_get_item(product_id):
    return jsonify({
        "message": "GET /api/items/<id> should return a single product (with department and origin) or 404 if not found.",
        "id_received": product_id
    })

@app.post("/api/items")
def api_create_item():
    data = request.get_json(force=True)
    return jsonify({
        "message": "POST /api/items should insert a product (resolving dept_id and origin_id) and return the new id.",
        "payload_received": data
    }), 201

@app.put("/api/items/<int:product_id>")
def api_update_item(product_id):
    data = request.get_json(force=True)
    return jsonify({
        "message": "PUT /api/items/<id> should update the product (name, department->dept_id, origin->origin_id, price, stock).",
        "id_received": product_id,
        "payload_received": data
    })

@app.delete("/api/items/<int:product_id>")
def api_delete_item(product_id):
    return jsonify({
        "message": "DELETE /api/items/<id> should delete the product and return a confirmation.",
        "id_received": product_id
    })

@app.get("/api/departments")
def api_departments():
    return jsonify({
        "message": "GET /api/departments should return a list like: [{id, name}, ...] ordered by name."
    })

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

@app.route("/api/items", methods=["GET"])
def api_list_items():
    command = request.args.get('command', '')
    results = fetch_all_products_from_db(command)
    json_data = json.dumps(results) 
    return Response(json_data, mimetype="application/json")

    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)



