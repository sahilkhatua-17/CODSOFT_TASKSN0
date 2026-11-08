import os
import random
import string
import sys
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


def generate_password(length=16, use_uppercase=True, use_lowercase=True, use_numbers=True, use_symbols=True):
    characters = ""
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_numbers:
        characters += string.digits
    if use_symbols:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if not characters:
        return ""

    return "".join(random.choice(characters) for _ in range(length))


@app.route("/")
def index():
    initial_password = generate_password(16)
    return render_template("index.html", initial_password=initial_password)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json() or {}
    try:
        length = int(data.get("length", 16))
    except (ValueError, TypeError):
        length = 16
    length = max(4, min(length, 128))

    use_upper = bool(data.get("uppercase", True))
    use_lower = bool(data.get("lowercase", True))
    use_digits = bool(data.get("numbers", True))
    use_symbols = bool(data.get("symbols", True))

    password = generate_password(
        length=length,
        use_uppercase=use_upper,
        use_lowercase=use_lower,
        use_numbers=use_digits,
        use_symbols=use_symbols,
    )

    if not password:
        return jsonify({"error": "Please select at least one character type."}), 400

    return jsonify({"password": password})


def run_cli():
    print("=" * 35)
    print("        Password Generator         ")
    print("=" * 35)
    try:
        raw_len = input("Enter password length [default 16]: ").strip()
        length = int(raw_len) if raw_len else 16
    except ValueError:
        length = 16

    password = generate_password(length)
    print(f"\nGenerated password:\n{password}")
    print("=" * 35)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli()
    else:
        print("\n" + "=" * 50)
        print(" Password Generator is running!")
        print(" Open in browser: http://127.0.0.1:5000")
        print(" Press Ctrl + C to stop.")
        print("=" * 50 + "\n")

        # Automatically pop up the browser when running directly
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            Timer(1.0, open_browser).start()
        elif not os.environ.get("WERKZEUG_RUN_MAIN"):
            Timer(1.0, open_browser).start()

        app.run(debug=True)
