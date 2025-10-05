# app.py
import os
import sys
import subprocess
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret"

# Global reference to calculator process
calc_proc = None

# ----------------- Login -----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Simple hardcoded authentication (change to DB or file if needed)
        if username == "admin" and password == "123":
            session["user"] = username
            return redirect(url_for("details"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


# ----------------- Details -----------------
@app.route("/details")
def details():
    if "user" not in session:
        return redirect(url_for("login"))

    project_info = {
        "project_name": "Virtual Scientific Calculator",
        "mentor": {"name": "Dr. Mentor Name", "img": "images/mentor.jpg", "bio": "Professor, Dept. of CS"},
        "leader": {"name": "Shubham Singh", "img": "images/leader.jpg", "bio": "Project Leader"},
        "members": [
            {"name": "Rahul", "img": "images/member1.jpg", "role": "Frontend / Docs"},
            {"name": "Priya", "img": "images/member2.jpg", "role": "Backend / Integration"}
        ]
    }
    return render_template("details.html", info=project_info)


# ----------------- Functions -----------------
@app.route("/functions")
def functions():
    if "user" not in session:
        return redirect(url_for("login"))

    buttons = [
        ("^", "Exponentiation (use as a^b)"),
        ("sqrt(x)", "Square root"),
        ("x^3", "Cube"),
        ("cbrt(x)", "Cube root"),
        ("exp(x)", "e^x (exponential)"),
        ("log(x)", "Log base 10"),
        ("ln(x)", "Natural logarithm"),
        ("pi", "π constant"),
        ("e", "Euler's number"),
        ("sin(x)", "Sine — input in degrees"),
        ("cos(x)", "Cosine — input in degrees"),
        ("tan(x)", "Tangent — input in degrees"),
        ("asin(x)", "Inverse sine — returns degrees"),
        ("acos(x)", "Inverse cosine — returns degrees"),
        ("atan(x)", "Inverse tangent — returns degrees"),
        ("!", "Factorial"),
        ("sinh(x)", "Hyperbolic sine"),
        ("cosh(x)", "Hyperbolic cosine"),
        ("tanh(x)", "Hyperbolic tangent"),
        ("mod / %", "Modulo / Remainder")
    ]
    return render_template("functions.html", buttons=buttons)


# ----------------- Calculator page -----------------
@app.route("/calculator")
def calculator():
    if "user" not in session:
        return redirect(url_for("login"))

    global calc_proc
    running = False
    if calc_proc is not None:
        running = (calc_proc.poll() is None)
    return render_template("calculator.html", running=running)


# ----------------- Start calculator process -----------------
@app.route("/run_calc", methods=["POST"])
def run_calc():
    if "user" not in session:
        return redirect(url_for("login"))

    global calc_proc
    # If process already running, do nothing
    if calc_proc is not None and calc_proc.poll() is None:
        flash("Calculator already running.")
        return redirect(url_for("calculator"))

    # Path to your Python script
    script_path = os.path.join(app.root_path, "VirtualCalculator.py")
    if not os.path.exists(script_path):
        flash("Calculator script not found: " + script_path)
        return redirect(url_for("calculator"))

    try:
        # Use same Python interpreter as the Flask app
        if os.name == "nt":
            # On Windows, open in a new console window so it has its own display
            calc_proc = subprocess.Popen(
                [sys.executable, script_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Unix/macOS - just spawn a process (may run in background)
            calc_proc = subprocess.Popen([sys.executable, script_path])
        flash("Calculator started.")
    except Exception as e:
        flash(f"Failed to start calculator: {e}")
    return redirect(url_for("calculator"))


# ----------------- Stop calculator process -----------------
@app.route("/stop_calc", methods=["POST"])
def stop_calc():
    if "user" not in session:
        return redirect(url_for("login"))

    global calc_proc
    if calc_proc is None or calc_proc.poll() is not None:
        flash("Calculator is not running.")
        return redirect(url_for("calculator"))

    try:
        calc_proc.terminate()
        calc_proc.wait(timeout=3)
        flash("Calculator stopped.")
    except Exception:
        try:
            calc_proc.kill()
        except Exception:
            pass
        flash("Calculator terminated.")
    finally:
        calc_proc = None

    return redirect(url_for("calculator"))


# ----------------- Logout -----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    # Run Flask on port 5000
    app.run(debug=True)
