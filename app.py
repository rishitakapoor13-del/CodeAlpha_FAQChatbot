"""Web server for the FAQ chatbot. Run: python app.py  then open http://127.0.0.1:5000"""
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, abort

from chatbot import FAQBot

BASE = Path(__file__).parent
PUBLIC_FILES = {"style.css", "script.js"}

app = Flask(__name__)
bot = FAQBot()


@app.route("/")
def home():
    return send_from_directory(BASE, "index.html")


@app.route("/<name>")
def public_file(name):
    if name not in PUBLIC_FILES:
        abort(404)
    return send_from_directory(BASE, name)


@app.route("/api/categories")
def categories():
    return jsonify(bot.categories())


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()[:300]
    if not message:
        return jsonify({"error": "Please type a question."}), 400
    return jsonify(bot.ask(message))


if __name__ == "__main__":
    app.run(debug=True)
