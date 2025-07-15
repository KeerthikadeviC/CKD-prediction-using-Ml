from flask import Flask, render_template, request, redirect, url_for, session, flash
import numpy as np
import pickle
import os

app = Flask(__name__)
app.secret_key = 'secret123'

# Dummy user store (in-memory)
users = {}

# Load model
model_path = os.path.join("models", "random_forest.pkl")
if os.path.exists(model_path):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
else:
    model = None

@app.route("/", methods=["GET"])
def root():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username]["password"] == password:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "error")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if username in users:
            flash("Username already exists", "error")
        elif password != confirm_password:
            flash("Passwords do not match", "error")
        else:
            users[username] = {"email": email, "password": password}
            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("login"))
    return redirect(url_for("login"))

@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))
        
    prediction = None
    if request.method == "POST":
        try:
            fields = ["age", "sg", "al", "bu", "sc", "hemo", "htn", "dm"]
            features = [float(request.form.get(f)) for f in fields]
            pred = model.predict([np.array(features)])
            prediction = "CKD Detected" if pred[0] == 1 else "No CKD Detected"
        except Exception as e:
            prediction = f"Error: {e}"
    return render_template("predict.html", prediction=prediction)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
