from flask import Flask, request, jsonify
import sqlite3
import hashlib

app = Flask(__name__)
DB_FILE = "central_users.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = hash_password(data.get("password"))
    email = data.get("email")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        return jsonify({"status": "fail", "message": "Username already exists"}), 400

    cursor.execute("INSERT INTO users (username, password, email, role, status) VALUES (?, ?, ?, ?, ?)",
                   (username, password, email, "user", "blocked"))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "User registered and blocked"}), 200

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = hash_password(data.get("password"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "success", "role": user["role"], "status_text": user["status"]})
    return jsonify({"status": "fail", "message": "Invalid credentials"}), 401

@app.route("/block_user", methods=["POST"])
def block_user():
    data = request.json
    username = data.get("username")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status='blocked' WHERE username=?", (username,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": f"{username} blocked"})

@app.route("/unblock_user", methods=["POST"])
def unblock_user():
    data = request.json
    username = data.get("username")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status='active' WHERE username=?", (username,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": f"{username} unblocked"})

@app.route("/reset_password", methods=["POST"])
def reset_password():
    data = request.json
    username = data.get("username")
    new_password = hash_password(data.get("new_password"))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Password reset successfully"})

if __name__ == "__main__":
    # Initialize DB if not exist
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        email TEXT,
                        role TEXT,
                        status TEXT)''')
    conn.close()
    app.run(debug=True)
