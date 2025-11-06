from flask import Flask, jsonify
import os
import psycopg2
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME", "minecraft")
SQL_PATH = "../SQL Queries/"
query = ""

def get_connection():
    return psycopg2.connect(
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:26257/{DB_NAME}?sslmode=require"
    )

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/capacity/<limit>")
def get_top_capacity(limit):
    with open(SQL_PATH+"select_top_capacity.sql", "r") as f:
      query = f.read().strip()

    conn = get_connection()
    with conn.cursor() as cursor:
      try:
        cursor.execute(query, [limit])
        result = cursor.fetchall()
        if result:
           return jsonify(result)
        else:
           print("No results for get_top_capacity")
      except Exception as e:
         print(e)
         return None
      
@app.route("/api/uptime/<limit>")
def get_top_uptime(limit):
    with open(SQL_PATH+"select_top_uptime.sql", "r") as f:
      query = f.read().strip()
    conn = get_connection()
    with conn.cursor() as cursor:
      try:
        cursor.execute(query, [limit])
        result = cursor.fetchall()
        if result:
           return jsonify(result)
        else:
           print("No results for get_top_capacity")
      except Exception as e:
         print(e)
         return None
  
if __name__ == "__main__":
  app.run() 
