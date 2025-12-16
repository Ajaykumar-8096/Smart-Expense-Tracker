from flask import Flask, render_template, request, redirect, session
from db_config import get_db_connection
import hashlib

app = Flask(__name__)
app.secret_key = "secret123"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])

        db = get_db_connection()
        cur = db.cursor()
        cur.execute("SELECT user_id FROM users WHERE username=%s AND password=%s",
                    (username, password))
        user = cur.fetchone()
        cur.close()
        db.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])

        db = get_db_connection()
        cur = db.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, password))
        db.commit()
        cur.close()
        db.close()

        return redirect("/")

    return render_template("register.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]

    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        desc = request.form["description"]
        date = request.form["date"]

        db = get_db_connection()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO expenses (user_id, amount, category, description, expense_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, amount, category, desc, date))
        db.commit()
        cur.close()
        db.close()

    db = get_db_connection()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM expenses WHERE user_id=%s ORDER BY expense_date DESC", (user_id,))
    expenses = cur.fetchall()

    cur.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses WHERE user_id=%s GROUP BY category
    """, (user_id,))
    summary = cur.fetchall()

    cur.close()
    db.close()

    return render_template("dashboard.html", expenses=expenses, summary=summary)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
