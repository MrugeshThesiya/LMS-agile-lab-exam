import os
import sqlite3

from flask import Flask, g, redirect, render_template, request, url_for, flash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["DATABASE"] = os.environ.get("DATABASE", "library.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            available INTEGER NOT NULL DEFAULT 1,
            borrower TEXT
        )
        """
    )
    db.commit()


@app.before_request
def ensure_db():
    init_db()


@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    db = get_db()
    if query:
        like = f"%{query}%"
        books = db.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY id",
            (like, like),
        ).fetchall()
    else:
        books = db.execute("SELECT * FROM books ORDER BY id").fetchall()
    return render_template("index.html", books=books, query=query)


@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        if not title or not author:
            flash("Title and author are required.")
            return render_template("add.html", title=title, author=author), 400
        db = get_db()
        db.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
        db.commit()
        flash(f"Added '{title}'.")
        return redirect(url_for("index"))
    return render_template("add.html", title="", author="")


@app.route("/issue/<int:book_id>", methods=["POST"])
def issue_book(book_id):
    borrower = request.form.get("borrower", "").strip()
    if not borrower:
        flash("Borrower name is required to issue a book.")
        return redirect(url_for("index"))
    db = get_db()
    cur = db.execute(
        "UPDATE books SET available = 0, borrower = ? WHERE id = ? AND available = 1",
        (borrower, book_id),
    )
    db.commit()
    flash("Book issued." if cur.rowcount else "Book is not available.")
    return redirect(url_for("index"))


@app.route("/return/<int:book_id>", methods=["POST"])
def return_book(book_id):
    db = get_db()
    cur = db.execute(
        "UPDATE books SET available = 1, borrower = NULL WHERE id = ? AND available = 0",
        (book_id,),
    )
    db.commit()
    flash("Book returned." if cur.rowcount else "Book was not issued.")
    return redirect(url_for("index"))


@app.route("/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    db = get_db()
    db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    db.commit()
    flash("Book deleted.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
