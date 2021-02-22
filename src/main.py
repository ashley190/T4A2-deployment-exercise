from flask import Flask, jsonify, request
import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)


connection = psycopg2.connect(
    database=os.getenv('database'),
    user=os.getenv('user'),
    password=os.getenv('password'),
    host=os.getenv('host')
)

cursor = connection.cursor()
cursor.execute("create table if not exists profile (id serial PRIMARY KEY, name varchar);")     # noqa:E501
connection.commit()


@app.route("/profile", methods=["GET"])
def profile_page():
    sql = "SELECT * FROM profile;"
    cursor.execute(sql)
    profile = cursor.fetchall()
    return jsonify(profile)


@app.route("/profile", methods=["POST"])
def create_profile():
    sql = "INSERT INTO profile (name) VALUES (%s);"
    cursor.execute(sql, (request.json["name"],))
    connection.commit()

    sql = "SELECT * FROM profile ORDER BY ID DESC LIMIT 1;"
    cursor.execute(sql)
    profile = cursor.fetchone()
    return jsonify(profile)
