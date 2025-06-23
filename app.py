from flask import Flask, render_template, request, redirect, url_for, session
import os
import json

app = Flask(__name__)
app.secret_key = "clave-super-secreta"  # Usa una clave más segura en producción


# Función para leer todos los artículos del folder
def load_articles():
    articles = []
    for filename in os.listdir("articles"):
        if filename.endswith(".json"):
            with open(os.path.join("articles", filename), "r", encoding="utf-8") as f:
                article = json.load(f)
                articles.append(article)
    # Ordenar por fecha (opcional)
    articles.sort(key=lambda x: x["date"], reverse=True)
    return articles

@app.route("/")
def home():
    articles = load_articles()
    return render_template("index.html", articles=articles)

@app.route("/article/<int:article_id>")
def show_article(article_id):
    filepath = f"articles/{article_id}.json"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            article = json.load(f)
        return render_template("article.html", article=article)
    else:
        return "Artículo no encontrado", 404

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Puedes cambiar esto por tus propios datos
        if username == "admin" and password == "1234":
            session["admin"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("home"))

@app.route("/admin")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("login"))

    articles = load_articles()
    return render_template("dashboard.html", articles=articles)

@app.route("/add", methods=["GET", "POST"])
def add_article():
    if not session.get("admin"):
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        date = request.form["date"]

        # Generar un nuevo ID basado en archivos existentes
        existing_ids = [int(f.split(".")[0]) for f in os.listdir("articles") if f.endswith(".json")]
        new_id = max(existing_ids, default=0) + 1

        new_article = {
            "id": new_id,
            "title": title,
            "content": content,
            "date": date
        }

        # Guardar el nuevo artículo como archivo JSON
        with open(f"articles/{new_id}.json", "w", encoding="utf-8") as f:
            json.dump(new_article, f, ensure_ascii=False, indent=4)

        return redirect(url_for("dashboard"))

    return render_template("add_article.html")

@app.route("/edit/<int:article_id>", methods=["GET", "POST"])
def edit_article(article_id):
    if not session.get("admin"):
        return redirect(url_for("login"))

    filepath = f"articles/{article_id}.json"
    if not os.path.exists(filepath):
        return "Artículo no encontrado", 404

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        date = request.form["date"]

        updated_article = {
            "id": article_id,
            "title": title,
            "content": content,
            "date": date
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(updated_article, f, ensure_ascii=False, indent=4)

        return redirect(url_for("dashboard"))

    with open(filepath, "r", encoding="utf-8") as f:
        article = json.load(f)

    return render_template("edit_article.html", article=article)

@app.route("/delete/<int:article_id>")
def delete_article(article_id):
    if not session.get("admin"):
        return redirect(url_for("login"))

    filepath = f"articles/{article_id}.json"
    if os.path.exists(filepath):
        os.remove(filepath)
        return redirect(url_for("dashboard"))
    else:
        return "Artículo no encontrado", 404

if __name__ == "__main__":
    app.run(debug=True)

